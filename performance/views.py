#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import logging
import traceback
from django.db.models.deletion import ProtectedError
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from .taskViews import start_test
from common.Result import result
from common.generator import toTimeStamp
# Create your views here.


logger = logging.getLogger('django')


def delete(request):
    if request.method == 'POST':
        try:
            delete_type = request.POST.get('type')
            delete_id = request.POST.get('id')
            if delete_type == 'plan':
                TestPlan.objects.get(id=delete_id).delete()
            if delete_type == 'group':
                ThreadGroup.objects.get(id=delete_id).delete()
            if delete_type == 'controller':
                TransactionController.objects.get(id=delete_id).delete()
            if delete_type == 'sample':
                HTTPSampleProxy.objects.get(id=delete_id).delete()
            if delete_type == 'header':
                HTTPRequestHeader.objects.get(id=delete_id).delete()
            if delete_type == 'task':
                PerformanceTestTask.objects.get(id=delete_id).delete()
            logger.info(f'{delete_type} {delete_id} is deleted success ~')
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
            logger.info(f'{set_type} {set_id} status is set to {is_valid} success, operator: {username}')
            return result(msg='Set success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Set failure ~')


def auto_run_task():
    try:
        tasks = PerformanceTestTask.objects.filter(plan__schedule=1, status=0)
        logger.info(f'Total auto test task is {len(tasks)}')
        for task in tasks:
            scheduler = task.plan.schedule
            if task.plan.type == 0 and -30 <= toTimeStamp(scheduler[0]['timing']) - time.time() <= 10:
                start_test(task.id, None, 'admin')
                logger.info(f'Task {task.id} - {task.plan.name} start success, type: Thread, operator: admin.')
            if task.plan.type == 1 and -60 <= toTimeStamp(scheduler[0]['timing'], delta=-600) - time.time() <= 10:
                start_test(task.id, None, 'admin')
                logger.info(f'Task {task.id} - {task.plan.name} start success, type: TPS, operator: admin.')
            if task.plan.type == 0 and toTimeStamp(scheduler[0]['timing']) - time.time() < -60:
                task.status = 4
                task.save()
            if task.plan.type == 1 and toTimeStamp(scheduler[0]['timing'], delta=-600) - time.time() < -60:
                task.status = 4
                task.save()
    except:
        logger.error(traceback.format_exc())
