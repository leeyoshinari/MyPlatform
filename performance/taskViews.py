#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import time
import logging
import traceback
from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from django.http import StreamingHttpResponse
from .models import TestPlan, ThreadGroup, TransactionController, TestTaskLogs
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from shell.models import Servers
from .common.generateJmx import *
from .common.getRedis import *
from .common.request import http_request
from common.Result import result, json_result
from common.generator import primaryKey, strfTime, strfDeltaTime, toTimeStamp
from .common.fileController import *
import influxdb
# Create your views here.


jmeter_header = '<?xml version="1.0" encoding="UTF-8"?>'
logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            if plan_id:
                total_page = PerformanceTestTask.objects.filter(plan_id=plan_id).count()
                tasks = PerformanceTestTask.objects.filter(plan_id=plan_id).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = PerformanceTestTask.objects.all().count()
                tasks = PerformanceTestTask.objects.all().order_by('-create_time')[page_size * (page - 1): page_size * page]
            logger.info(f'Get task success, operator: {username}')
            return render(request, 'performance/task/home.html', context={'tasks': tasks, 'page': page, 'page_size': page_size,
                          'total_page': (total_page + page_size - 1) // page_size})
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
            plan_id = request.POST.get('plan_id')
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
                            zip_file_url = upload_file_by_path(settings.FILE_STORE_TYPE, zip_file_path)
                        logger.info(f'zip file is written successfully, operator: {username}, zip file: {zip_file_url}')
                        task_path = f'{settings.FILE_URL}{zip_file_url}'
                        del_file = delete_local_file(test_jmeter_path)
                        if del_file['code'] == 1:
                            logger.error(del_file['msg'])
                    else:
                        logger.error(f'The Thread Group has no or many Controllers, current controller No is {len(controllers)} ~')
                        if len(controllers) < 1:
                            msg = 'The Thread Group has no Controllers, Please add Controller ~'
                        else:
                            msg = 'The Thread Group has too many Controllers, Please disabled Controller ~'
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
            test_jmeter_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
            if os.path.exists(test_jmeter_path):
                _ = delete_local_file(test_jmeter_path)
            temp_file_path = os.path.join(settings.TEMP_PATH, task_id)
            if os.path.exists(temp_file_path):
                _ = delete_local_file(temp_file_path)
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
                'numberSamples': tasks.number_samples,
                'filePath': tasks.path,
                'isDebug': tasks.plan.is_debug
            }
            if host:
                host_info = get_value_by_host('jmeterServer_'+host)
                if host_info and host_info['status'] == 0:
                    res = http_request('post', host, host_info['port'], 'runTask', json=post_data)
                    response_data = json.loads(res.content.decode())
                    if response_data['code'] == 0:
                        logger.info(f'Task {task_id} is starting, host: {host}, operator: {username}')
                        return result(msg=f'Task {task_id} is starting, please wait a minute ~ ~')
                    else:
                        logger.error(f'Task {task_id} run task failure, host: {host}, operator: {username}')
                        return result(code=1, msg=response_data['msg'])
                else:
                    logger.error(f'Agent {host} is not registered or busy ~')
                    return result(code=1, msg=f'Host {host} is not registered or busy ~')
            else:
                registered_servers = get_all_host()
                idle_servers = [s['host'] for s in registered_servers if s['status'] == 0]
                available_servers = Servers.objects.values('host').filter(room_id=tasks.server_room_id, host__in=idle_servers)
                logger.debug(available_servers.query)
                if len(available_servers) < tasks.plan.server_number:
                    logger.warning(f'There is not enough servers to run performance test, operator: {username}')
                    return result(code=1, msg='There is not enough servers to run performance test ~')
                for h in available_servers:
                    res = http_request('post', h['host'], get_value_by_host('jmeterServer_' + h['host'], 'port'), 'runTask', json=post_data)
                    # response_data = json.loads(res.content.decode())
                logger.info(f'Task {task_id} is starting, operator: {username}')
                return result(msg=f'Task {task_id} is starting, please wait a minute ~', data=task_id)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'Task {task_id} started failure ~')


