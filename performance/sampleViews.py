#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.shortcuts import render
from .models import TestPlan, GlobalVariable, ThreadGroup, TransactionController
from .models import HTTPRequestHeader, HTTPSampleProxy, PerformanceTestTask
from common.Result import result
from common.generator import primaryKey, strfTime
# Create your views here.


logger = logging.getLogger('django')
protocols = {'HTTP': 'HTTP', 'HTTPS': 'HTTPS'}
methods = {'GET': 'GET', 'POST': 'POST', 'HEAD': 'HEAD', 'PUT': 'PUT', 'OPTIONS': 'OPTIONS', 'DELETE': 'DELETE', 'TRACE': 'TRACE'}
assertion_types = {'Contain': 2, 'Equal': 8, 'Match': 1}
contentEncodings = {'None': '', 'UTF-8': 'UTF-8'}
data_types = {'Json Data': 'json', 'Form Data': 'form'}


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


def get_from_header(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            header_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 15
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and header_id:
                samples = HTTPSampleProxy.objects.filter(http_header_id=header_id, name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif header_id and not key_word:
                samples = HTTPSampleProxy.objects.filter(http_header_id=header_id).order_by('-update_time')[page_size * (page - 1): page_size * page]
            elif key_word and not header_id:
                samples = HTTPSampleProxy.objects.filter(name__contains=key_word).order_by('-update_time')[page_size * (page - 1): page_size * page]
            else:
                samples = HTTPSampleProxy.objects.all().order_by('-update_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get http samples success, operator: {username}')
            return render(request, 'performance/httpSample/home.html', context={'samples': samples, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'header_id': header_id})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get controller failure ~')


def add_sample(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            data = json.loads(request.body)
            name = data.get('name')
            controller_id = data.get('controller_id')
            protocol = data.get('protocol')
            contentEncoding = data.get('contentEncoding')
            domain = data.get('domain')
            port = data.get('port')
            path = data.get('path')
            method = data.get('method')
            http_header = data.get('http_header')
            assertion_type = data.get('assertion_type')
            assertion_string = data.get('assertion_string')
            argument = data.get('argument')
            extractor = data.get('extractor')
            comment = data.get('comment')
            sample = HTTPSampleProxy.objects.create(id=primaryKey(), name=name, protocol=protocol, comment=comment, is_valid='true',
                          domain=domain, port=port, path=path, method=method, http_header_id=http_header, assert_type=assertion_type,
                          assert_content=assertion_string, argument=argument, extractor=extractor, controller_id=controller_id,
                          contentEncoding=contentEncoding, create_time=strfTime(), update_time=strfTime(), operator=username)
            logger.info(f'Http Sample {name} {sample.id} is save success, operator: {username}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        ctl_id = request.GET.get('id')
        ctl_id = int(ctl_id) if ctl_id else ctl_id
        controllers = TransactionController.objects.all().order_by('-update_time')
        http_headers = HTTPRequestHeader.objects.all().order_by('-update_time')
        return render(request, 'performance/httpSample/add.html', context={
            'controller_id': ctl_id, 'controllers': controllers, 'protocols': protocols, 'http_headers': http_headers,
            'methods': methods, 'assertion_types': assertion_types, 'contentEncodings': contentEncodings, 'data_types': data_types
        })

def edit_sample(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            data = json.loads(request.body)
            sample_id = data.get('sample_id')
            name = data.get('name')
            controller_id = data.get('controller_id')
            protocol = data.get('protocol')
            contentEncoding = data.get('contentEncoding')
            domain = data.get('domain')
            port = data.get('port')
            path = data.get('path')
            method = data.get('method')
            http_header = data.get('http_header')
            assertion_type = data.get('assertion_type')
            assertion_string = data.get('assertion_string')
            argument = data.get('argument')
            extractor = data.get('extractor')
            comment = data.get('comment')
            samples = HTTPSampleProxy.objects.get(id=sample_id)
            samples.name = name
            samples.controller_id = controller_id
            samples.protocol = protocol
            samples.contentEncoding = contentEncoding
            samples.domain = domain
            samples.port = port
            samples.path = path
            samples.method = method
            samples.http_header_id = http_header
            samples.assert_type = assertion_type
            samples.assert_content = assertion_string
            samples.argument = argument
            samples.extractor = extractor
            samples.comment = comment
            samples.update_time = strfTime()
            samples.operator = username
            samples.save()
            logger.info(f'HTTP Sample {sample_id} is edit success, operator: {username}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        sample_id = request.GET.get('id')
        samples = HTTPSampleProxy.objects.get(id=sample_id)
        controllers = TransactionController.objects.all().order_by('-update_time')
        http_headers = HTTPRequestHeader.objects.all().order_by('-update_time')
        return render(request, 'performance/httpSample/edit.html', context={
            'controllers': controllers, 'samples': samples, 'protocols': protocols, 'methods': methods, 'http_headers': http_headers,
            'assertion_types': assertion_types, 'contentEncodings': contentEncodings, 'data_types': data_types})
