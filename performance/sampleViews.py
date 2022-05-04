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
            ctl_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 15
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and ctl_id:
                samples = HTTPSampleProxy.objects.filter(controller_id=ctl_id, name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif ctl_id and not key_word:
                samples = HTTPSampleProxy.objects.filter(controller_id=ctl_id).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif key_word and not ctl_id:
                samples = HTTPSampleProxy.objects.filter(name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                samples = HTTPSampleProxy.objects.all().order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get http samples success, operator: {username}')
            return render(request, 'performance/httpSample/home.html', context={'samples': samples, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'controller_id': ctl_id})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get controller failure ~')


def add_sample(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            name = request.POST.get('name')
            group_id = request.POST.get('controller_id')
            comment = request.POST.get('comment')
            controller = TransactionController.objects.create(id=primaryKey(), name=name, comment=comment, is_valid='true',
                          thread_group_id=group_id, create_time=strfTime(), update_time=strfTime(), operator=username)
            logger.info(f'Controller {name} {controller.id} is save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        ctl_id = request.GET.get('id')
        ctl_id = int(ctl_id) if ctl_id else ctl_id
        controllers = TransactionController.objects.all().order_by('-update_time')
        http_headers = HTTPRequestHeader.objects.all().order_by('-update_time')
        return render(request, 'performance/httpSample/add.html', context={'controller_id': ctl_id, 'controllers': controllers,
                                                                           'http_headers': http_headers})

def edit_sample(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            controller_id = request.POST.get('id')
            name = request.POST.get('name')
            group_id = request.POST.get('group_id')
            comment = request.POST.get('comment')
            controllers = TransactionController.objects.get(id=controller_id)
            controllers.name = name
            controllers.thread_group_id = group_id
            controllers.comment = comment
            controllers.update_time = strfTime()
            controllers.operator = username
            controllers.save()
            logger.info(f'Controller {controller_id} is edit success, operator: {username}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        group_id = request.GET.get('id')
        controllers = TransactionController.objects.get(id=group_id)
        groups = ThreadGroup.objects.all().order_by('-update_time')
        return render(request, 'performance/controller/edit.html', context={'controllers': controllers, 'groups': groups})
