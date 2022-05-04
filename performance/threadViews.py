#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import logging
import traceback
from django.shortcuts import render
from .models import TestPlan, GlobalVariable, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from common.Result import result
from common.generator import primaryKey, strfTime
# Create your views here.


logger = logging.getLogger('django')


def home(request):
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
            if key_word and plan_id:
                groups = ThreadGroup.objects.filter(plan_id=plan_id, name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif plan_id and not key_word:
                groups = ThreadGroup.objects.filter(plan_id=plan_id).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif key_word and not plan_id:
                groups = ThreadGroup.objects.filter(name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                groups = ThreadGroup.objects.all().order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get thread group success, operator: {username}')
            return render(request, 'performance/threadGroup/home.html', context={'groups': groups, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'plan_id': plan_id})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get test plan failure ~')


def add_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            name = request.POST.get('name')
            plan_id = request.POST.get('plan_id')
            num_threads = request.POST.get('num_threads')
            ramp_time = request.POST.get('ramp_time')
            scheduler = request.POST.get('scheduler')
            duration = request.POST.get('duration')
            duration = duration if duration else None
            comment = request.POST.get('comment')
            group = ThreadGroup.objects.create(id=primaryKey(), name=name, num_threads=num_threads, ramp_time=ramp_time,
                                duration=duration, comment=comment, scheduler=scheduler, is_valid='true', plan_id=plan_id,
                                create_time=strfTime(), update_time=strfTime(), operator=username)
            logger.info(f'Thread Group {name} {group.id} is save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        plan_id = request.GET.get('id')
        plan_id = int(plan_id) if plan_id else plan_id
        plans = TestPlan.objects.all().order_by('-update_time')
        return render(request, 'performance/threadGroup/add.html', context={'plan_id': plan_id, 'plans': plans})

def edit_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            group_id = request.POST.get('id')
            name = request.POST.get('name')
            plan_id = request.POST.get('plan_id')
            num_threads = request.POST.get('num_threads')
            ramp_time = request.POST.get('ramp_time')
            scheduler = request.POST.get('scheduler')
            duration = request.POST.get('duration')
            duration = duration if duration else None
            comment = request.POST.get('comment')
            groups = ThreadGroup.objects.get(id=group_id)
            groups.name = name
            groups.plan_id = plan_id
            groups.num_threads = num_threads
            groups.ramp_time = ramp_time
            groups.scheduler = scheduler
            groups.duration = duration
            groups.comment = comment
            groups.update_time = strfTime()
            groups.operator = username
            groups.save()
            logger.info(f'Thread Group {group_id} is edit success, operator: {username}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        group_id = request.GET.get('id')
        groups = ThreadGroup.objects.get(id=group_id)
        plans = TestPlan.objects.all().order_by('-update_time')
        return render(request, 'performance/threadGroup/edit.html', context={'groups': groups, 'plans': plans})
