#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import logging
import traceback
from django.conf import settings
from django.shortcuts import render, redirect, resolve_url
from .models import ThreadGroup, TransactionController, HTTPSampleProxy
from .sampleViews import copy_one_sample
from common.Result import result
from common.generator import primaryKey
# Create your views here.


logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            groups = request.user.groups.all().values('id')
            group_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and group_id:
                total_page = TransactionController.objects.filter(thread_group_id=group_id, name__contains=key_word).count()
                controllers = TransactionController.objects.filter(thread_group_id=group_id, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif group_id and not key_word:
                total_page = TransactionController.objects.filter(thread_group_id=group_id).count()
                controllers = TransactionController.objects.filter(thread_group_id=group_id).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif key_word and not group_id:
                total_page = TransactionController.objects.filter(group__in=groups, name__contains=key_word).count()
                controllers = TransactionController.objects.filter(group__in=groups, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = TransactionController.objects.filter(group__in=groups).count()
                controllers = TransactionController.objects.filter(group__in=groups).order_by('-create_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get controller success, operator: {username}, IP: {ip}')
            return render(request, 'controller/home.html', context={'controllers': controllers, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'group_id': group_id, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def add_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            name = request.POST.get('name')
            group_id = request.POST.get('group_id')
            comment = request.POST.get('comment')
            my_group = ThreadGroup.objects.values('group').get(id=group_id)
            controller = TransactionController.objects.create(id=primaryKey(), name=name, comment=comment, is_valid='true',
                          thread_group_id=group_id, group=my_group['group'], operator=username)
            logger.info(f'Controller {name} {controller.id} is save success, operator: {username}, IP: {ip}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        try:
            group_id = request.GET.get('id')
            if group_id:
                group = ThreadGroup.objects.values('group').get(id=group_id)
                groups = ThreadGroup.objects.filter(group=group['group']).order_by('-create_time')
            else:
                my_groups = request.user.groups.all().values('id')
                groups = ThreadGroup.objects.filter(group__in=my_groups).order_by('-create_time')
            return render(request, 'controller/add.html', context={'group_id': group_id, 'groups': groups})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')

def edit_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            controller_id = request.POST.get('id')
            name = request.POST.get('name')
            group_id = request.POST.get('group_id')
            comment = request.POST.get('comment')
            my_group = ThreadGroup.objects.values('group').get(id=group_id)
            controllers = TransactionController.objects.get(id=controller_id)
            controllers.name = name
            controllers.thread_group_id = group_id
            controllers.group = my_group['group']
            controllers.comment = comment
            controllers.operator = username
            controllers.save()
            logger.info(f'Controller {controller_id} is edit success, operator: {username}, IP: {ip}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        try:
            group_id = request.GET.get('id')
            controllers = TransactionController.objects.get(id=group_id)
            groups = ThreadGroup.objects.filter(group=controllers.thread_group.group).order_by('-create_time')
            return render(request, 'controller/edit.html', context={'controllers': controllers, 'groups': groups})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')

def copy_controller(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            controller_id = request.GET.get('id')
            group_id = request.GET.get('group_id')
            copy_one_controller(group_id, controller_id, username, ip)
            return redirect(resolve_url('perf:controller_home') + '?id=' + group_id)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy controller Failure ~')

def copy_one_controller(group_id, controller_id, username, ip):
    controllers = TransactionController.objects.get(id=controller_id)
    controllers.id = primaryKey()
    controllers.name = controllers.name + ' - Copy'
    if group_id: controllers.thread_group_id = group_id
    controllers.operator = username
    controllers.save()
    samples = HTTPSampleProxy.objects.filter(controller_id=controller_id)
    for sample in samples:
        copy_one_sample(controllers.id, sample.id, username, ip)
    logger.info(f'Copy controller {controller_id} success, target controller is {controllers.id}, operator: {username}, IP: {ip}')
