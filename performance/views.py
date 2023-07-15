#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import time
import logging
import traceback
from django.db.models.deletion import ProtectedError
from django.conf import settings
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from .taskViews import start_test
from .common.fileController import delete_local_file
from common.Result import result
from common.generator import toTimeStamp
from common.multiThread import start_thread
# Create your views here.


logger = logging.getLogger('django')
is_auto_run = False


def delete_file_from_disk(file_path):
    path_list = file_path.split('/')
    if settings.FILE_STORE_TYPE == '0':
        try:
            file_folder = os.path.join(settings.FILE_ROOT_PATH, path_list[-2])
            file_local_path = os.path.join(file_folder, path_list[-1])
            os.remove(file_local_path)
            _ = delete_local_file(file_folder)
        except FileNotFoundError:
            logger.warning(f"FileNotFound: No such file: {file_path}")
    else:
        settings.MINIO_CLIENT.delete_file(path_list[-2], path_list[-1])


def delete(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            delete_type = request.POST.get('type')
            delete_id = request.POST.get('id')
            if delete_type == 'plan':
                plan = TestPlan.objects.get(id=delete_id)
                if plan.is_file == 1:
                    delete_file_from_disk(plan.file_path)
                plan.delete()
            if delete_type == 'group':
                group = ThreadGroup.objects.get(id=delete_id)
                if group.file:
                    file_path = group.file.get('file_path')
                    delete_file_from_disk(file_path)
                group.delete()
            if delete_type == 'controller':
                TransactionController.objects.get(id=delete_id).delete()
            if delete_type == 'sample':
                HTTPSampleProxy.objects.get(id=delete_id).delete()
            if delete_type == 'header':
                HTTPRequestHeader.objects.get(id=delete_id).delete()
            if delete_type == 'task':
                task = PerformanceTestTask.objects.get(id=delete_id)
                if task.path:
                    delete_file_from_disk(task.path)
                task.delete()
            logger.info(f'{delete_type} {delete_id} is deleted success, operator: {username}, IP: {ip}')
            return result(msg='Delete success ~')
        except ProtectedError:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete failure, because it is referenced through protected foreign keys ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete failure ~')

def is_valid(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            set_type = request.POST.get('set_type')
            set_id = request.POST.get('id')
            is_valid = request.POST.get('is_valid')
            if set_type == 'plan':
                res = TestPlan.objects.get(id=set_id)
            if set_type == 'group':
                res = ThreadGroup.objects.get(id=set_id)
            if set_type == 'controller':
                res = TransactionController.objects.get(id=set_id)
            if set_type == 'sample':
                res = HTTPSampleProxy.objects.get(id=set_id)
            res.is_valid = is_valid
            res.operator = username
            res.save()
            logger.info(f'{set_type} {set_id} status is set to {is_valid} success, operator: {username}, IP: {ip}')
            return result(msg='Set success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Set failure ~')

def request_auto_run(request):
    if request.method == 'GET':
        username = request.user.username
        ip = request.headers.get('x-real-ip')
        start_thread(auto_run_task, ())
        logger.info(f'Auto run performance test task success, operator: {username}, IP: {ip}')
        return result(msg='success')

def auto_run_task():
    global is_auto_run
    if not is_auto_run:
        index = 0
        is_auto_run = True
        while True:
            try:
                tasks = PerformanceTestTask.objects.filter(plan__schedule=1, status=0)
                logger.info(f'Total auto test task is {len(tasks)}')
                if len(tasks) == 0:
                    index += 1
                if index > 3:
                    is_auto_run = False
                    break
                for task in tasks:
                    scheduler = task.plan.time_setting
                    if task.plan.type == 0 and -10 <= toTimeStamp(scheduler[0]['timing']) - time.time() <= 10:
                        start_test(task.id, None, 'admin')
                        logger.info(f'Task {task.id} - {task.plan.name} start success, type: Thread, operator: admin.')
                    if task.plan.type == 1 and -10 <= toTimeStamp(scheduler[0]['timing'], delta=-60) - time.time() <= 10:
                        start_test(task.id, None, 'admin')
                        logger.info(f'Task {task.id} - {task.plan.name} start success, type: TPS, operator: admin.')
                    if task.plan.type == 0 and toTimeStamp(scheduler[0]['timing']) - time.time() < -30:
                        task.status = 4
                        task.save()
                        logger.info(f'Modify task {task.id} status to Cancel ~')
                    if task.plan.type == 1 and toTimeStamp(scheduler[0]['timing'], delta=-60) - time.time() < -30:
                        task.status = 4
                        task.save()
                        logger.info(f'Modify task {task.id} status to Cancel ~')
            except:
                logger.error(traceback.format_exc())
            time.sleep(15)
    else:
        logger.info('Auto run task is running ~')
