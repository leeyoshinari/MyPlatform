#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from django.http import StreamingHttpResponse
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from .common.generateJmx import *
from .common.getRedis import *
from .common.request import http_request
from common.Result import result, json_result
from common.generator import primaryKey, strfTime, strfDeltaTime, toTimeStamp
from .common.fileController import upload_file_by_path, download_file_to_path, zip_file, download_file_to_bytes
import common.Request as Request
import influxdb
# Create your views here.


jmeter_header = '<?xml version="1.0" encoding="UTF-8"?>'
logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            if plan_id:
                plans = TestPlan.objects.get(id=plan_id)
                tasks = PerformanceTestTask.objects.filter(plan_id=plan_id).order_by('-create_time')
                context = {'plans': plans, 'tasks': tasks}
            else:
                tasks = PerformanceTestTask.objects.all().order_by('-create_time')
                context = {'tasks': tasks}
            logger.info(f'Get task success, operator: {username}')
            return render(request, 'performance/task/home.html', context=context)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get task Failure ~')


def register(request):
    if request.method == 'POST':
        value = request.body.decode()
        host = json.loads(value).get('host')
        settings.REDIS.set(f'jmeterServer_{host}', value, ex=settings.HEARTBEAT)
        logger.info(f'Agent: {host} registers successfully ~')
        return result(msg='Agent registers successfully ~',data={'influx': {'host': settings.INFLUX_HOST, 'port': settings.INFLUX_PORT,
                      'username': settings.INFLUX_USER_NAME, 'password': settings.INFLUX_PASSWORD, 'database': settings.INFLUX_DATABASE},
                      'redis': {'host': settings.REDIS_HOST, 'port': settings.REDIS_PORT, 'password': settings.REDIS_PWD,
                       'db': settings.REDIS_DB}, 'key_expire': settings.PERFORMANCE_EXPIRE})


