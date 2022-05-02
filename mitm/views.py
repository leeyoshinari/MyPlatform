#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import json
import logging
import traceback
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
from .models import Mitm
from common.Result import result

# Create your views here.
logger = logging.getLogger('django')
if settings.IS_MITMPROXY == 1:
    import redis
    r  = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PWD,
                     db=settings.REDIS_DB, decode_responses=True)


def home(request):
    if request.method == 'GET':
        username = request.user.username
        datas = Mitm.objects.all().order_by('-update_time')
        logger.info(f'Get rule list success, operator: {username}')
        return render(request, 'mitm/home.html', context={'datas': datas,
                                                          'types': ["直接拦截请求", "篡改请求或响应", "篡改响应值", "请求响应都篡改"]})

def course(request):
    if request.method == 'GET':
        return render(request, 'mitm/course.html')

def save(request):
    try:
        if request.method == 'POST':
            if request.POST.get('method') != '0':
                if not isinstance(json.loads(request.POST.get('fields')), dict):
                    raise Exception('篡改字段的值不是合法的Json')
            username = request.user.username
            name = request.POST.get('name')
            domain_name = request.POST.get('domain_name')
            url_path = request.POST.get('url_path')
            method = request.POST.get('method')
            is_re = request.POST.get('is_re')
            status_code = request.POST.get('status_code') if method == '0' else -1
            response = request.POST.get('response') if method == '0' else request.POST.get('fields')
            is_file = request.POST.get('is_file') if method == '0' else -1

            res = Mitm.objects.create(id=int(time.time() * 1000), name=name, domain=domain_name, url_path=url_path,
                                      status_code=status_code, method=method, response=response, is_regular=is_re,
                                      is_file=is_file, is_valid=1, creator=username, modifier=username,
                                      update_time=time.strftime('%Y-%m-%d %H:%M:%S'))
            logger.info(f'{res.id} save success, operator: {username}')
            return result(msg='Save success ~')
    except json.JSONDecodeError:
        logger.error(traceback.format_exc())
        return result(code=1, msg='篡改字段的值不是合法的Json ~')
    except:
        logger.error(traceback.format_exc())
        return result(code=1, msg='Save failure ~')

def update(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ID = request.POST.get('ID')
            name = request.POST.get('name')
            domain_name = request.POST.get('domain_name')
            url_path = request.POST.get('url_path')
            is_re = request.POST.get('is_re')
            method = request.POST.get('method')
            status_code = request.POST.get('status_code') if method == '0' else -1
            response = request.POST.get('response') if method == '0' else request.POST.get('fields')
            is_file = request.POST.get('is_file') if method == '0' else -1

            mitm = Mitm.objects.get(id=ID)
            mitm.name = name
            mitm.domain = domain_name
            mitm.url_path = url_path
            mitm.is_regular = is_re
            mitm.method = method
            mitm.status_code = status_code
            mitm.response = response
            mitm.is_file = is_file
            mitm.modifier = username
            mitm.update_time = time.strftime('%Y-%m-%d %H:%M:%S')
            mitm.save()
            logger.info(f'Update rule {ID} success, operator: {username}')
            return result(msg=f'Update rule {ID} success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg=f'Update rule failure ~')


def isRun(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ID = request.POST.get('Id')
            is_run = request.POST.get('isRun')
            mitm = Mitm.objects.get(id=ID)
            mitm.is_valid = is_run
            mitm.modifier = username
            mitm.update_time = time.strftime('%Y-%m-%d %H:%M:%S')
            mitm.save()
            logger.info(f'Rule {ID} status is set to {is_run}, operator: {username}')
            return result(msg='Operate success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Operate failure ~ ')

def delete(request, rule_id):
    if request.method == 'GET':
        try:
            username = request.user.username
            Mitm.objects.get(id=rule_id).delete()
            logger.info(f'Mitm rule {rule_id} is deleted success, operator: {username}')
            return result(msg='Delete rule success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete rule failure ~')

def edit(request, rule_id):
    if request.method == 'GET':
        try:
            username = request.user.username
            mitm = Mitm.objects.get(id=rule_id)
            logger.info(f'edit: get rule {rule_id} success, operator: {username}')
            return result(msg='Get rule success ~', data=json.loads(serializers.serialize('json', [mitm]))[-1])
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Operate Failure ~ ')

def reload(request):
    try:
        username = request.user.username
        mitm = Mitm.objects.filter(is_valid=1).order_by('-update_time')
        if r.get('mitmproxy'):
            return result(code=1, msg='The last active is invalid ~')
        r.set('mitmproxy', serializers.serialize('json', mitm), nx=True)
        logger.info(f'All rule are actived success, operator: {username}')
        return result(msg='All rule are actived success ~')
    except:
        logger.error(traceback.format_exc())
        return result(code=1, msg='Active failure ~')
