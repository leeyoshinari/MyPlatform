#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import json
import logging
import traceback
from django.shortcuts import render
from .models import Mitm
from common.Result import result

# Create your views here.
logger = logging.getLogger('django')


def home(request):
    if request.method == 'GET':
        datas = Mitm.objects.all().order_by('-update_time')
        logger.info(datas.values())
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
            status_code = request.POST.get('status_code') if method == '0' else None
            response = request.POST.get('response') if method == '0' else request.POST.get('fields')
            is_file = request.POST.get('is_file') if method == '0' else 'null'

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

def isRun(request):
    if request.method == 'POST':
        try:
            ID = request.POST.get('Id')
            is_run = request.POST.get('isRun')
            logger.info(f'{ID} 设置为 {is_run}')
        except:
            return

def delete(request, rule_id):
    if request.method == 'GET':
        try:
            Mitm.objects.get(id=rule_id).delete()
            logger.info(f'Mitm rule {rule_id} is deleted success ~ ')
            return result(msg='Delete rule success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete rule failure ~')
