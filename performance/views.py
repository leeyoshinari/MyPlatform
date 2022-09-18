#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import logging
import traceback
from django.db.models.deletion import ProtectedError
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from common.Result import result
from common.generator import primaryKey, strfTime
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
            res.update_time = strfTime()
            res.save()
            logger.info(f'{set_type} {set_id} status is set to {is_valid} success, operator: {username}')
            return result(msg='Set success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Set failure ~')
