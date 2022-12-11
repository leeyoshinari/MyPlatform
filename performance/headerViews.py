#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.conf import settings
from django.shortcuts import render, redirect
from .models import HTTPRequestHeader
from common.Result import result
from common.generator import primaryKey
# Create your views here.


logger = logging.getLogger('django')
methods = {'GET': 'GET', 'POST': 'POST', 'HEAD': 'HEAD', 'PUT': 'PUT', 'OPTIONS': 'OPTIONS', 'DELETE': 'DELETE', 'TRACE': 'TRACE'}


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word:
                total_page = HTTPRequestHeader.objects.filter(name__contains=key_word).count()
                headers = HTTPRequestHeader.objects.filter(name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = HTTPRequestHeader.objects.all().count()
                headers = HTTPRequestHeader.objects.all().order_by('-create_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get controller success, operator: {username}, IP: {ip}')
            return render(request, 'header/home.html', context={'headers': headers, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def add_header(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            data = json.loads(request.body)
            name = data.get('name')
            method = data.get('method')
            header = data.get('header')
            comment = data.get('comment')
            headers = HTTPRequestHeader.objects.create(id=primaryKey(), name=name, comment=comment, method=method,
                          value=header, operator=username)
            logger.info(f'HTTP request header {name} {headers.id} is save success, operator: {username}, IP: {ip}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        return render(request, 'header/add.html', context={'methods':methods})

def edit_header(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
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
            headers.operator = username
            headers.save()
            logger.info(f'HTTP request header {header_id} is edit success, operator: {username}, IP: {ip}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        header_id = request.GET.get('id')
        headers = HTTPRequestHeader.objects.get(id=header_id)
        return render(request, 'header/edit.html', context={'methods':methods, 'headers': headers})


def copy_header(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            header_id = request.GET.get('id')
            headers = HTTPRequestHeader.objects.get(id=header_id)
            headers.id = primaryKey()
            headers.name = headers.name + ' - Copy'
            headers.operator = username
            headers.save()
            logger.info(f'Copy HTTP Header {header_id} success, target HTTP Header is {headers.id}, operator: {username}, IP: {ip}')
            return redirect('perf:header_home')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy HTTP Header Failure ~')
