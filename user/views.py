#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import logging
import traceback
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.conf import settings
from common.Result import result


logger = logging.getLogger('django')


def login(request):
    if request.method == 'POST':
        if request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            current_time = request.POST.get('currentTime')
            p = parse_pwd(password, current_time)
            ip = request.headers.get('x-real-ip')
            session = auth.authenticate(username=username, password=p)
            if session:
                auth.login(request, session)
                request.session.set_expiry(0)
                logger.info(f'{username} login success ~ , ip: {ip}')
                return result(msg='login success ~')
            else:
                logger.error(f'UserName or Password Error, operator: {username}, ip: {ip}')
                return result(code=1, msg='UserName or Password Error ~ ')
        else:
            return result(code=1, msg='login failure ~ ')
    else:
        return render(request, 'login.html')


def logout(request):
    username = request.user.username
    ip = request.headers.get('x-real-ip')
    ip = ip if ip else '127.0.0.1'
    auth.logout(request)
    logger.info(f'{username} logout success, ip: {ip}')
    return redirect('user:login')


def change_pwd(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            old_pwd = request.POST.get('old_password')
            new_pwd = request.POST.get('new_password')
            current_time = request.POST.get('current_time')
            p = parse_pwd(old_pwd, current_time)
            ip = request.headers.get('x-real-ip')
            session = auth.authenticate(username=username, password=p)
            if session:
                user = User.objects.get(username=username)
                user.set_password(parse_pwd(new_pwd, current_time))
                user.save()
                logger.info(f'{username} change password success ~ , ip: {ip}')
                return result(msg='Change password success ~')
            else:
                logger.error(f'UserName or Password Error, operator: {username}, ip: {ip}')
                return result(code=1, msg='UserName or Password Error ~ ')
        except:
            logger.error(traceback.format_exc())
            return  result(code=1, msg='Change password error ~')
    else:
        return render(request, 'password.html')


def parse_pwd(password: str, s: str):
    p = ''
    time_len = len(s)
    for i in range(len(password)):
        if i < time_len:
            p += chr(ord(password[i]) ^ int(s[i]))
        else:
            p += chr(ord(password[i]) ^ int(s[i - time_len]))
    return p


def home(request):
    if request.method == 'GET':
        username = request.user.username
        ip = request.headers.get('x-real-ip')
        is_staff = request.user.is_staff
        logger.info(f'Access Home Page success, operator: {username}, ip: {ip}')
        return render(request, 'home.html', context={'username': username, 'is_monitor': settings.IS_MONITOR,
                                                     'isATIJMeter': settings.IS_ATIJMETER, 'is_staff': is_staff,
                                                     'is_perf': settings.IS_PERF, 'is_nginx': settings.IS_NGINX})
    else:
        return render(request, '404.html')


def course(request):
    if request.method == 'GET':
        lang = request.GET.get('_lang')
        if lang == 'zh':
            return render(request, 'course_zh.html')
        else:
            return render(request, 'course_en.html')
    else:
        return render(request, '404.html')


def register_first(request):
    if request.method == 'POST':
        ip = request.headers.get('x-real-ip')
        value = request.body.decode()
        data = json.loads(value)
        logger.info(f"Agent: {data['host']}:{data['port']} registers successfully, ip: {ip}")
        return result(msg='Agent registers successfully ~',data={'influx': {'host': settings.INFLUX_HOST, 'port': settings.INFLUX_PORT,
                      'username': settings.INFLUX_USER_NAME, 'password': settings.INFLUX_PASSWORD, 'database': settings.INFLUX_DATABASE},
                      'redis': {'host': settings.REDIS_HOST, 'port': settings.REDIS_PORT, 'password': settings.REDIS_PWD,
                       'db': settings.REDIS_DB}, 'key_expire': settings.PERFORMANCE_EXPIRE, 'deploy_path': settings.DEPLOY_PATH})
