#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.conf import settings
from django.shortcuts import render, redirect, resolve_url
from .models import HTTPRequestHeader, HTTPSampleProxy, TransactionController
from common.Result import result
from common.generator import primaryKey
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
            ip = request.headers.get('x-real-ip')
            groups = request.user.groups.all().values('id')
            ctl_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and ctl_id:
                total_page = HTTPSampleProxy.objects.filter(controller_id=ctl_id, name__contains=key_word).count()
                samples = HTTPSampleProxy.objects.filter(controller_id=ctl_id, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif ctl_id and not key_word:
                total_page = HTTPSampleProxy.objects.filter(controller_id=ctl_id).count()
                samples = HTTPSampleProxy.objects.filter(controller_id=ctl_id).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif key_word and not ctl_id:
                total_page = HTTPSampleProxy.objects.filter(group__in=groups, name__contains=key_word).count()
                samples = HTTPSampleProxy.objects.filter(group__in=groups, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = HTTPSampleProxy.objects.filter(group__in=groups).count()
                samples = HTTPSampleProxy.objects.filter(group__in=groups).order_by('-create_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get http samples success, operator: {username}, IP: {ip}')
            return render(request, 'httpSample/home.html', context={'samples': samples, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'controller_id': ctl_id, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def get_from_header(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            groups = request.user.groups.all().values('id')
            header_id = request.GET.get('id')
            page_size = request.GET.get('pageSize')
            page = request.GET.get('page')
            key_word = request.GET.get('keyWord')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            key_word = key_word.replace('%', '').strip() if key_word else ''
            if key_word and header_id:
                total_page = HTTPSampleProxy.objects.filter(http_header_id=header_id, group__in=groups, name__contains=key_word).count()
                samples = HTTPSampleProxy.objects.filter(http_header_id=header_id, group__in=groups, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif header_id and not key_word:
                total_page = HTTPSampleProxy.objects.filter(http_header_id=header_id, group__in=groups).count()
                samples = HTTPSampleProxy.objects.filter(http_header_id=header_id, group__in=groups).order_by('-create_time')[page_size * (page - 1): page_size * page]
            elif key_word and not header_id:
                total_page = HTTPSampleProxy.objects.filter(group__in=groups, name__contains=key_word).count()
                samples = HTTPSampleProxy.objects.filter(group__in=groups, name__contains=key_word).order_by('-create_time')[page_size * (page - 1): page_size * page]
            else:
                total_page = HTTPSampleProxy.objects.filter(group__in=groups).count()
                samples = HTTPSampleProxy.objects.filter(group__in=groups).order_by('-create_time')[page_size * (page - 1): page_size * page]

            logger.info(f'Get http samples success, operator: {username}, IP: {ip}')
            return render(request, 'httpSample/home.html', context={'samples': samples, 'page': page, 'page_size': page_size,
                                                                     'key_word': key_word, 'header_id': header_id, 'total_page': (total_page + page_size - 1) // page_size})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def add_sample(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
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
            group = TransactionController.objects.values('group').get(id = controller_id)
            sample = HTTPSampleProxy.objects.create(id=primaryKey(), name=name, protocol=protocol, comment=comment, is_valid='true',
                          domain=domain, port=port, path=path, method=method, http_header_id=http_header, assert_type=assertion_type,
                          assert_content=assertion_string, argument=argument, extractor=extractor, controller_id=controller_id,
                          contentEncoding=contentEncoding, group=group['group'], operator=username)
            logger.info(f'Http Sample {name} {sample.id} is save success, operator: {username}, IP: {ip}')
            return result(msg='Save success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Save failure ~')
    else:
        try:
            ctl_id = request.GET.get('id')
            if ctl_id:
                group = TransactionController.objects.values('group').get(id=ctl_id)
                controllers = TransactionController.objects.filter(group=group['group']).order_by('-id')
            else:
                groups = request.user.groups.all().values('id')
                controllers = TransactionController.objects.filter(group__in=groups).order_by('-create_time')
            http_headers = HTTPRequestHeader.objects.filter(method='GET').order_by('-create_time')
            return render(request, 'httpSample/add.html', context={
                'controller_id': ctl_id, 'controllers': controllers, 'protocols': protocols, 'http_headers': http_headers,
                'methods': methods, 'assertion_types': assertion_types, 'contentEncodings': contentEncodings, 'data_types': data_types
            })
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')

def edit_sample(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
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
            group = TransactionController.objects.values('group').get(id=controller_id)
            samples = HTTPSampleProxy.objects.get(id=sample_id)
            samples.name = name
            samples.controller_id = controller_id
            samples.group = group['group']
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
            samples.operator = username
            samples.save()
            logger.info(f'HTTP Sample {sample_id} is edit success, operator: {username}, IP: {ip}')
            return result(msg='Edit success ~')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Edit failure ~')
    else:
        try:
            sample_id = request.GET.get('id')
            samples = HTTPSampleProxy.objects.get(id=sample_id)
            controllers = TransactionController.objects.filter(group=samples.controller.group).order_by('-create_time')
            http_headers = HTTPRequestHeader.objects.filter(method=samples.method).order_by('-create_time')
            return render(request, 'httpSample/edit.html', context={
                'controllers': controllers, 'samples': samples, 'protocols': protocols, 'methods': methods, 'http_headers': http_headers,
                'assertion_types': assertion_types, 'contentEncodings': contentEncodings, 'data_types': data_types})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')


def copy_sample(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            sample_id = request.GET.get('id')
            controller_id = request.GET.get('controller_id')
            copy_one_sample(controller_id, sample_id, username, ip)
            return redirect(resolve_url('perf:sample_home') + '?id=' + controller_id)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Copy HTTP Sample Failure ~')

def get_header_by_method(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            method = request.GET.get('method')
            headers = HTTPRequestHeader.objects.values('id', 'name').filter(method=method).order_by('-id')
            if headers:
                logger.info(f'Get headers success, operator: {username}, IP: {ip}')
                return result(msg='Get headers success ~', data=list(headers))
            else:
                return result(code=1, msg=f'Method {method} has no headers, pls set it firstly ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get headers error ~')

def copy_one_sample(controller_id, sample_id, username, ip):
    samples = HTTPSampleProxy.objects.get(id=sample_id)
    samples.id = primaryKey()
    samples.name = samples.name + ' - Copy'
    if controller_id: samples.controller_id = controller_id
    samples.operator = username
    samples.save()
    logger.info(f'Copy HTTP Sample {sample_id} success, target HTTP Sample is {samples.id}, operator: {username}, IP: {ip}')
