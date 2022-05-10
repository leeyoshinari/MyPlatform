#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import logging
import traceback
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
from django.db.models.deletion import ProtectedError
from .models import TestPlan, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from common.Result import result
from common.generator import primaryKey, strfTime
from .common.parseJmx import read_jmeter_from_byte
# Create your views here.


header_type = {'GET': 1, 'POST': 2}
logger = logging.getLogger('django')


def delete(request):
    if request.method == 'POST':
        try:
            delete_type = request.POST.get('type')
            delete_id = request.POST.get('id')
            if delete_type == 'plan':
                TestPlan.objects.get(id=delete_id).delete()
            if delete_type == 'variable':
                GlobalVariable.objects.get(id=delete_id).delete()
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

def parse_jmx(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            res = read_jmeter_from_byte('')
            for plan in res:
                testPlan = TestPlan.objects.create(id=primaryKey(), name=plan.get('testname'), comment=plan.get('comments'),
                                        tearDown=plan.get('tearDown_on_shutdown'), serialize=plan.get('serialize_threadgroups'),
                                        is_valid=plan.get('enabled'), create_time=strfTime(), update_time=strfTime(),
                                        operator=username)
                for k, v in plan['arguments'].items():
                    global_variable = GlobalVariable.objects.create(id=primaryKey(), plan_id=testPlan.id, name=k, value=v,
                                                                    create_time=strfTime(), update_time=strfTime(), operator=username)
                for tg in plan['thread_group']:
                    thread = ThreadGroup.objects.create(id=primaryKey(), plan_id=testPlan.id, name=tg.get('testname'),
                                        is_valid=tg.get('enabled'), num_threads=tg.get('num_threads'), ramp_time=tg.get('ramp_time'),
                                        duration=tg.get('duration'), scheduler=tg.get('scheduler'), comment=tg.get('comments'),
                                        create_time=strfTime(), update_time=strfTime(), operator=username)
                    for ctl in tg['controller']:
                        controller = TransactionController.objects.create(id=primaryKey(), thread_group_id=thread.id,
                                        name=ctl.get('testname'), is_valid=ctl.get('enabled'), comment=ctl.get('comments'),
                                        create_time=strfTime(), update_time=strfTime(), operator=username)
                        for sample in ctl['http_sample']:
                            http = HTTPSampleProxy.objects.create(id=primaryKey(), controller_id=controller.id, name=sample.get('testname'),
                                        is_valid=sample.get('enabled'), comment=sample.get('sample_dict').get('comments'),
                                        domain=sample.get('sample_dict').get('domain'), port=sample.get('sample_dict').get('port'),
                                        protocol=sample.get('sample_dict').get('protocol'), path=sample.get('sample_dict').get('path'),
                                        method=sample.get('sample_dict').get('method'), contentEncoding=sample.get('sample_dict').get('contentEncoding'),
                                        argument=sample.get('arguments'), http_header_id=header_type.get(sample.get('sample_dict').get('method')),
                                        assert_type=sample.get('assertion').get('test_type'), assert_content=sample.get('assertion').get('test_string'),
                                        extractor=sample.get('extractor'), create_time=strfTime(), update_time=strfTime(), operator=username)
        except:
            logger.error(traceback.format_exc())
