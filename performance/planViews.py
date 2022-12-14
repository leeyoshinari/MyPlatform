#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from django.db.models import Count
from .models import TestPlan, ThreadGroup, TransactionController, HTTPSampleProxy
from shell.models import Servers, ServerRoom
from .common.parseJmx import read_jmeter_from_byte
from .common.getRedis import *
from .threadViews import copy_one_group
from common.Result import result
from common.generator import primaryKey, strfTime
# Create your views here.


header_type = {'GET': 1, 'POST': 2}
logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            server_num_rooms = {}
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            groups = request.user.groups.all()
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word:
                total_page = TestPlan.objects.filter(is_file=0, group__in=groups, name__contains=key_word).count()
                plans = TestPlan.objects.filter(is_file=0, group__in=groups, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = TestPlan.objects.filter(is_file=0, group__in=groups).count()
                plans = TestPlan.objects.filter(is_file=0, group__in=groups).order_by('-create_time')[page_size * (page - 1): page_size * page]
            if plans:
                server_num_rooms = get_idle_server_num()
            logger.info(f'Get test plan success, operator: {username}, IP: {ip}')
            return render(request, 'plan/home.html', context={'plans': plans, 'page': page, 'page_size': page_size, 'server_num_rooms': server_num_rooms,
                                                                     'key_word': key_word, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')

def add(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            data = json.loads(request.body)
            name = data.get('name')
            teardown = data.get('teardown')
            serialize = data.get('serialize')
            run_type = data.get('run_type')
            schedule = data.get('schedule')
            server_room = data.get('server_room')
            group_id = data.get('group_id')
            server_num = data.get('server_num')
            is_debug = data.get('is_debug')
            target_number = data.get('target_number')
            duration = data.get('duration')
            time_setting = data.get('time_setting') if schedule == '1' else []
            comment = data.get('comment')
            plans = TestPlan.objects.create(id=primaryKey(), name=name, tearDown=teardown, serialize=serialize, is_valid='true',
                            type=run_type, schedule=schedule, server_room_id=server_room, group_id=group_id, server_number=server_num,
                            target_num=target_number,time_setting=time_setting, duration=duration,
                            is_debug=is_debug, comment=comment, operator=username)
            logger.info(f'Test plan {name} is save success, id is {plans.id}, operator: {username}, IP: {ip}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        groups = request.user.groups.all()
        server_rooms = ServerRoom.objects.filter(type=2).order_by('-create_time')
        return render(request, 'plan/add.html', context={'server_rooms': server_rooms, 'groups': groups})


def edit(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            plan = TestPlan.objects.get(id=plan_id)
            plan.name = data.get('name')
            plan.tearDown = data.get('teardown')
            plan.serialize = data.get('serialize')
            plan.type = data.get('run_type')
            plan.schedule = data.get('schedule')
            plan.server_room_id = data.get('server_room')
            plan.group_id = data.get('group_id')
            plan.server_number = data.get('server_num')
            plan.target_num = data.get('target_number')
            plan.is_debug = data.get('is_debug')
            plan.duration = data.get('duration')
            if data.get('schedule') == '1':
                plan.time_setting = data.get('time_setting')
            plan.comment = data.get('comment')
            plan.operator = username
            plan.save()
            logger.info(f'Test plan {plan_id} is edited success, operator: {username}, IP: {ip}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Edit failure ~')
    else:
        try:
            plan_id = request.GET.get('id')
            groups = request.user.groups.all()
            plans = TestPlan.objects.get(id=plan_id)
            server_rooms = ServerRoom.objects.filter(type=2).order_by('-create_time')
            return render(request, 'plan/edit.html', context={'plan': plans, 'server_rooms': server_rooms,
                                                                          'groups': groups, 'current_time': strfTime()})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')

def edit_variable(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            variables = data.get('variables')
            plans = TestPlan.objects.get(id=plan_id)
            plans.variables = variables
            plans.save()
            logger.info(f'Test Plan {plan_id} variable save success, operator: {username}, IP: {ip}')
            return result(msg='Save variables success ~')
        except:
            logger.error(traceback.format_exc())
            return result(msg='Save variables failure ~')
    else:
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            plan_id = request.GET.get('id')
            variables = TestPlan.objects.get(id=plan_id)
            logger.info(f'Get test plan variables success, operator: {username}, IP: {ip}')
            return render(request, 'plan/variable.html', context={'variables': variables})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')


def upload_file(request):
    if request.method == 'POST':
        username = request.user.username
        ip = request.headers.get('x-real-ip')
        groups = request.user.groups.all().order_by('-id')
        form = request.FILES['file']
        file_name = form.name
        file_byte = form.file.read()
        try:
            res = read_jmeter_from_byte(file_byte)
            parse_jmx_to_database(res, groups[0].id, username)
            logger.info(f'{file_name} Import Success, operator: {username}, IP: {ip}')
            return result(msg=f'{file_name} Import Success ~', data=file_name)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'{file_name} Import Failure ~', data=file_name)


def parse_jmx_to_database(res, group_id, username):
    try:
        for plan in res:
            testPlan = TestPlan.objects.create(id=primaryKey(), name=plan.get('testname'), comment=plan.get('comments'),
                                    tearDown=plan.get('tearDown_on_shutdown'), serialize=plan.get('serialize_threadgroups'), group_id=group_id,
                                    variables=plan['arguments'], is_valid=plan.get('enabled'), operator=username)
            for tg in plan['thread_group']:
                thread = ThreadGroup.objects.create(id=primaryKey(), plan_id=testPlan.id, name=tg.get('testname'), group=group_id,
                                    is_valid=tg.get('enabled'), ramp_time=tg.get('ramp_time'), comment=tg.get('comments'), operator=username)
                for ctl in tg['controller']:
                    controller = TransactionController.objects.create(id=primaryKey(), thread_group_id=thread.id, group=group_id,
                                    name=ctl.get('testname'), is_valid=ctl.get('enabled'), comment=ctl.get('comments'),
                                    operator=username)
                    for sample in ctl['http_sample']:
                        http = HTTPSampleProxy.objects.create(id=primaryKey(), controller_id=controller.id, name=sample.get('testname'),
                                    is_valid=sample.get('enabled'), comment=sample.get('sample_dict').get('comments'), group=group_id,
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
            ip = request.headers.get('x-real-ip')
            plan_id = request.GET.get('id')
            plans = TestPlan.objects.get(id=plan_id)
            keyWord = plans.name
            plans.id = primaryKey()
            plans.name = plans.name + ' - Copy'
            plans.operator = username
            plans.save()
            thread_groups = ThreadGroup.objects.filter(plan_id=plan_id)
            for thread_group in thread_groups:
                copy_one_group(plans.id, thread_group.id, username, ip)
            logger.info(f'Copy plan {plan_id} success, target plan is {plans.id}, operator: {username}, IP: {ip}')
            return redirect(resolve_url('perf:plan_home') + '?keyWord=' + keyWord)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy Plan Failure ~')


# def get_server(request):
#     if request.method == 'GET':
#         try:
#             username = request.user.username
#             groups = request.user.groups.all()
#             servers = Servers.objects.filter(group__in=groups).order_by('-id')
#             all_keys = get_all_keys()
#             datas = []
#             status = []
#             for server in servers:
#                 if 'jmeterServer_' + server.host in all_keys:
#                     datas.append(server)
#                     status.append(get_value_by_host('jmeterServer_' + server.host, 'status'))
#             logger.info(f'Get pressure server info success, operator: {username}')
#             return render(request, 'performance/plan/server.html', context={'servers': datas, 'status': status})
#         except:
#             logger.error(traceback.format_exc())
#             return result(code=1, msg='Get server info Error ~')

def get_idle_server_num(is_name=False):
    result = {}
    try:
        registered_servers = get_all_host()
        available_servers = [s['host'] for s in registered_servers if s['status'] == 0]
        servers = Servers.objects.values('room_id').filter(room__type=2, host__in=available_servers).annotate(count=Count('room_id'))
        logger.info(servers.query)
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
