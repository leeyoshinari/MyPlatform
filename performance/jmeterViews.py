#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import json
import logging
import traceback
from django.shortcuts import render
from django.conf import settings
from .models import TestPlan, PerformanceTestTask
from shell.models import ServerRoom
from .planViews import get_idle_server_num
from .common.getRedis import *
from .common.fileController import *
from .common.parseJmx import modify_jmeter, get_enabled_samples_num
from common.Result import result
from common.generator import primaryKey
from common.customException import MyException
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
        file_id = str(primaryKey())
        try:
            temp_file_path = os.path.join(settings.TEMP_PATH, file_id)
            if not os.path.exists(temp_file_path):
                os.mkdir(temp_file_path)
            zip_file_path = os.path.join(temp_file_path, file_name)
            with open(zip_file_path, 'wb') as f:
                f.write(form.file.read())
            unzip_file(zip_file_path, temp_file_path)
            jmx_file = [f for f in os.listdir(temp_file_path) if f.endswith('.jmx')]
            if len(jmx_file) == 0:
                _ = delete_local_file(temp_file_path)
                return result(code=1, msg='Not found ".jmx" file, Please zip file not folder ~')
            if len(jmx_file) > 1:
                _ = delete_local_file(temp_file_path)
                return result(code=1, msg='Too many ".jmx" files, Only one ".jmx" file is allowed ~')
            # upload file
            if settings.FILE_STORE_TYPE == '0':
                local_file_path = os.path.join(settings.FILE_ROOT_PATH, file_id)
                if not os.path.exists(local_file_path):
                    os.mkdir(local_file_path)
                ff = open(os.path.join(local_file_path, f'{file_id}.zip'), 'wb')
                with open(zip_file_path, 'rb') as f:
                    ff.write(f.read())
                ff.close()
                zip_file_url = f'{settings.STATIC_URL}files/{file_id}/{file_id}.zip'
            else:
                zip_file_url = upload_file_by_path(settings.FILE_STORE_TYPE, zip_file_path)
            del_file = delete_local_file(temp_file_path)
            if del_file['code'] == 1:
                logger.error(del_file['msg'])
            task_path = f'{settings.FILE_URL}{zip_file_url}'
            plans = TestPlan.objects.create(id=file_id, name=file_name, is_valid='true',is_file=1, file_path=task_path, operator=username)
            logger.info(f'{file_name} upload success, operator: {username}')
            return result(msg=f'{file_name} upload success ~', data=file_name)
        except:
            temp_file_path = os.path.join(settings.TEMP_PATH, file_id)
            if os.path.exists(temp_file_path):
                _ = delete_local_file(temp_file_path)
            local_file_path = os.path.join(settings.FILE_ROOT_PATH, file_id)
            if os.path.exists(local_file_path):
                _ = delete_local_file(local_file_path)
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'{file_name} upload failure ~', data=file_name)


def add_to_task(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            plan_id = request.POST.get('plan_id')
            plans = TestPlan.objects.get(id=plan_id)
            task_id = str(primaryKey())
            if plans.is_valid == 'true':
                # write file to local
                test_jmeter_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
                if not os.path.exists(test_jmeter_path):
                    os.mkdir(test_jmeter_path)
                jmeter_zip_file_path = os.path.join(test_jmeter_path, task_id + '.zip')
                download_file_to_path(plans.file_path, jmeter_zip_file_path)    # download file
                unzip_file(jmeter_zip_file_path, test_jmeter_path)      # unzip file
                jmx_file = [f for f in os.listdir(test_jmeter_path) if f.endswith('.jmx')]  # get jmx file
                source_jmeter_path = os.path.join(test_jmeter_path, jmx_file[0])
                number_of_samples = get_enabled_samples_num(source_jmeter_path)     # get number of http samples
                jmeter_file_path = os.path.join(test_jmeter_path, 'test.jmx')
                # modify jmx file
                modify_jmeter(source_jmeter_path, jmeter_file_path, plans.type, plans.target_num, plans.duration)
                os.remove(source_jmeter_path)       # remove source jmx file
                os.remove(jmeter_zip_file_path)
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
                logger.error('The JMeter file has been disabled ~')
                return result(code=1, msg='The JMeter file has been disabled ~')

            tasks = PerformanceTestTask.objects.create(id=task_id, plan_id=plan_id, ratio=1, status=0, number_samples=number_of_samples,
                                                       server_room_id=plans.server_room_id, path=task_path, operator=username)
            logger.info(f'Task {tasks.id} generate success, operator: {username}')
            return result(msg=f'Start success ~', data=task_id)
        except MyException as err:
            test_jmeter_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
            if os.path.exists(test_jmeter_path):
                _ = delete_local_file(test_jmeter_path)
            temp_file_path = os.path.join(settings.TEMP_PATH, task_id)
            if os.path.exists(temp_file_path):
                _ = delete_local_file(temp_file_path)
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'"{err}"')
        except:
            test_jmeter_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
            if os.path.exists(test_jmeter_path):
                _ = delete_local_file(test_jmeter_path)
            temp_file_path = os.path.join(settings.TEMP_PATH, task_id)
            if os.path.exists(temp_file_path):
                _ = delete_local_file(temp_file_path)
            logger.error(traceback.format_exc())
            return result(code=1, msg='Start failure ~')
