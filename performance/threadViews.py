#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import json
import logging
import traceback
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from .models import TestPlan, ThreadGroup, TransactionController
from common.Result import result
from common.generator import primaryKey
import common.Request as Request
# Create your views here.


logger = logging.getLogger('django')
share_mode = {'All threads': 'shareMode.all','Current thread group': 'shareMode.group', 'Current thread': 'shareMode.thread'}


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            plan_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 20
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and plan_id:
                total_page = ThreadGroup.objects.filter(plan_id=plan_id, name__contains=key_word).count()
                groups = ThreadGroup.objects.filter(plan_id=plan_id, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif plan_id and not key_word:
                total_page = ThreadGroup.objects.filter(plan_id=plan_id).count()
                groups = ThreadGroup.objects.filter(plan_id=plan_id).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif key_word and not plan_id:
                total_page = ThreadGroup.objects.filter(name__contains=key_word).count()
                groups = ThreadGroup.objects.filter(name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = ThreadGroup.objects.all().count()
                groups = ThreadGroup.objects.all().order_by('-create_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get thread group success, operator: {username}')
            return render(request, 'performance/threadGroup/home.html', context={'groups': groups, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'plan_id': plan_id, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get test plan failure ~')


def add_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            name = request.POST.get('name')
            plan_id = request.POST.get('plan_id')
            # num_threads = request.POST.get('num_threads')
            ramp_time = request.POST.get('ramp_time')
            # scheduler = request.POST.get('scheduler')
            duration = request.POST.get('duration')
            duration = duration if duration else None
            comment = request.POST.get('comment')
            file_path = request.POST.get('file_path')
            if file_path:
                file_dict = {
                    'file_path': file_path,
                    'variable_names': request.POST.get('variable_names'),
                    'delimiter': request.POST.get('delimiter'),
                    'recycle': request.POST.get('recycle'),
                    'share_mode': request.POST.get('share_mode')}
            else:
                file_dict = None
            group = ThreadGroup.objects.create(id=primaryKey(), name=name, ramp_time=ramp_time,
                                duration=duration, comment=comment, is_valid='true', plan_id=plan_id,
                                file=file_dict, operator=username)
            logger.info(f'Thread Group {name} {group.id} is save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        plan_id = request.GET.get('id')
        plan_id = int(plan_id) if plan_id else plan_id
        plans = TestPlan.objects.all().order_by('-create_time')
        return render(request, 'performance/threadGroup/add.html', context={'plan_id': plan_id, 'plans': plans, 'share_mode': share_mode})


def edit_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            group_id = request.POST.get('id')
            name = request.POST.get('name')
            plan_id = request.POST.get('plan_id')
            # num_threads = request.POST.get('num_threads')
            ramp_time = request.POST.get('ramp_time')
            # scheduler = request.POST.get('scheduler')
            duration = request.POST.get('duration')
            duration = duration if duration else None
            comment = request.POST.get('comment')
            file_path = request.POST.get('file_path')
            if file_path:
                file_dict = {
                    'file_path': file_path,
                    'variable_names': request.POST.get('variable_names'),
                    'delimiter': request.POST.get('delimiter'),
                    'recycle': request.POST.get('recycle'),
                    'share_mode': request.POST.get('share_mode')}
            else:
                file_dict = None
            groups = ThreadGroup.objects.get(id=group_id)
            groups.name = name
            groups.plan_id = plan_id
            groups.ramp_time = ramp_time
            groups.duration = duration
            groups.comment = comment
            groups.file = file_dict
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
        plans = TestPlan.objects.all().order_by('-create_time')
        return render(request, 'performance/threadGroup/edit.html', context={'groups': groups, 'plans': plans, 'share_mode': share_mode})


def upload_file(request):
    if request.method == 'POST':
        form = request.FILES['file']
        file_name = form.name
        plan_id = request.POST.get('plan_id')
        try:
            if settings.FILE_STORE_TYPE == '0':
                file_folder = os.path.join(settings.FILE_ROOT_PATH, plan_id)
                if not os.path.exists(file_folder):
                    os.mkdir(file_folder)
                file_path = os.path.join(file_folder, file_name)
                with open(file_path, 'wb') as f:
                    f.write(form.file.read())
            return result(msg=f'{file_name} Upload Success ~', data=f'{settings.FILE_URL}{settings.STATIC_URL}files/{plan_id}/{file_name}')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'{file_name} Upload Failure ~', data=file_name)


def edit_cookie(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            cookies = data.get('cookies')
            group = ThreadGroup.objects.get(id=plan_id)
            group.cookie = cookies
            group.operator = username
            group.save()
            logger.info(f'Thread Group {group.name} {group.id} cookies is save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        try:
            username = request.user.username
            group_id = request.GET.get('id')
            cookies = ThreadGroup.objects.get(id=group_id)
            logger.info(f'Get thread group cookies success, operator: {username}')
            return render(request, 'performance/threadGroup/cookie.html', context={'cookies': cookies})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get cookies failure ~')


def copy_group(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            group_id = request.GET.get('id')
            plan_id = request.GET.get('plan_id')
            groups = ThreadGroup.objects.get(id=group_id)
            groups.id = primaryKey()
            groups.name = groups.name + ' - Copy'
            if plan_id: groups.plan_id = plan_id
            groups.operator = username
            groups.save()
            controllers = TransactionController.objects.filter(thread_group_id=group_id)
            for controller in controllers:
                res = Request.get(request.headers.get('Host'), f'{resolve_url("perf:controller_copy")}?id={controller.id}&group_id={groups.id}', cookies=request.headers.get('cookie'))
            logger.info(f'Copy thread group {group_id} success, target thread group is {groups.id}, operator: {username}')
            return redirect(resolve_url('perf:group_home') + '?id=' + plan_id)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy thread group Failure ~')
