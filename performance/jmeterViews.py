#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import json
import logging
import shutil
import traceback
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from django.db.models import Count
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from shell.models import Servers, ServerRoom
from .planViews import get_idle_server_num
from .common.generateJmx import *
from .common.getRedis import *
from .common.fileController import *
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
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word:
                total_page = TestPlan.objects.filter(is_file=1, name__contains=key_word).count()
                plans = TestPlan.objects.filter(is_file=1, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = TestPlan.objects.filter(is_file=1).count()
                plans = TestPlan.objects.filter(is_file=1).order_by('-create_time')[page_size * (page - 1): page_size * page]
            if plans:
                server_num_rooms = get_idle_server_num()
            logger.info(f'Get test plan success, operator: {username}')
            return render(request, 'performance/jmeter/home.html', context={'plans': plans, 'page': page, 'page_size': page_size, 'server_num_rooms': server_num_rooms,
                                                                     'key_word': key_word, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get test plan failure ~')

def edit(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            plan_id = request.POST.get('plan_id')
            plan = TestPlan.objects.get(id=plan_id)
            plan.name = request.POST.get('name')
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
            server_rooms = ServerRoom.objects.filter(type=2).order_by('-create_time')
            return render(request, 'performance/jmeter/edit.html', context={'plan': plans, 'server_rooms': server_rooms})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get test plan failure ~')


def upload_file(request):
    if request.method == 'POST':
        username = request.user.username
        form = request.FILES['file']
        file_name = form.name
        # file_byte = form.file.read()
        try:
            file_id = primaryKey()
            temp_file_path = os.path.join(settings.TEMP_PATH, file_id)
            if not os.path.exists(temp_file_path):
                os.mkdir(temp_file_path)
            zip_file_path = os.path.join(temp_file_path, file_name)
            with open(zip_file_path, 'wb') as f:
                f.write(form.file)
            unzip_file(zip_file_path, temp_file_path)
            jmx_file = [f for f in os.listdir(temp_file_path) if f.endswith('.jmx')]
            if len(jmx_file) == 0:
                return result(code=1, msg='Not found ".jmx" file, Please zip file not folder ~')
            if len(jmx_file) > 1:
                return result(code=1, msg='Too many ".jmx" files, Only one ".jmx" file is allowed ~')
            # upload file
            if settings.FILE_STORE_TYPE == '0':
                local_file_path = os.path.join(settings.FILE_ROOT_PATH, file_id)
                if not os.path.exists(local_file_path):
                    os.mkdir(local_file_path)
                with open(os.path.join(local_file_path, f'{file_id}.zip'), 'wb') as f:
                    f.write(form.file)
                zip_file_url = f'{settings.STATIC_URL}files/{file_id}/{file_id}.zip'
            else:
                zip_file_url = upload_file_by_path(settings.FILE_STORE_TYPE, zip_file_path)
            plans = TestPlan.objects.create(id=file_id, name=file_name, is_valid='true',is_file=1, file_path=zip_file_url,
                                            operator=username)
            logger.info(f'{file_name} upload success, operator: {username}')
            return result(msg=f'{file_name} upload success ~', data=file_name)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'{file_name} upload failure ~', data=file_name)


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

