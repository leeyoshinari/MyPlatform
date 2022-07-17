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
from common.Result import result
from common.generator import primaryKey, strfTime
from .common.fileController import upload_file_by_path, download_file_to_path, zip_file, download_file_to_bytes
import common.Request as Request
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
                                'db': settings.REDIS_DB}})


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
                    num_threads = 200 if plans.type == 1 else plans.init_num
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
                        logger.info(f'zip file is written successfully, operator: {username}')
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
                                                       path=task_path, server_num=plans.server_num, operator=username)
            logger.info(f'Task {tasks.id} generate success, operator: {username}')
            return result(msg=f'Start success ~')
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
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            all_servers = get_all_host()
            idle_servers = [s for s in all_servers if s['status'] == 0]
            server_num = tasks.plan.server_num
            if server_num > len(idle_servers):
                logger.warning(f'There is not enough servers to run performance test, operator: {username}')
                return result(code=1, msg='There is not enough servers to run performance test ~')
            all_servers = idle_servers[0: server_num]
            hosts = []
            post_data = {
                'taskId': task_id,
                'planId': tasks.plan.id,
                'agentNum': server_num,
                'filePath': tasks.path,
            }
            for h in all_servers:
                res = http_request('post', h['host'], h['port'], 'runTask', json=post_data)
                response_data = json.loads(res.content.decode())
                if response_data['code'] == 0:
                    hosts.append(h['host'])

            if not hosts:
                logger.error(f'{server_num - len(hosts)} agent run task failure, operator: {username}')
                return result(code=1, msg=f'{server_num - len(hosts)} agent run task failure ~')
            tasks.servers = ','.join(hosts)
            tasks.status = 1
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
            tasks = PerformanceTestTask.objects.get(id=task_id)
            hosts = tasks.servers.split(',')
            stop_host = []
            for h in hosts:
                res = http_request('get', h, get_value_by_host('jmeterServer_'+h, 'port'), 'stopTask/'+task_id)
                response_data = json.loads(res.content.decode())
                if response_data['code'] != 0:
                    stop_host.append(h)
            if stop_host:
                tasks.servers = ','.join(stop_host)
                tasks.save()
                logger.error(f'{len(stop_host)} agent stop failure, operator: {username}')
                return result(code=1, msg=f'{len(stop_host)} agent stop failure ~')
            else:
                tasks.status = 3
                tasks.end_time = strfTime()
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


def change_tps(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            task_id = request.POST.get('taskId')
            tps = request.POST.get('TPS')
            tasks = PerformanceTestTask.objects.get(id=task_id)
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
            status = datas.get('status')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            tasks.status = status
            tasks.save()
            logger.info(f'Set task {task_id} status to {status}')
            return result(msg='Set task status success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Set task status failure ~')

