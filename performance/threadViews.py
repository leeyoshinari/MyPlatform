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
from .views import delete_file_from_disk
from .controllerViews import copy_one_controller
from common.Result import result
from common.generator import primaryKey
# Create your views here.


logger = logging.getLogger('django')
share_mode = {'All threads': 'shareMode.all','Current thread group': 'shareMode.group', 'Current thread': 'shareMode.thread'}


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            my_groups = request.user.groups.all().values('id')
            plan_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and plan_id:
                total_page = ThreadGroup.objects.filter(plan_id=plan_id, name__contains=key_word).count()
                groups = ThreadGroup.objects.filter(plan_id=plan_id, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif plan_id and not key_word:
                total_page = ThreadGroup.objects.filter(plan_id=plan_id).count()
                groups = ThreadGroup.objects.filter(plan_id=plan_id).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif key_word and not plan_id:
                total_page = ThreadGroup.objects.filter(group__in=my_groups, name__contains=key_word).count()
                groups = ThreadGroup.objects.filter(group__in=my_groups, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = ThreadGroup.objects.filter(group__in=my_groups).count()
                groups = ThreadGroup.objects.filter(group__in=my_groups).order_by('-create_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get thread group success, operator: {username}, IP: {ip}')
            return render(request, 'threadGroup/home.html', context={'groups': groups, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'plan_id': plan_id, 'total_page': (total_page + page_size - 1) // page_size})
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
            plan_id = request.POST.get('plan_id')
            ramp_time = request.POST.get('ramp_time')
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
            plan = TestPlan.objects.values('group_id').get(id=plan_id)
            group = ThreadGroup.objects.create(id=primaryKey(), name=name, ramp_time=ramp_time, comment=comment, group=plan['group_id'],
                                               is_valid='true', plan_id=plan_id, file=file_dict, operator=username)
            logger.info(f'Thread Group {name} {group.id} is save success, operator: {username}, IP: {ip}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        try:
            plan_id = request.GET.get('id')
            if plan_id:
                group = TestPlan.objects.values('group').get(id=plan_id)
                plans = TestPlan.objects.filter(group_id=group['group'], is_file=0).order_by('-create_time')
            else:
                groups = request.user.groups.all()
                plans = TestPlan.objects.filter(group__in=groups, is_file=0).order_by('-create_time')
            return render(request, 'threadGroup/add.html', context={'plan_id': plan_id, 'plans': plans, 'share_mode': share_mode})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')


def edit_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            group_id = request.POST.get('id')
            name = request.POST.get('name')
            plan_id = request.POST.get('plan_id')
            ramp_time = request.POST.get('ramp_time')
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
            plan = TestPlan.objects.values('group_id').get(id=plan_id)
            groups = ThreadGroup.objects.get(id=group_id)
            groups.name = name
            groups.plan_id = plan_id
            groups.group = plan['group_id']
            groups.ramp_time = ramp_time
            groups.comment = comment
            groups.file = file_dict
            groups.operator = username
            groups.save()
            logger.info(f'Thread Group {group_id} is edit success, operator: {username}, IP: {ip}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            group_id = request.GET.get('id')
            groups = ThreadGroup.objects.get(id=group_id)
            plans = TestPlan.objects.filter(group_id=groups.plan.group_id, is_file=0).order_by('-create_time')
            logger.info(f'Open threadGroup edit page success, group: {group_id}, operator: {username}, IP: {ip}')
            return render(request, 'threadGroup/edit.html', context={'groups': groups, 'plans': plans, 'share_mode': share_mode})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')


def upload_file(request):
    if request.method == 'POST':
        username = request.user.username
        ip = request.headers.get('x-real-ip')
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
                file_url = f'{settings.FILE_URL}{settings.STATIC_URL}files/{plan_id}/{file_name}'
            else:
                res = settings.MINIO_CLIENT.upload_file_bytes(file_name, form.file, form.size)
                file_url = f'{settings.FILE_URL}{res.bucket_name}/{res.object_name}'
            logger.info(f'Upload file success, filename: {file_name}, operator: {username}, IP: {ip}')
            return result(msg=f'{file_name} Upload Success ~', data=file_url)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'{file_name} Upload Failure ~', data=file_name)


def delete_file(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            group_id = request.POST.get('group_id')
            file_path = request.POST.get('file_path')
            delete_file_from_disk(file_path)
            if group_id:
                group = ThreadGroup.objects.get(id=group_id)
                group.file = None
                group.save()
            logger.info(f'Delete file {file_path} success, operator: {username}, IP: {ip}')
            return result(msg='Delete file success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete file failure ~')


def edit_cookie(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            data = json.loads(request.body)
            plan_id = data.get('plan_id')
            cookies = data.get('cookies')
            group = ThreadGroup.objects.get(id=plan_id)
            group.cookie = cookies
            group.operator = username
            group.save()
            logger.info(f'Thread Group {group.name} {group.id} cookies is save success, operator: {username}, IP: {ip}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            group_id = request.GET.get('id')
            cookies = ThreadGroup.objects.get(id=group_id)
            logger.info(f'Get thread group cookies success, operator: {username}, IP: {ip}')
            return render(request, 'threadGroup/cookie.html', context={'cookies': cookies})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')


def copy_group(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            group_id = request.GET.get('id')
            plan_id = request.GET.get('plan_id')
            copy_one_group(plan_id, group_id, username, ip)
            return redirect(resolve_url('perf:group_home') + '?id=' + plan_id)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy thread group Failure ~')


def copy_one_group(plan_id, group_id, username, ip):
    groups = ThreadGroup.objects.get(id=group_id)
    groups.id = primaryKey()
    groups.name = groups.name + ' - Copy'
    if plan_id: groups.plan_id = plan_id
    groups.operator = username
    groups.save()
    controllers = TransactionController.objects.filter(thread_group_id=group_id)
    for controller in controllers:
        copy_one_controller(groups.id, controller.id, username, ip)
    logger.info(f'Copy thread group {group_id} success, target thread group is {groups.id}, operator: {username}, IP: {ip}')
