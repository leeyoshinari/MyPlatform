#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import logging
import traceback
from django.shortcuts import render
from .models import TestPlan, GlobalVariable
from common.Result import result
from common.generator import primaryKey, strfTime
# Create your views here.


header_type = {'GET': 1, 'POST': 2}
logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 15
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word:
                plans = TestPlan.objects.filter(name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                plans = TestPlan.objects.all().order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get test plan success, operator: {username}')
            return render(request, 'performance/plan/home.html', context={'plans': plans, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word})
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
            comment = request.POST.get('comment')
            plans = TestPlan.objects.create(id=primaryKey(), name=name, tearDown=teardown, serialize=serialize, is_valid='true',
                            comment=comment, create_time=strfTime(), update_time=strfTime(), operator=username)
            logger.info(f'Test plan {name} is save success ~')
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
            comment = request.POST.get('comment')
            plan = TestPlan.objects.get(id=plan_id)
            plan.name = name
            plan.tearDown = teardown
            plan.serialize = serialize
            plan.comment = comment
            plan.update_time = strfTime()
            plan.operator = username
            plan.save()
            logger.info(f'Test plan {plan_id} is edited success ~')
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

def variable(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 15
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word:
                variables = GlobalVariable.objects.filter(plan_id=plan_id, name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                variables = GlobalVariable.objects.filter(plan_id=plan_id).order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get variables success, operator: {username}')
            return render(request, 'performance/plan/variable.html', context={'variables': variables, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'plan_id': plan_id})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get variables failure ~')

def add_variable(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            plan_id = request.POST.get('plan_id')
            name = request.POST.get('name')
            value = request.POST.get('value')
            comment = request.POST.get('comment')
            variables = GlobalVariable.objects.create(id=primaryKey(), name=name, value=value, plan_id=plan_id, comment=comment,
                                                      create_time=strfTime(), update_time=strfTime(), operator=username)
            logger.info(f'Test Plan {plan_id} variable {name} save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(msg='Save failure ~')
    else:
        plan_id = request.GET.get('id')
        return render(request, 'performance/plan/add_variable.html', context={'plan_id': plan_id})

def edit_variable(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            var_id = request.POST.get('id')
            plan_id = request.POST.get('plan_id')
            name = request.POST.get('name')
            value = request.POST.get('value')
            comment = request.POST.get('comment')
            variables = GlobalVariable.objects.get(id=var_id)
            variables.name = name
            variables.value = value
            variables.comment = comment
            variables.update_time = strfTime()
            variables.operator = username
            variables.save()
            logger.info(f'Test Plan {plan_id} variable {name} edit success, operator: {username}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return result(msg='Edit failure ~')
    else:
        var_id = request.GET.get('id')
        variables = GlobalVariable.objects.get(id=var_id)
        return render(request, 'performance/plan/edit_variable.html', context={'variables': variables})