def add_to_task(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            # task_id = request.POST.get('task_id')
            plan_id = request.POST.get('plan_id')
            # tasks = PerformanceTestTask.objects.get(id=task_id)
            plans = TestPlan.objects.get(id=plan_id)
            task_id = str(primaryKey())

            if plans.is_valid == 'true':
                test_plan, duration = generate_test_plan(plans)
                logger.info(f'Write Test Plan success, operator: {username}')

                thread_groups = ThreadGroup.objects.filter(plan_id=plans.id, is_valid='true')
                if len(thread_groups) == 1:
                    num_threads = 200 if plans.type == 1 else plans.target_num
                    thread_group = generate_thread_group(thread_groups[0], num_threads, duration)
                    cookie_manager = generate_cookie(thread_groups[0].cookie)
                    csv_data_set = generator_csv(thread_groups[0].file)
                    logger.info(f'Write Thread Group success, , operator: {username}')
                    controllers = TransactionController.objects.filter(thread_group_id=thread_groups[0].id, is_valid='true').order_by('id')
                    if len(controllers) == 1:
                        http_controller = ''
                        http_samples_proxy = ''
                        samples = HTTPSampleProxy.objects.filter(controller_id=controllers[0].id, is_valid='true').order_by('id')
                        number_of_samples = len(samples)
                        throughput = generator_throughput(number_of_samples)
                        if len(samples) > 0:
                            for sample in samples:
                                if sample.assert_content:
                                    headers = HTTPRequestHeader.objects.get(id=sample.http_header_id)
                                    http_samples_proxy += generator_samples_and_header(sample, headers)
                                else:
                                    logger.error(f'HTTP Sample {sample.name} has no assertion ~')
                                    return result(code=1, msg=f'HTTP Sample {sample.name} has no assertion ~')
                            http_controller += generator_controller(controllers[0]) + '<hashTree>' + http_samples_proxy + '</hashTree>'
                        else:
                            logger.error('The Controller has no HTTP Samples ~')
                            return result(code=1, msg='The Controller has no HTTP Samples, Please add HTTP Samples ~')

                        all_threads = thread_group + '<hashTree>' + throughput + cookie_manager + csv_data_set + http_controller + '</hashTree>'
                        test_plan = test_plan + '<hashTree>' + all_threads + '</hashTree>'
                        jmeter_test_plan = jmeter_header + '<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.4.3"><hashTree>' + test_plan + '</hashTree></jmeterTestPlan>'

                        # write file to local
                        test_jmeter_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
                        if not os.path.exists(test_jmeter_path):
                            os.mkdir(test_jmeter_path)
                        # write jmeter file to path
                        jmeter_file_path = os.path.join(test_jmeter_path, 'test.jmx')
                        with open(jmeter_file_path, 'w', encoding='utf-8') as f:
                            f.write(jmeter_test_plan)
                        # write csv file to path
                        if thread_groups[0].file:
                            csv_file_path_url = thread_groups[0].file['file_path']
                            csv_file_path = os.path.join(test_jmeter_path, csv_file_path_url.split('/')[-1])
                            download_file_to_path(csv_file_path_url, csv_file_path)
                        logger.info(f'jmx file and csv file are written successfully, operator: {username}')
                        # write zip file to temp path
                        temp_file_path = os.path.join(settings.TEMP_PATH, task_id)
                        if not os.path.exists(temp_file_path):
                            os.mkdir(temp_file_path)
                        zip_file_path = os.path.join(temp_file_path, task_id + '.zip')
                        zip_file(test_jmeter_path, zip_file_path)
                        # upload file
                        if settings.FILE_STORE_TYPE == '0':
                            zip_file_url = f'{settings.STATIC_URL}temp/{task_id}/{task_id}.zip'
                        else:
                            zip_file_url = upload_file_by_path(zip_file_path)
                        logger.info(f'zip file is written successfully, operator: {username}, zip file: {zip_file_url}')
                        task_path = f'{settings.FILE_URL}{zip_file_url}'
                    else:
                        logger.error(f'The Thread Group has no or many Controllers, current controller No is {len(controllers)} ~')
                        if len(controllers) < 1:
                            msg = 'The Thread Group has no Controllers, Please add Controller ~'
                        else:
                            msg = 'The Thread Group has too much Controllers, Please disabled Controller ~'
                        return result(code=1, msg=msg)
                else:
                    logger.error('The Test Plan can only have one enable Thread Group ~')
                    return result(code=1, msg='The Test Plan can only have one enable Thread Group, Please check it ~')
            else:
                logger.error('The Test Plan has been disabled ~')
                return result(code=1, msg='The Test Plan has been disabled ~')

            tasks = PerformanceTestTask.objects.create(id=task_id, plan_id=plan_id, ratio=1, status=0, number_samples=number_of_samples,
                                                       server_room_id=plans.server_room_id, path=task_path, operator=username)
            logger.info(f'Task {tasks.id} generate success, operator: {username}')
            return result(msg=f'Start success ~', data=task_id)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Start failure ~')


def delete_task(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            task = PerformanceTestTask.objects.get(id=task_id).delete()
            logger.info(f'Delete task {task.id} success, operator: {username}')
            return result(msg='Delete task success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete task Failure ~')


def start_task(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            task_id = request.POST.get('task_id')
            host = request.POST.get('host')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            post_data = {
                'taskId': task_id,
                'planId': tasks.plan.id,
                'agentNum': 1,
                'filePath': tasks.path,
                'isDebug': True
            }
            if host:
                host_info = get_value_by_host('jmeterServer_'+host)
                if host_info:
                    res = http_request('post', host, host_info['port'], 'runTask', json=post_data)
                    response_data = json.loads(res.content.decode())
                    if response_data['code'] == 0:
                        tasks.servers = tasks.servers + ',' + host
                        tasks.status = 0
                        tasks.save()
                        logger.info(f'Task {task_id} run task success, host: {host}, operator: {username}')
                        return result(msg='Agent run task success ~')
                    else:
                        logger.error(f'Task {task_id} run task failure, host: {host}, operator: {username}')
                        return result(code=1, msg='Agent run task failure ~')
                else:
                    logger.error(f'Agent {host} is not registered ~')
                    return result(code=1, msg='Agent is not registered ~')
            else:
                all_servers = get_all_host()
                idle_servers = [s for s in all_servers if s['status'] == 0]
                if len(idle_servers) > 0:
                    logger.warning(f'There is not enough servers to run performance test, operator: {username}')
                    return result(code=1, msg='There is not enough servers to run performance test ~')
                all_servers = idle_servers[0]
                hosts = []
                for h in all_servers:
                    res = http_request('post', h['host'], h['port'], 'runTask', json=post_data)
                    response_data = json.loads(res.content.decode())
                    if response_data['code'] == 0:
                        hosts.append(h['host'])

                if not hosts:
                    logger.error(f'{all_servers} agent run task failure, operator: {username}')
                    return result(code=1, msg=f'{all_servers} agent run task failure ~')
                tasks.servers = ','.join(hosts)
                tasks.status = 0
                tasks.running_num = 0
                tasks.stopping_num = 0
                tasks.start_time = strfTime()
                tasks.save()
                logger.info(f'Task {task_id} run task success, operator: {username}')
                return result(msg=f'{len(hosts)} agent run task success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Run task failure ~')


def stop_task(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            host = request.GET.get('host')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            if host:
                hosts = [host]
            else:
                hosts = tasks.servers.split(',')
            stop_host = []
            for h in hosts:
                res = http_request('get', h, get_value_by_host('jmeterServer_'+h, 'port'), 'stopTask/'+task_id)
                response_data = json.loads(res.content.decode())
                if response_data['code'] == 0:
                    stop_host.append(h)
            # if stop_host:
            #     tasks.servers = ','.join(stop_host)
            #     tasks.save()
            #     logger.error(f'{len(stop_host)} agent stop failure, operator: {username}')
            #     return result(code=1, msg=f'{len(stop_host)} agent stop failure ~')
            # else:
            tasks.status = 1
            tasks.running_num = 0
            tasks.stopping_num = 0
            # tasks.end_time = strfTime()
            # tasks.samples =
            # tasks.tps =
            # tasks.average_rt =
            # tasks.error =
            tasks.save()
            logger.info(f'Task {task_id} stop success, operator: {username}')
            return result(msg=f'Stop success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Stop failure ~')


def download_file(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            task = PerformanceTestTask.objects.values('path').get(id=task_id)
            response = StreamingHttpResponse(download_file_to_bytes(task.path))
            response['Content-Type'] = 'application/zip'
            response['Content-Disposition'] = f'attachment;filename="{task_id}.zip"'
            logger.info(f'{task_id}.zip download successful, operator: {username}')
            return response
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='test plan file download failure.')


def download_log(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            host = request.GET.get('host')
            logger.info(f'{task_id}.zip download successful, operator: {username}')
            return http_request('get', host, get_value_by_host('jmeterServer_'+host, 'port'), f'download/{task_id}')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='log file download failure.')


def change_tps(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            task_id = request.POST.get('taskId')
            tps = request.POST.get('TPS')
            host = request.POST.get('host')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            if host:
                post_data = {'taskId': task_id, 'tps': int(tasks.plan.target_num * tps)}
                res = http_request('post', host, get_value_by_host('jmeterServer_' + host, 'port'), 'change', json=post_data)
                response_data = json.loads(res.content.decode())
                if response_data['code'] != 0:
                    logger.error(f'Change TPS failure, host: {host}, operator: {username}')
                    return result(code=1, msg='Change TPS failure ~')
                logger.info(f'Change TPS success, {host}: current tps is {tasks.plan.target_num * tps}, operator: {username}')
            else:
                hosts = tasks.servers.split(',')
                current_tps = int(tasks.plan.target_num * tps / len(hosts))
                post_data = {'taskId': task_id, 'tps': current_tps}
                for h in hosts:
                    res = http_request('post', h, get_value_by_host('jmeterServer_'+h, 'port'), 'change', json=post_data)
                    response_data = json.loads(res.content.decode())
                    if response_data['code'] != 0:
                        logger.error(f'Change TPS failure, host: {h}, operator: {username}')
                        return result(code=1, msg='Change TPS failure ~')
                logger.info(f'Change TPS success, current tps is {current_tps}, operator: {username}')
            return result(msg='Change TPS success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Change TPS failure ~')


def set_message(request):
    if request.method == 'POST':
        try:
            datas = json.loads(request.body.decode())
            task_id = datas.get('taskId')
            task_type = datas.get('type')
            data = datas.get('data')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            if task_type == 'run_task':
                if data == 1:
                    tasks.running_num = tasks.running_num + 1
                    tasks.status = 1
                    tasks.start_time = strfTime()
                else:
                    tasks.stopping_num = tasks.stopping_num + 1

            if task_type == 'stop_task':
                if data == 0:
                    tasks.running_num = tasks.running_num + 1
                else:
                    tasks.stopping_num = tasks.stopping_num + 1
                if tasks.running_num == 0:
                    tasks.status = 2
                    tasks.end_time = strfTime()
                    durations = time.time() - toTimeStamp(tasks.start_time)
                    datas = get_data_from_influx(task_id, host=None, start_time=tasks.start_time, end_time=strfTime())
                    if datas['code'] == 0:
                        total_samples = sum(datas['data']['samples'])
                        avg_rt = [s * t / total_samples for s, t in zip(datas['data']['samples'], datas['data']['avg_rt'])]
                        tasks.samples = total_samples
                        tasks.tps = round(total_samples / durations, 2)
                        tasks.average_rt = round(sum(avg_rt), 2)
                        tasks.min_rt = min(datas['data']['min_rt'])
                        tasks.max_rt = max(datas['data']['max_rt'])
                        tasks.error = round(sum(datas['data']['err']) / total_samples * 100, 4)
            tasks.save()
            logger.info(f'Set message success, type:{task_type}, task ID: {task_id}, data is {data}')
            return result(msg='Set message success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Set message failure ~')


def view_task_detail(request):
    if request.method == 'GET':
        try:
            task_id = request.GET.get('id')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            return render(request, 'performance/task/detail.html', context={'tasks': tasks})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get task detail error ~')


def query_data(request):
    if request.method == 'POST':
        try:
            task_id = request.POST.get('id')
            host = request.POST.get('host')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            start_time = tasks.start_time
            end_time = strfTime()
            if tasks.end_time:
                end_time = tasks.end_time
            return json_result(get_data_from_influx(task_id, host=host, start_time=start_time, end_time=end_time))
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Query data error ~')


def get_data_from_influx(task_id, host=None, start_time=None, end_time=None):
    query_data = {'time': [], 'samples': [], 'tps': [], 'avg_rt': [], 'min_rt': [], 'max_rt': [], 'err': [], 'active': []}
    res = {'code': 0, 'data': None, 'message': 'Query InfluxDB Successful!'}
    try:
        conn = influxdb.InfluxDBClient(settings.INFLUX_HOST, settings.INFLUX_PORT, settings.INFLUX_USER_NAME,
                                       settings.INFLUX_PASSWORD, settings.INFLUX_DATABASE)
        if start_time and end_time:     # If there is a start time and an end time
            pass
        elif start_time is None and end_time is None:  # If the start time and end time do not exist, use the default time.
            start_time = strfDeltaTime(1800)
            end_time = strfTime()
        else:   # If the end time does not exist, the current time is used
            end_time = strfTime()

        if host:
            sql = f'select samples, tps, avg_rt, min_rt, max_rt, err, active from "performance_jmeter_task" where task="{task_id}" and ' \
                  f'host="{host}" and time>"{start_time}" and time<"{end_time}" tz("Asia/Shanghai")'
        else:
            sql = f'select samples, tps, avg_rt, min_rt, max_rt, err, active from "performance_jmeter_task" where task="{task_id}" and ' \
                  f'time>"{start_time}" and time<"{end_time}" tz("Asia/Shanghai")'
        logger.info(f'Execute SQL: {sql}')
        datas = conn.query(sql)
        if datas:
            for data in datas.get_points():
                query_data['time'].append(data['time'][:19].replace('T', ' '))
                query_data['samples'].append(data['samples'])
                query_data['tps'].append(data['tps'])
                query_data['avg_rt'].append(data['avg_rt'])
                query_data['min_rt'].append(data['min_rt'])
                query_data['max_rt'].append(data['max_rt'])
                query_data['err'].append(data['err'])
                query_data['active'].append(data['active'])
        else:
            res['message'] = 'No data is found, please check or wait a minute.'
            res['code'] = 1
            logger.error('No data is found, please check or wait a minute.')
        res['data'] = query_data
        del conn, query_data
        logger.info('Query data success ~')
    except:
        logger.error(traceback.format_exc())
        res['message'] = 'System Error ~'
        res['code'] = 1
    return res
