#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from django.db.models import Count
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from shell.models import Servers, ServerRoom
from .common.parseJmx import read_jmeter_from_byte
from .common.generateJmx import *
from .common.getRedis import *
from common.Result import result
from common.generator import primaryKey
import common.Request as Request
# Create your views here.


header_type = {'GET': 1, 'POST': 2}
logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            server_num_rooms = {}
            username = request.user.username
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 20
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word:
                total_page = TestPlan.objects.filter(name__contains=key_word).count()
                plans = TestPlan.objects.filter(name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = TestPlan.objects.all().count()
                plans = TestPlan.objects.all().order_by('-create_time')[page_size * (page - 1): page_size * page]

            if plans:
                server_num_rooms = get_idle_server_num()
            logger.info(f'Get test plan success, operator: {username}')
            return render(request, 'performance/plan/home.html', context={'plans': plans, 'page': page, 'page_size': page_size, 'server_num_rooms': server_num_rooms,
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
            server_room = request.POST.get('server_room')
            server_num = request.POST.get('server_num')
            # init_number = request.POST.get('init_number')
            target_number = request.POST.get('target_number')
            duration = request.POST.get('duration')
            time_setting = request.POST.get('time_setting') if schedule == '1' else None
            comment = request.POST.get('comment')
            plans = TestPlan.objects.create(id=primaryKey(), name=name, tearDown=teardown, serialize=serialize, is_valid='true',
                            type=run_type, schedule=schedule, server_room_id=server_room, server_number=server_num,
                            target_num=target_number,time_setting=time_setting, duration=duration, comment=comment, operator=username)
            logger.info(f'Test plan {name} is save success, id is {plans.id}, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        server_num_rooms = get_idle_server_num(is_name=True)
        return render(request, 'performance/plan/add.html', context={'server_num_rooms': server_num_rooms})


def edit(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            plan_id = request.POST.get('plan_id')
            plan = TestPlan.objects.get(id=plan_id)
            plan.name = request.POST.get('name')
            plan.tearDown = request.POST.get('teardown')
            plan.serialize = request.POST.get('serialize')
            plan.type = request.POST.get('run_type')
            plan.schedule = request.POST.get('schedule')
            plan.server_room_id = request.POST.get('server_room')
            plan.server_number = request.POST.get('server_num')
            plan.target_num = request.POST.get('target_number')
            plan.duration = request.POST.get('duration')
            plan.time_setting = request.POST.get('time_setting') if request.POST.get('schedule') == '1' else None
            plan.comment = request.POST.get('comment')
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
            server_num_rooms = get_idle_server_num(is_name=True)
            return render(request, 'performance/plan/edit.html', context={'plan': plans, 'server_num_rooms': server_num_rooms})
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


def get_server(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            groups = request.user.groups.all()
            servers = Servers.objects.filter(group__in=groups).order_by('-id')
            all_keys = get_all_keys()
            datas = []
            status = []
            for server in servers:
                if 'jmeterServer_' + server.host in all_keys:
                    datas.append(server)
                    status.append(get_value_by_host('jmeterServer_' + server.host, 'status'))
            logger.info(f'Get pressure server info success, operator: {username}')
            return render(request, 'performance/plan/server.html', context={'servers': datas, 'status': status})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get server info Error ~')

def get_idle_server_num(is_name=False):
    result = {}
    try:
        # registered_servers = get_all_host()
        available_servers = ['127.0.10.1', '127.0.0.2', '127.0.0.3', '127.0.0.4', '127.0.0.5', '127.0.0.6']
        # available_servers = [s['host'] for s in registered_servers if s['status'] == 0]
        servers = Servers.objects.values('room_id').filter(room__type=2, host__in=available_servers).annotate(count=Count('room_id'))
        if is_name:     # whether return name
            room_dict = {}
            server_rooms = ServerRoom.objects.values('id', 'name').filter(type=2)
            for r in server_rooms:
                room_dict.update({r['id']: r['name']})
            for s in servers:
                result.update({s['room_id']: f"{room_dict[s['room_id']]} ({s['count']} idle)"})
        else:
            for s in servers:
                result.update({s['room_id']: s['count']})
        logger.info('Get idle server success ~')
    except:
        logger.error('Get idle server failure ~')
        logger.error(traceback.format_exc())
    return result
