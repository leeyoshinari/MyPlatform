#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.shortcuts import render
from .models import HTTPRequestHeader
from common.Result import result
from common.generator import primaryKey, strfTime
# Create your views here.


logger = logging.getLogger('django')
methods = {'GET': 'GET', 'POST': 'POST', 'HEAD': 'HEAD', 'PUT': 'PUT', 'OPTIONS': 'OPTIONS', 'DELETE': 'DELETE', 'TRACE': 'TRACE'}


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
                headers = HTTPRequestHeader.objects.filter(name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                headers = HTTPRequestHeader.objects.all().order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get controller success, operator: {username}')
            return render(request, 'performance/header/home.html', context={'headers': headers, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get controller failure ~')


def add_header(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            data = json.loads(request.body)
            name = data.get('name')
            method = data.get('method')
            header = data.get('header')
            comment = data.get('comment')
            headers = HTTPRequestHeader.objects.create(id=primaryKey(), name=name, comment=comment, method=method,
                          value=header, create_time=strfTime(), update_time=strfTime(), operator=username)
            logger.info(f'HTTP request header {name} {headers.id} is save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        return render(request, 'performance/header/add.html', context={'methods':methods})

def edit_header(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            data = json.loads(request.body)
            header_id = data.get('id')
            name = data.get('name')
            method = data.get('method')
            header = data.get('header')
            comment = data.get('comment')
            headers = HTTPRequestHeader.objects.get(id=header_id)
            headers.name = name
            headers.method = method
            headers.value = header
            headers.comment = comment
            headers.update_time = strfTime()
            headers.operator = username
            headers.save()
            logger.info(f'HTTP request header {header_id} is edit success, operator: {username}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        header_id = request.GET.get('id')
        headers = HTTPRequestHeader.objects.get(id=header_id)
        return render(request, 'performance/header/edit.html', context={'methods':methods, 'headers': headers})
