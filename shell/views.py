#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import json
import logging
import traceback
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import StreamingHttpResponse
from django.core import serializers
from django.db.models import Q
from common.Result import result
from .models import Servers
from .channel.ssh import get_server_info, UploadAndDownloadFile


logger = logging.getLogger('django')
current_path = os.path.abspath(os.path.dirname(__file__))
upload_file_path = os.path.join(current_path, 'uploadFile')
if not os.path.exists(upload_file_path):
    os.mkdir(upload_file_path)


def index(request):
    if request.method == 'GET':
        try:
            user_id = request.user.id
            username = request.user.username
            user = User.objects.get(id=user_id)
            groups = user.groups.all()
            servers = Servers.objects.filter(group__in=groups).order_by('-id')
            logger.info(f'access shell index.html. operator: {username}')
            return render(request, 'shell/index.html', context={'servers': servers, 'groups': groups})
        except Exception as err:
            logger.error(err)
            logger.error(traceback.format_exc())
            return result(code=1, msg='access shell index.html failure ~')


def add_server(request):
    if request.method == 'POST':
        try:
            group_id = request.POST.get('GroupName')
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
            arch = ''
            mem = 0
            disk = 0

            if password:
                datas = get_server_info(host=server_ip, port = int(port), user = sshname, pwd = password, current_time=current_time)
                if datas['code'] == 0:
                    system = datas['system']
                    cpu = datas['cpu']
                    mem = datas['mem']
                    disk = datas['disk']
                    arch = datas['arch']
                else:
                    return result(code=1, msg=datas['msg'])

            server = Servers.objects.create(id = current_time, group_id = group_id, name=server_name,
                                   host=server_ip, port = int(port), user = sshname, pwd = password, system = system,
                                   cpu = cpu, arch=arch, mem = mem, disk = disk, is_monitor=0)
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


def upload_file(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            form = request.FILES['file']
            file_name = form.name
            # file_size = form.size
            # content_type = form.content_type
            data = form.file
            host = request.POST.get('host')
            remote_path = request.POST.get('remotePath').strip()
            index = int(request.POST.get('index'))
            total = int(request.POST.get('total'))
            upload_time = request.POST.get('uploadTime')
            temp_path = os.path.join(upload_file_path, upload_time)
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)
            if index == total:
                with open(os.path.join(temp_path, file_name), 'wb') as f:
                    f.write(data.read())

                remote_path = remote_path if remote_path else '/home'
                allfiles = os.listdir(temp_path)
                server = Servers.objects.get(host=host)
                upload_obj = UploadAndDownloadFile(server)
                for fp in allfiles:
                    _ = upload_obj.upload(os.path.join(temp_path, fp), f'{remote_path}/{fp}')
                    os.remove(os.path.join(temp_path, fp))
                    logger.info(f'{fp} upload success, operator: {username}')
                del upload_obj
                allfiles = os.listdir(temp_path)
                if len(allfiles) == 0:
                    os.rmdir(temp_path)
                    return result(code=0, msg='upload file success ~')
                else:
                    for fp in allfiles:
                        os.remove(os.path.join(temp_path, fp))
                    os.rmdir(temp_path)
                    return result(code=1, msg='upload file failure ~', data=allfiles)
            else:
                with open(os.path.join(temp_path, file_name), 'wb') as f:
                    f.write(data.read())
                return result(code=0, msg='upload file success ~')
        except Exception as err:
            logger.info(err)
            logger.info(traceback.format_exc())
            return result(code=1, msg='upload file failure ~')

def download_file(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            host = request.GET.get('host')
            file_path = request.GET.get('filePath')
            _, file_name = os.path.split(file_path)
            if not file_name:
                logger.error('file path is error ~ ')
                return render(request, '404.html')
            server = Servers.objects.get(host=host)
            upload_obj = UploadAndDownloadFile(server)
            fp = upload_obj.download(file_path)
            response = StreamingHttpResponse(fp)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="{file_name}"'.encode('utf-8')
            del fp, upload_obj
            return response
        except Exception as err:
            del upload_obj
            logger.error(err)
            logger.error(traceback.format_exc())
            return render(request, '404.html')