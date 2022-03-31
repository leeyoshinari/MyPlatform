#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import logging
import traceback
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User, Group
from common.Result import result


logger = logging.getLogger('django')


def login(request):
    if request.method == 'POST':
        if request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            current_time = request.POST.get('currentTime')
            p = ''
            time_len = len(current_time)
            for i in range(len(password)):
                if i < time_len:
                    p += chr(ord(password[i])^int(current_time[i]))
                else:
                    p += chr(ord(password[i]) ^ int(current_time[i-time_len]))
            ip = request.headers.get('x-real-ip')
            ip = ip if ip else '127.0.0.1'
            session = auth.authenticate(username=username, password=p)
            if session:
                auth.login(request, session)
                request.session.set_expiry(0)
                logger.info(f'{username} login success ~ , ip: {ip}')
                return result(msg='login success ~')
            else:
                logger.error(f'{username} login failure ~ ')
                return result(code=1, msg='login failure ~ ')
        else:
            return result(code=1, msg='UserName or Password Error ~ ')
    else:
        return render(request, 'user/login.html')


def logout(request):
    username = request.user.username
    ip = request.headers.get('x-real-ip')
    ip = ip if ip else '127.0.0.1'
    auth.logout(request)
    logger.info(f'{username} logout success, ip: {ip}')
    return redirect('user:login')
