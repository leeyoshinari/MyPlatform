#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from shell.models import Servers
from .common.parseJmx import read_jmeter_from_byte
from .common.generateJmx import *
from common.Result import result
from common.generator import primaryKey
from .common.fileController import upload_file_by_path, download_file_to_path, zip_file
import common.Request as Request
# Create your views here.


header_type = {'GET': 1, 'POST': 2}
jmeter_header = '<?xml version="1.0" encoding="UTF-8"?>'
logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 20
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word:
                total_page = TestPlan.objects.filter(name__contains=key_word).count()
                plans = TestPlan.objects.filter(name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = TestPlan.objects.all().count()
                plans = TestPlan.objects.all().order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get test plan success, operator: {username}')
            return render(request, 'performance/plan/home.html', context={'plans': plans, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get test plan failure ~')

def add(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            name = request.POST.get('name')
            teardown = request.POST.get('teardown')
            serialize = request.POST.get('serialize')
            run_type = request.POST.get('run_type')
            schedule = request.POST.get('schedule')
            server_num = request.POST.get('server_num')
            # init_number = request.POST.get('init_number')
            target_number = request.POST.get('target_number')
            duration = request.POST.get('duration')
            time_setting = request.POST.get('time_setting') if schedule == '1' else None
            comment = request.POST.get('comment')
            plans = TestPlan.objects.create(id=primaryKey(), name=name, tearDown=teardown, serialize=serialize, is_valid='true',
                            type=run_type, schedule=schedule, server_num=server_num, target_num=target_number,time_setting=time_setting,
                            duration=duration, comment=comment, operator=username)
            logger.info(f'Test plan {name} is save success, id is {plans.id}, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        return render(request, 'performance/plan/add.html')


def edit(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            plan_id = request.POST.get('plan_id')
            name = request.POST.get('name')
            teardown = request.POST.get('teardown')
            serialize = request.POST.get('serialize')
            run_type = request.POST.get('run_type')
            schedule = request.POST.get('schedule')
            server_num = request.POST.get('server_num')
            # init_number = request.POST.get('init_number')
            target_number = request.POST.get('target_number')
            duration = request.POST.get('duration')
            time_setting = request.POST.get('time_setting') if schedule == '1' else None
            comment = request.POST.get('comment')
            plan = TestPlan.objects.get(id=plan_id)
            plan.name = name
            plan.tearDown = teardown
            plan.serialize = serialize
            plan.type = run_type
            plan.schedule = schedule
            plan.server_num = server_num
            # plan.init_num = init_number
            plan.target_num = target_number
            plan.duration = duration
            plan.time_setting = time_setting
            plan.comment = comment
            plan.operator = username
            plan.save()
            logger.info(f'Test plan {plan_id} is edited success, operator: {username}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Edit failure ~')
    else:
        try:
            plan_id = request.GET.get('id')
            plans = TestPlan.objects.get(id=plan_id)
            return render(request, 'performance/plan/edit.html', context={'plan': plans})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get test plan failure ~')

def edit_variable(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            variables = data.get('variables')
            plans = TestPlan.objects.get(id=plan_id)
            plans.variables = variables
            plans.save()
            logger.info(f'Test Plan {plan_id} variable save success, operator: {username}')
            return result(msg='Save variables success ~')
        except:
            logger.error(traceback.format_exc())
            return result(msg='Save variables failure ~')
    else:
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            variables = TestPlan.objects.get(id=plan_id)
            logger.info(f'Get test plan variables success, operator: {username}')
            return render(request, 'performance/plan/variable.html', context={'variables': variables})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get variables failure ~')


def upload_file(request):
    if request.method == 'POST':
        username = request.user.username
        form = request.FILES['file']
        file_name = form.name
        file_byte = form.file.read()
        try:
            res = read_jmeter_from_byte(file_byte)
            parse_jmx_to_database(res, username)
            logger.info(f'{file_name} Import Success, operator: {username}')
            return result(msg=f'{file_name} Import Success ~', data=file_name)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'{file_name} Import Failure ~', data=file_name)


def parse_jmx_to_database(res, username):
    try:
        for plan in res:
            testPlan = TestPlan.objects.create(id=primaryKey(), name=plan.get('testname'), comment=plan.get('comments'),
                                    tearDown=plan.get('tearDown_on_shutdown'), serialize=plan.get('serialize_threadgroups'),
                                    variables=plan['arguments'], is_valid=plan.get('enabled'), operator=username)
            for tg in plan['thread_group']:
                thread = ThreadGroup.objects.create(id=primaryKey(), plan_id=testPlan.id, name=tg.get('testname'),
                                    is_valid=tg.get('enabled'), ramp_time=tg.get('ramp_time'),
                                    duration=tg.get('duration'), comment=tg.get('comments'), operator=username)
                for ctl in tg['controller']:
                    controller = TransactionController.objects.create(id=primaryKey(), thread_group_id=thread.id,
                                    name=ctl.get('testname'), is_valid=ctl.get('enabled'), comment=ctl.get('comments'),
                                    operator=username)
                    for sample in ctl['http_sample']:
                        http = HTTPSampleProxy.objects.create(id=primaryKey(), controller_id=controller.id, name=sample.get('testname'),
                                    is_valid=sample.get('enabled'), comment=sample.get('sample_dict').get('comments'),
                                    domain=sample.get('sample_dict').get('domain'), port=sample.get('sample_dict').get('port'),
                                    protocol=sample.get('sample_dict').get('protocol'), path=sample.get('sample_dict').get('path'),
                                    method=sample.get('sample_dict').get('method'), contentEncoding=sample.get('sample_dict').get('contentEncoding'),
                                    argument=sample.get('arguments'), http_header_id=header_type.get(sample.get('sample_dict').get('method')),
                                    assert_type=sample.get('assertion').get('test_type'), assert_content=sample.get('assertion').get('test_string'),
                                    extractor=sample.get('extractor'), operator=username)
    except:
        raise


def copy_plan(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            plans = TestPlan.objects.get(id=plan_id)
            keyWord = plans.name
            plans.id = primaryKey()
            plans.name = plans.name + ' - Copy'
            plans.operator = username
            plans.save()
            thread_groups = ThreadGroup.objects.filter(plan_id=plan_id)
            for thread_group in thread_groups:
                res = Request.get(request.headers.get('Host'), f'{resolve_url("perf:group_copy")}?plan_id={plans.id}&id={thread_group.id}', cookies=request.headers.get('cookie'))
                logger.info(res)
            logger.info(f'Copy plan {plan_id} success, target plan is {plans.id}, operator: {username}')
            return redirect(resolve_url('perf:plan_home') + '?keyWord=' + keyWord)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy Plan Failure ~')


def add_to_task(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            # plans = TestPlan.objects.get(id=plan_id)
            task = PerformanceTestTask.objects.filter(plan_id=plan_id, status__lte=1)
            if not task:
                task = PerformanceTestTask.objects.create(id=primaryKey(), plan_id=plan_id, ratio=1, status=0,
                                                        operator=username)
                logger.info(f'Create task {task.id} success, operator: {username}')
            return result(msg='Add task success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Add task Failure ~')


def task_home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            plans = TestPlan.objects.get(id=plan_id)
            tasks = PerformanceTestTask.objects.filter(plan_id=plan_id).order_by('-update_time')
            logger.info(f'Get task success, operator: {username}')
            return render(request, 'performance/plan/task.html', context={'plans': plans, 'tasks': tasks})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get task Failure ~')


def start_task(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            task_id = request.POST.get('task_id')
            plan_id = request.POST.get('plan_id')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            plans = TestPlan.objects.get(id=plan_id)
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
                        zip_file_path = os.path.join(settings.TEMP_PATH, task_id, task_id + '.zip')
                        zip_file(test_jmeter_path, zip_file_path)
                        if settings.FILE_STORE_TYPE == '0':
                            zip_file_url = f'temp/{task_id}/{task_id}.zip'
                        else:
                            zip_file_url = upload_file_by_path(zip_file_path)
                        logger.info(f'zip file is written successfully, operator: {username}')
                        tasks.path = f'{settings.FILE_URL}/{zip_file_url}'
                    else:
                        logger.error('The Thread Group has no Controllers ~')
                        return result(code=1, msg='The Thread Group has no Controllers, Please add Controller ~')
                else:
                    logger.error('The Test Plan can only have one enable Thread Group ~')
                    return result(code=1, msg='The Test Plan can only have one enable Thread Group, Please check it ~')
            else:
                logger.error('The Test Plan has been disabled ~')
                return result(code=1, msg='The Test Plan has been disabled ~')

            tasks.status = 1
            tasks.number_samples = number_of_samples
            tasks.save()
            logger.info(f'Task {task_id} start success, operator: {username}')
            return result(msg=f'Start success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Start failure ~')


def stop_task(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            task_id = request.GET.get('id')
            tasks = PerformanceTestTask.objects.get(id=task_id)
            tasks.status = 3
            tasks.save()
            logger.info(f'Task {task_id} stop success, operator: {username}')
            return result(msg=f'Stop success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Stop failure ~')

def get_server(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            groups = request.user.groups.all()
            servers = Servers.objects.filter(is_perf__gt=0, group__in=groups).order_by('-id')
            logger.info(f'Get pressure server info success, operator: {username}')
            return render(request, 'performance/plan/server.html', context={'servers': servers})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get server info Error ~')