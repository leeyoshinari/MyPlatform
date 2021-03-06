#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import logging
import traceback
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models import Q
from common.Result import result
from .models import Servers
from .channel.ssh import get_server_info, UploadAndDownloadFile, deploy_mon, stop_mon


logger = logging.getLogger('django')
current_path = os.path.abspath(os.path.dirname(__file__))
upload_file_path = os.path.join(current_path, 'uploadFile')
if not os.path.exists(upload_file_path):
    os.mkdir(upload_file_path)


def index(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            page = request.GET.get('page')
            page_size = request.GET.get('pageSize')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else 20
            groups = request.user.groups.all()
            total_num = Servers.objects.filter(group__in=groups).count()
            servers = Servers.objects.filter(group__in=groups).order_by('-id')[(page - 1) * page_size: page * page_size]
            logger.info(f'access shell index.html. operator: {username}')
            return render(request, 'shell/index.html', context={'servers': servers, 'groups': groups, 'page': page, 'isMonitor': settings.IS_MONITOR,
                                                                'page_size': page_size, 'total_page': (total_num - 1) // page_size + 1})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Access shell index.html failure ~')


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
            logger.error(traceback.format_exc())
            return result(code=1, msg=err)


def add_user(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            user_name = request.POST.get('UserName')
            group_name = request.POST.get('GroupName')
            operator = request.POST.get('Operator')
            groups = request.user.groups.get(id=group_name)
            users = User.objects.get(username=user_name)
            if operator == 'add':
                users.groups.add(groups.id)
                logger.info(f'add {user_name} to {groups.name} group success, operator: {username}')
                return result(msg='Add User success ~')
            else:
                users.groups.remove(groups.id)
                logger.info(f'Remove {user_name} from {groups.name} group success, operator: {username}')
                return result(msg='Remove User success ~')
        except User.DoesNotExist:
            logger.error(traceback.format_exc())
            return result(code=1, msg='User is not exist ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='System error ~')


def create_group(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            group_name = request.POST.get('GroupName')
            group = Group.objects.create(name=group_name)
            users = User.objects.filter(is_staff=1)
            for user in users:
                user.groups.add(group.id)
            logger.info(f'create group {group_name} success, operator: {username}')
            return result(msg='Create group success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='System error ~')


def delete_server(request):
    if request.method == 'GET':
        try:
            server_id = request.GET.get('id')
            username = request.user.username
            groups = request.user.groups.all()
            Servers.objects.filter(Q(id=server_id), Q(group__in=groups)).delete()
            logger.info(f'Delete server success. operator: {username}, server id: {server_id}')
            return result(code=0, msg='Delete server success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete server failure ~')


def search_server(request):
    if request.method == 'GET':
        try:
            group_name = request.GET.get('group')
            server_name = request.GET.get('server')
            group_name = group_name.replace('%', '').replace('+', '').strip()
            server_name = server_name.replace('%', '').replace('+', '').strip()
            if not group_name and not server_name:
                return redirect('shell:index')

            if group_name:
                groups = request.user.groups.filter(name__contains=group_name)
            else:
                groups = request.user.groups.all()

            if server_name:
                servers = Servers.objects.filter(group__in=groups).filter(Q(name__contains=server_name) | Q(host__contains=server_name)).order_by('-id')
            else:
                servers = Servers.objects.filter(group__in=groups).order_by('-id')
            username = request.user.username
            is_staff = request.user.is_staff
            logger.info(f'search server success. operator: {username}')
            return render(request, 'shell/index.html', context={'servers': servers, 'groups': groups, 'page': 0, 'isMonitor': settings.IS_MONITOR,
                                                                'is_staff': is_staff, 'page_size': 200, 'total_page': 0})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')


def openssh(request):
    if request.method == 'GET':
        username = request.user.username
        groups = request.user.groups.all()
        host = request.GET.get('ip')
        if Servers.objects.filter(Q(host=host), Q(group__in=groups)).exists():
            logger.info(f'Open shell. ip: {host}, operator: {username}')
            return render(request,'shell/webssh.html', context={'host': host})
        else:
            return render(request, '404.html')
    else:
        return render(request, '404.html')


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
        except:
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
            logger.info(f'{file_path} download success, operator: {username}')
            return response
        except:
            del upload_obj
            logger.error(traceback.format_exc())
            return render(request, '404.html')

def deploy_monitor(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            host = request.GET.get('host')
            servers = Servers.objects.get(Q(host=host), Q(is_monitor=0))
            local_file = f"{servers.system.split(' ')[0].strip().lower()}_{servers.arch.strip().lower()}_agent.zip"
            local_file_path = os.path.join('monitor','agent', local_file)
            if not os.path.exists(local_file_path):
                return result(code=1, msg=f'{local_file} is not exist ~')
            res = deploy_mon(host = servers.host, port = servers.port, user = servers.user, pwd = servers.pwd,
                             current_time = servers.id, local_path=local_file_path, file_name=local_file)
            if res['code'] > 0:
                return result(code=1, msg=res['msg'])
            else:
                servers.is_monitor = 1
                servers.save()
                logger.info(f'deploy monitor success, file: {local_file_path}, operator: {username}')
                return result(msg='deploy monitor success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='deploy monitor failure ~ ')


def stop_monitor(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            host = request.GET.get('host')
            servers = Servers.objects.get(Q(host=host), Q(is_monitor=1))
            res = stop_mon(host=servers.host, port=servers.port, user=servers.user, pwd=servers.pwd,
                             current_time=servers.id)
            if res['code'] > 0:
                return result(code=1, msg=res['msg'])
            else:
                servers.is_monitor = 0
                servers.save()
                logger.info(f'stop monitor success, operator: {username}')
                return result(msg='stop monitor success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='stop monitor failure, please try again ~ ')
