#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import json
import logging
import traceback
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.core import serializers
from django.db.models import Q
from common.Result import result
from .models import Servers
from .channel.ssh import get_server_info


logger = logging.getLogger('django')


def index(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            servers = Servers.objects.all().order_by('-id')
            groups = Group.objects.all().order_by('-id')
            logger.info(f'access shell index.html. operator: {username}')
            return render(request, 'shell/index.html', context={'servers': json.loads(serializers.serialize('json', servers)),
                                                                'groups': json.loads(serializers.serialize('json', groups))})
        except Exception as err:
            logger.error(err)
            logger.error(traceback.format_exc())
            return result(code=1, msg='access shell index.html failure ~')


def add_server(request):
    if request.method == 'POST':
        try:
            group_id = request.POST.get('GroupName')
            group_name = Group.objects.get(id=group_id)
            server_name = request.POST.get('ServerName')
            server_ip = request.POST.get('ServerIP')
            try:
                Servers.objects.get(host=server_ip)
                logger.info(f'server has been added ~ ')
                return result(code=2, msg='server has been added ~ ')
            except Servers.DoesNotExist:
                pass
            port = request.POST.get('Port')
            sshname = request.POST.get('UserName')
            password = request.POST.get('Password')
            current_time = request.POST.get('time')
            username = request.user.username
            system = ''
            cpu = 0
            mem = 0
            disk = 0

            if password:
                datas = get_server_info(host=server_ip, port = int(port), user = sshname, pwd = password, current_time=current_time)
                if datas['code'] == 0:
                    system = datas['system']
                    cpu = datas['cpu']
                    mem = datas['mem']
                    disk = datas['disk']
                else:
                    return result(code=1, msg=datas['msg'])

            server = Servers.objects.create(id = current_time, group_name = group_name, group_id = group_id, name=server_name,
                                   host=server_ip, port = int(port), user = sshname, pwd = password, system = system,
                                   cpu = cpu, mem = mem, disk = disk, is_monitor=0)
            logger.info(f'Add server success. ip: {server.host}, operator: {username}, time: {server.id}')
            return result(code=0, msg='Add server success ~ ')
        except Exception as err:
            logger.error(f'Add server error. {err}')
            logger.error(traceback.format_exc())
            return result(code=1, msg=err)


def delete_server(request):
    if request.method == 'GET':
        try:
            server_id = request.GET.get('id')
            username = request.user.username
            Servers.objects.get(id=server_id).delete()
            logger.info(f'Delete server success. operator: {username}, server id: {server_id}')
            return result(code=0, msg='Delete server success ~')
        except Exception as err:
            logger.error(err)
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete server failure ~')


def search_server(request):
    if request.method == 'GET':
        try:
            keyword = request.GET.get('keyword')
            keyword = keyword.replace('%', '').replace('+', '').strip()
            if not keyword:
                return result(code=1, msg='Please input KeyWord ~')
            username = request.user.username
            servers = Servers.objects.filter(Q(name__contains=keyword) | Q(host__contains=keyword)).order_by('-id')
            groups = Group.objects.all().order_by('-id')
            logger.info(f'search server success. operator: {username}')
            return render(request, 'shell/index.html', context={'servers': json.loads(serializers.serialize('json', servers)),
                                   'groups': json.loads(serializers.serialize('json', groups))})
        except Exception as err:
            logger.error(err)
            logger.error(traceback.format_exc())
            return result(code=1, msg='search server failure ~')


def openssh(request):
    if request.method == 'GET':
        username = request.user.username
        host = request.GET.get('ip')
        logger.info(f'Open shell. ip: {host}, operator: {username}')
        return render(request,'shell/webssh.html', context={'host': host})
