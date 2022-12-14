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
from common.generator import primaryKey, strfTime
from common.customException import MyException
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
                total_page = TestPlan.objects.filter(is_file=1, group__in=groups, name__contains=key_word).count()
                plans = TestPlan.objects.filter(is_file=1, group__in=groups, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = TestPlan.objects.filter(is_file=1, group__in=groups).count()
                plans = TestPlan.objects.filter(is_file=1, group__in=groups).order_by('-create_time')[page_size * (page - 1): page_size * page]
            if plans:
                server_num_rooms = get_idle_server_num()
            logger.info(f'Get test plan success, operator: {username}, IP: {ip}')
            return render(request, 'jmeter/home.html', context={'plans': plans, 'page': page, 'page_size': page_size, 'server_num_rooms': server_num_rooms,
                                                                     'key_word': key_word, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')

def edit(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            plan = TestPlan.objects.get(id=plan_id)
            plan.name = data.get('name')
            plan.type = data.get('run_type')
            plan.schedule = data.get('schedule')
            plan.server_room_id = data.get('server_room')
            plan.group_id = data.get('group_id')
            plan.server_number = data.get('server_num')
            plan.target_num = data.get('target_number')
            plan.duration = data.get('duration')
            plan.is_debug = data.get('is_debug')
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
            return render(request, 'jmeter/edit.html', context={'plan': plans, 'server_rooms': server_rooms,
                                                                            'groups': groups, 'current_time': strfTime()})
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
                logger.error('Not found ".jmx" file, Please zip file not folder ~')
                return result(code=1, msg='Not found ".jmx" file, Please zip file not folder ~')
            if len(jmx_file) > 1:
                _ = delete_local_file(temp_file_path)
                logger.error('Too many ".jmx" files, Only one ".jmx" file is allowed ~')
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
                res = settings.MINIO_CLIENT.upload_file_by_path(file_name, zip_file_path)
                zip_file_url = f'{res.bucket_name}/{res.object_name}'
            del_file = delete_local_file(temp_file_path)
            if del_file['code'] == 1:
                logger.error(del_file['msg'])
            task_path = f'{settings.FILE_URL}{zip_file_url}'
            plans = TestPlan.objects.create(id=file_id, name=file_name, group_id=groups[0].id, is_valid='true',is_file=1, file_path=task_path, operator=username)
            logger.info(f'{file_name} upload success, operator: {username}, IP: {ip}')
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
            ip = request.headers.get('x-real-ip')
            plan_id = request.POST.get('plan_id')
            tasks = PerformanceTestTask.objects.filter(plan_id=plan_id, plan__schedule=1, status__lte=1)
            if len(tasks) > 0:
                logger.info(f'Plan {plan_id} has generated task, operator: {username}, IP: {ip}')
                return result(code=1, msg='There has been task, please check it ~')

            plans = TestPlan.objects.get(id=plan_id)
            task_id = str(primaryKey())
            if plans.is_valid == 'true':
                # write file to local
                test_jmeter_path = os.path.join(settings.TEMP_PATH, task_id)
                if not os.path.exists(test_jmeter_path):
                    os.mkdir(test_jmeter_path)
                jmeter_zip_file_path = os.path.join(test_jmeter_path, task_id + '.zip')
                download_file_to_path(plans.file_path, jmeter_zip_file_path)    # download file
                unzip_file(jmeter_zip_file_path, test_jmeter_path)      # unzip file
                jmx_file = [f for f in os.listdir(test_jmeter_path) if f.endswith('.jmx')]  # get jmx file
                source_jmeter_path = os.path.join(test_jmeter_path, jmx_file[0])
                number_of_samples = get_enabled_samples_num(source_jmeter_path)     # get number of http samples
                jmeter_file_path = os.path.join(test_jmeter_path, task_id + '.jmx')
                # modify jmx file
                modify_jmeter(source_jmeter_path, jmeter_file_path, plans.type, plans.schedule, plans.target_num, plans.duration, number_of_samples)
                os.remove(source_jmeter_path)       # remove source jmx file
                os.remove(jmeter_zip_file_path)
                # write zip file to temp path
                temp_file_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
                if not os.path.exists(temp_file_path):
                    os.mkdir(temp_file_path)
                zip_file_path = os.path.join(temp_file_path, task_id + '.zip')
                zip_file(test_jmeter_path, zip_file_path)
                # upload file
                if settings.FILE_STORE_TYPE == '0':
                    zip_file_url = f'{settings.STATIC_URL}files/{task_id}/{task_id}.zip'
                else:
                    res = settings.MINIO_CLIENT.upload_file_by_path(task_id + '.zip', zip_file_path)
                    zip_file_url = f'{res.bucket_name}/{res.object_name}'
                    os.remove(zip_file_path)
                    _ = delete_local_file(temp_file_path)
                logger.info(f'zip file is written successfully, operator: {username}, zip file: {zip_file_url}, IP: {ip}')
                task_path = f'{settings.FILE_URL}{zip_file_url}'
                del_file = delete_local_file(test_jmeter_path)
                if del_file['code'] == 1:
                    logger.error(del_file['msg'])
            else:
                logger.error(f'The JMeter file has been disabled, operator: {username}, IP: {ip}')
                return result(code=1, msg='The JMeter file has been disabled ~')

            tasks = PerformanceTestTask.objects.create(id=task_id, plan_id=plan_id, ratio=1, status=0, number_samples=number_of_samples,
                                                      group_id=plans.group_id, server_room_id=plans.server_room_id, path=task_path, operator=username)
            logger.info(f'Task {tasks.id} generate success, operator: {username}, IP: {ip}')
            if plans.schedule == 0:
                return result(msg=f'Start success ~', data={'taskId': task_id, 'flag': 1})
            else:
                return result(msg=f'Add to test task success ~', data={'flag': 0})
        except MyException as err:
            test_jmeter_path = os.path.join(settings.TEMP_PATH, task_id)
            if os.path.exists(test_jmeter_path):
                _ = delete_local_file(test_jmeter_path)
            temp_file_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
            if os.path.exists(temp_file_path):
                _ = delete_local_file(temp_file_path)
            logger.error(traceback.format_exc())
            return result(code=1, msg=err.msg)
        except:
            test_jmeter_path = os.path.join(settings.TEMP_PATH, task_id)
            if os.path.exists(test_jmeter_path):
                _ = delete_local_file(test_jmeter_path)
            temp_file_path = os.path.join(settings.FILE_ROOT_PATH, task_id)
            if os.path.exists(temp_file_path):
                _ = delete_local_file(temp_file_path)
            logger.error(traceback.format_exc())
            return result(code=1, msg='Start failure ~')
