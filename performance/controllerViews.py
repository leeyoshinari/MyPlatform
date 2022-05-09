#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import logging
import traceback
from django.shortcuts import render, redirect
from .models import ThreadGroup, TransactionController
from common.Result import result
from common.generator import primaryKey
# Create your views here.


logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            group_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 20
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and group_id:
                total_page = TransactionController.objects.filter(thread_group_id=group_id, name__contains=key_word).count()
                controllers = TransactionController.objects.filter(thread_group_id=group_id, name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif group_id and not key_word:
                total_page = TransactionController.objects.filter(thread_group_id=group_id).count()
                controllers = TransactionController.objects.filter(thread_group_id=group_id).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif key_word and not group_id:
                total_page = TransactionController.objects.filter(name__contains=key_word).count()
                controllers = TransactionController.objects.filter(name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = TransactionController.objects.all().count()
                controllers = TransactionController.objects.all().order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get controller success, operator: {username}')
            return render(request, 'performance/controller/home.html', context={'controllers': controllers, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'group_id': group_id, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get controller failure ~')


def add_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            name = request.POST.get('name')
            group_id = request.POST.get('group_id')
            comment = request.POST.get('comment')
            controller = TransactionController.objects.create(id=primaryKey(), name=name, comment=comment, is_valid='true',
                          thread_group_id=group_id, operator=username)
            logger.info(f'Controller {name} {controller.id} is save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        group_id = request.GET.get('id')
        group_id = int(group_id) if group_id else group_id
        groups = ThreadGroup.objects.all().order_by('-update_time')
        return render(request, 'performance/controller/add.html', context={'group_id': group_id, 'groups': groups})

def edit_group(request):
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


def copy_controller(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            controller_id = request.GET.get('id')
            controllers = TransactionController.objects.get(id=controller_id)
            controllers.id = primaryKey()
            controllers.name = controllers.name + ' - Copy'
            controllers.operator = username
            controllers.save()
            logger.info(f'Copy controller {controller_id} success, target controller is {controllers.id}, operator: {username}')
            return redirect('perf:controller_home')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy controller Failure ~')