def stop_task(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            host = request.GET.get('host')
            host = host if host else 'all'
            if host == 'all':
                runnging_server = TestTaskLogs.objects.filter(task_id=task_id, action=1).values('value')
                hosts = [h['value'] for h in runnging_server]
            else:
                host_info = TestTaskLogs.objects.get(task_id=task_id, value=host)
                hosts = [host]
            for h in hosts:
                res = http_request('get', h, get_value_by_host('jmeterServer_'+h, 'port'), 'stopTask/'+task_id)
                # response_data = json.loads(res.content.decode())
            logger.info(f'Task {task_id} is stopping, operator: {username}')
            return result(msg=f'Task {task_id} is stopping, please wait a minute ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'Task {task_id} Stop failure ~')


def get_running_status(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            code = 0
            msg = ''
            start_time = time.time()
            while True:
                time.sleep(2)
                tasks = PerformanceTestTask.objects.get(id=task_id)
                if tasks.status == 1:
                    code = 0
                    msg = f'Task {task_id} start success ~'
                    break
                if time.time() - start_time > 60:
                    code = 2
                    msg = f'Task {task_id} is starting, please wait a minute ~'
                    break
            logger.info(f'{msg}, operator: {username}')
            return result(code=code, msg=msg, data=tasks.status)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Query task status failure ~')


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
            url = f"http://{host}:{get_value_by_host('jmeterServer_'+host, 'port')}/download/{task_id}"
            response = StreamingHttpResponse(get_request(url))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="{task_id}-log.zip"'
            logger.info(f'{task_id}-log.zip download successful, operator: {username}')
            return response
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
            try:
                tps = float(tps)
            except ValueError:
                logger.error(traceback.format_exc())
                return result(code=1, msg='TPS is not a number ~')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            if host == 'all':
                running_server = TestTaskLogs.objects.filter(task_id=task_id, action=1).values('value')
                hosts = [h['value'] for h in running_server]
            else:
                host_info = TestTaskLogs.objects.get(task_id=task_id, value=host)
                hosts = [host]
            current_tps = int(tasks.plan.target_num * tasks.number_samples * tps * 0.6/ len(hosts))
            post_data = {'taskId': task_id, 'tps': current_tps}
            logger.debug(f"Change TPS hosts: {hosts}")
            res_host = []
            for h in hosts:
                res = http_request('post', h, get_value_by_host('jmeterServer_'+h, 'port'), 'change', json=post_data)
                response_data = json.loads(res.content.decode())
                logger.debug(response_data)
                if response_data['code'] != 0:
                    res_host.append(h)
                    logger.error(f'Change TPS failure, task: {task_id}, host: {h}, operator: {username}')

            if res_host:
                return result(code=1, msg=f'{",".join(res_host)} change TPS failure ~')
            logger.info(f'Change TPS success, task: {task_id}, current tps is {current_tps}, operator: {username}')
            return result(msg='Change TPS success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Change TPS failure ~')


def set_message(request):
    if request.method == 'POST':
        try:
            datas = json.loads(request.body.decode())
            task_id = datas.get('taskId')
            host = datas.get('host')
            task_type = datas.get('type')
            # data = datas.get('data')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            if task_type == 'run_task':
                tasks.running_num = tasks.running_num + 1
                tasks.status = 1
                tasks.start_time = strfTime()
                try:
                    task_log = TestTaskLogs.objects.get(task_id=task_id, value=host)
                    task_log.action = 1
                    task_log.save()
                except TestTaskLogs.DoesNotExist:
                    TestTaskLogs.objects.create(id=primaryKey(), task_id=task_id, action=1, value=host, operator='System')

            if task_type == 'stop_task':
                tasks.running_num = tasks.running_num - 1
                task_log = TestTaskLogs.objects.get(task_id=task_id, value=host)
                task_log.action = 2
                task_log.save()
                if tasks.running_num == 0 and TestTaskLogs.objects.filter(task_id=task_id, action=1).count() == 0:
                    tasks.status = 2
                    tasks.end_time = strfTime()
                    durations = time.time() - toTimeStamp(str(tasks.start_time))
                    datas = get_data_from_influx('1', task_id, host='all', start_time=tasks.start_time, end_time=tasks.end_time)
                    logger.info(f"Task {task_id} stop success ~")
                    if datas['code'] == 0:
                        total_samples = sum(datas['data']['samples'])
                        avg_rt = [s * t / total_samples for s, t in zip(datas['data']['samples'], datas['data']['avg_rt'])]
                        tasks.samples = total_samples
                        tasks.tps = round(total_samples / durations, 2)
                        tasks.average_rt = round(sum(avg_rt), 2)
                        tasks.min_rt = min(datas['data']['min_rt'])
                        tasks.max_rt = max(datas['data']['max_rt'])
                        tasks.error = round(sum(datas['data']['err']) / total_samples * 100, 4)
                    else:
                        logger.error(datas['message'])
            tasks.save()
            logger.info(f'Set message success, type:{task_type}, task ID: {task_id}')
            return result(msg='Set message success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Set message failure ~')


def view_task_detail(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            if tasks.start_time:
                logger.info(f'query task {task_id} detail page success, operator: {username}')
                return render(request, 'performance/task/detail.html', context={'tasks': tasks})
            else:
                return render(request, 'performance/task/detail.html', context={'tasks': None})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get task detail error ~')


def get_running_server(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            hosts = TestTaskLogs.objects.values('value', 'action').filter(task_id=task_id, action=1)
            host_info = []
            for h in hosts:
                jmeter_server_dict = get_value_by_host('jmeterServer_' + h['value'])
                server_monitor_dict = get_value_by_host('Server_' + h['value'])
                host_dict = jmeter_server_dict if jmeter_server_dict else {}
                if server_monitor_dict:
                    host_dict.update(server_monitor_dict)
                host_dict.update({'action': h['action']})
                host_info.append(host_dict)
            logger.info(f'Query running servers success, operator: {username}')
            return result(msg='Get running servers success ~', data=host_info)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get running servers failure ~')


def get_idle_server(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            server_room_id = request.GET.get('id')
            servers = Servers.objects.values('host').filter(Q(room_id=server_room_id), Q(room__type=2))
            host_info = []
            for server in servers:
                host_dict = get_value_by_host('jmeterServer_' + server['host'])
                host_dict = host_dict if host_dict else {}
                if host_dict.get('status') == 0:
                    host_dict.update(get_value_by_host('Server_' + server['host']))
                    host_info.append(host_dict)
            logger.info(f'Query idle servers success, operator: {username}')
            return result(msg='Get idle servers success ~', data=host_info)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get idle servers failure ~')


def query_data(request):
    if request.method == 'GET':
        try:
            task_id = request.GET.get('id')
            host = request.GET.get('host')
            delta = request.GET.get('delta')
            start_time = request.GET.get('startTime')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            start_time = start_time if start_time else tasks.start_time
            end_time = tasks.end_time
            return json_result(get_data_from_influx(delta, task_id, host=host, start_time=start_time, end_time=end_time))
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Query data error ~')


def get_data_from_influx(delta, task_id, host='all', start_time=None, end_time=None):
    query_data = {'time': [], 'c_time': [], 'samples': [], 'tps': [], 'avg_rt': [], 'min_rt': [], 'max_rt': [], 'err': [], 'active': []}
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

        if delta == '520':
            sql = f"select c_time, samples, tps, avg_rt, min_rt, max_rt, err, active from performance_jmeter_task where task='{task_id}' and " \
                  f"host='{host}' and time>'{start_time}'"
        else:
            sql = f"select c_time, samples, tps, avg_rt, min_rt, max_rt, err, active from performance_jmeter_task where task='{task_id}' and " \
                  f"host='{host}' and time>'{start_time}' and time<='{end_time}' tz('Asia/Shanghai')"

        logger.info(f'Execute SQL: {sql}')
        datas = conn.query(sql)
        if datas:
            for data in datas.get_points():
                if data['time'] == start_time: continue
                query_data['time'].append(data['time'])
                query_data['c_time'].append(data['c_time'])
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
        res['data'] = query_data
    return res