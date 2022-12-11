#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import json
import logging
import traceback
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from django.conf import settings
from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from common.Result import result
from common.generator import primaryKey
from common.customException import MyException
from .models import Servers, ServerRoom, GroupIdentifier, Packages
from .channel.ssh import get_server_info, UploadAndDownloadFile
from .channel.deployAgent import deploy, stop_deploy, check_deploy_status


logger = logging.getLogger('django')
current_path = os.path.abspath(os.path.dirname(__file__))
upload_file_path = os.path.join(current_path, 'uploadFile')
deploy_path = settings.DEPLOY_PATH
local_file_path = os.path.join(settings.BASE_DIR, 'static', 'autoDeploy')
if not os.path.exists(upload_file_path):
    os.mkdir(upload_file_path)
if not os.path.exists(local_file_path):
    os.mkdir(local_file_path)


def index(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            is_staff = request.user.is_staff
            page = request.GET.get('page')
            page_size = request.GET.get('pageSize')
            page = int(page) if page else 1
            page_size = int(page_size) if page_size else settings.PAGE_SIZE
            groups = request.user.groups.all()
            rooms = ServerRoom.objects.all().order_by('-create_time')
            total_num = Servers.objects.filter(group__in=groups).count()
            servers = Servers.objects.filter(group__in=groups).order_by('-id')[(page - 1) * page_size: page * page_size]
            logger.info(f'access shell index.html. operator: {username}, IP: {ip}')
            return render(request, 'index.html', context={'servers': servers, 'groups': groups, 'page': page,
                                                                'page_size': page_size, 'total_page': (total_num - 1) // page_size + 1,
                                                                'rooms': rooms, 'is_staff': is_staff, 'operator': username})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def add_server(request):
    if request.method == 'POST':
        try:
            ip = request.headers.get('x-real-ip')
            group_id = request.POST.get('GroupName')
            server_name = request.POST.get('ServerName')
            room_id = request.POST.get('ServerRoom')
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

            server = Servers.objects.create(id = current_time, group_id = group_id, name=server_name, room_id=room_id,
                                   host=server_ip, port = int(port), user = sshname, pwd = password, system = system,
                                   cpu = cpu, arch=arch, mem = mem, disk = disk, creator=username, operator=username)
            logger.info(f'Add server success. host: {server.host}, operator: {username}, time: {server.id}, IP:{ip}')
            return result(code=0, msg='Add server success ~ ')
        except Exception as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=err)

def get_server(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            server_id = request.GET.get('id')
            servers = Servers.objects.get(id=server_id)
            server_dict = model_to_dict(servers)
            server_dict.pop('pwd')
            logger.info(f'Get server {servers.host} info success, operator: {username}, IP: {ip}')
            return result(data=server_dict)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get server failure ~')

def edit_server(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            server_id = request.POST.get('ServerId')
            server_ip = request.POST.get('ServerIP')
            servers = Servers.objects.get(id=server_id, host=server_ip)
            servers.group_id = request.POST.get('GroupName')
            servers.name = request.POST.get('ServerName')
            servers.room_id = request.POST.get('ServerRoom')
            servers.port = request.POST.get('Port')
            servers.user = request.POST.get('UserName')
            servers.operator = username
            password = request.POST.get('Password')
            if password:
                servers.pwd = password
            servers.save()
            logger.info(f'Edit server success. host: {servers.host}, operator: {username}, id: {servers.id}, IP: {ip}')
            return result(msg='Edit server success ~ ')
        except Servers.DoesNotExist:
            logger.error(f'Please do not modify server id and host, operator: {username}, IP: {ip}')
            return result(code=1, msg='Please do not modify server id and host ~')
        except Exception as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=err)

def add_user(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            user_name = request.POST.get('UserName')
            group_name = request.POST.get('GroupName')
            operator = request.POST.get('Operator')
            groups = request.user.groups.get(id=group_name)
            users = User.objects.get(username=user_name)
            if operator == 'add':
                users.groups.add(groups.id)
                logger.info(f'add {user_name} to {groups.name} group success, operator: {username}, IP: {ip}')
                return result(msg='Add User success ~')
            else:
                users.groups.remove(groups.id)
                logger.info(f'Remove {user_name} from {groups.name} group success, operator: {username}, IP: {ip}')
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
            ip = request.headers.get('x-real-ip')
            group_name = request.POST.get('GroupName')
            group_id = request.POST.get('GroupId')
            group_key = request.POST.get('GroupKey')
            group_type = request.POST.get('GroupType')
            prefix = request.POST.get('Prefix')
            if group_type == 'add':
                group = Group.objects.create(name=group_name)
                users = User.objects.filter(is_staff=1)
                for user in users:
                    user.groups.add(group.id)
                try:
                    identifier = GroupIdentifier.objects.get(key=group_key)
                    Group.objects.get(id=group.id).delete()
                    logger.error(f"{identifier.key} has existed, operator: {username}, IP: {ip}")
                    return result(code=1, msg=f"{identifier.key} has existed, Group Name is {identifier.group.name}")
                except GroupIdentifier.DoesNotExist:
                    identifier = GroupIdentifier.objects.create(id=primaryKey(), group_id=group.id, key=group_key, prefix=prefix)
            if group_type == 'delete':
                group = Group.objects.get(id=group_id).delete()
            logger.info(f'{group_type} group {group_name} success, operator: {username}, IP: {ip}')
            return result(msg='Create group success ~')
        except ProtectedError:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Cannot delete Group because it is referenced')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='System error ~')


def create_room(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            room_name = request.POST.get('roomName')
            room_type = request.POST.get('roomType')
            operate_type = request.POST.get('operateType')
            room_id = request.POST.get('roomId')
            if operate_type == 'add':
                try:
                    _ = ServerRoom.objects.get(name=room_name, type=room_type)
                    return result(msg='Server room has been created ~')
                except ServerRoom.DoesNotExist:
                    room = ServerRoom.objects.create(id=primaryKey(), name=room_name, type=room_type, operator=username)
            if operate_type == 'delete':
                room = ServerRoom.objects.get(id=room_id).delete()
            logger.info(f'{operate_type} server room {room_name} success, operator: {username}, IP: {ip}')
            return result(msg='Create server room success ~')
        except ProtectedError:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Cannot delete Server Room because it is referenced')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='System error ~')


def delete_server(request):
    if request.method == 'GET':
        try:
            ip = request.headers.get('x-real-ip')
            server_id = request.GET.get('id')
            username = request.user.username
            groups = request.user.groups.all()
            Servers.objects.filter(Q(id=server_id), Q(group__in=groups)).delete()
            logger.info(f'Delete server success. operator: {username}, server id: {server_id}, IP: {ip}')
            return result(code=0, msg='Delete server success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete server failure ~')

def delete_package(request):
    if request.method == 'GET':
        try:
            ip = request.headers.get('x-real-ip')
            package_id = request.GET.get('id')
            username = request.user.username
            package = Packages.objects.get(id=package_id)
            os.remove(package.path)
            package.delete()
            logger.info(f'Delete server success. operator: {username}, package id: {package.id}, package name: {package.name}, IP: {ip}')
            return result(code=0, msg='Delete package success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Delete package failure ~')

def search_server(request):
    if request.method == 'GET':
        try:
            ip = request.headers.get('x-real-ip')
            group_name = request.GET.get('group')
            server_name = request.GET.get('server')
            server_room = request.GET.get('room')
            group_name = group_name.replace('%', '').replace('+', '').strip()
            server_name = server_name.replace('%', '').replace('+', '').strip()
            if not group_name and not server_name and not server_room:
                return redirect('shell:index')

            if group_name:
                groups = request.user.groups.filter(name__contains=group_name)
            else:
                groups = request.user.groups.all()

            if server_name and server_room:
                servers = Servers.objects.filter(group__in=groups, room__name__contains=server_room).filter(Q(name__contains=server_name) | Q(host__contains=server_name)).order_by('-id')
            elif server_room:
                servers = Servers.objects.filter(group__in=groups, room__name__contains=server_room).order_by('-id')
            elif server_name:
                servers = Servers.objects.filter(group__in=groups).filter(Q(name__contains=server_name) | Q(host__contains=server_name)).order_by('-id')
            else:
                servers = Servers.objects.filter(group__in=groups).order_by('-id')
            username = request.user.username
            is_staff = request.user.is_staff
            rooms = ServerRoom.objects.all().order_by('-create_time')
            logger.info(f'search server success. operator: {username}, IP: {ip}')
            return render(request, 'index.html', context={'servers': servers, 'groups': groups, 'page': 0, 'rooms': rooms,
                                                                'is_staff': is_staff, 'page_size': 200, 'total_page': 0})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def openssh(request):
    if request.method == 'GET':
        username = request.user.username
        ip = request.headers.get('x-real-ip')
        groups = request.user.groups.all()
        host = request.GET.get('ip')
        if Servers.objects.filter(Q(host=host), Q(group__in=groups)).exists():
            logger.info(f'Open shell. host: {host}, operator: {username}, IP: {ip}')
            return render(request, 'webssh.html', context={'host': host})
        else:
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def upload_file(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
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
                    logger.info(f'{fp} upload success, operator: {username}, IP: {ip}')
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
            logger.error(traceback.format_exc())
            return result(code=1, msg='upload file failure ~')

def download_file(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            host = request.GET.get('host')
            file_path = request.GET.get('filePath')
            _, file_name = os.path.split(file_path)
            if not file_name:
                logger.error(f'file path is error, operator: {username}, IP: {ip}')
                return render(request, '404.html')
            server = Servers.objects.get(host=host)
            upload_obj = UploadAndDownloadFile(server)
            fp = upload_obj.download(file_path)
            response = StreamingHttpResponse(fp)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="{file_name}"'.encode('utf-8')
            del fp, upload_obj
            logger.info(f'{file_path} download success, operator: {username}, IP: {ip}')
            return response
        except:
            del upload_obj
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')

def deploy_package(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            groups = request.user.groups.all()
            host = request.POST.get('host')
            package_id = request.POST.get('id')
            servers = Servers.objects.get(host=host, group__in=groups)
            package = Packages.objects.get(id=package_id)
            if package.type == 'collector-agent':
                address = f"{request.POST.get('address')}/{settings.PREFIX}"
            else:
                address = settings.COLLECTOR_AGENT_ADDRESS
            if not os.path.exists(package.path):
                return result(code=1, msg=f'{package.name} is not exist ~')
            deploy(host = servers.host, port = servers.port, user = servers.user, pwd = servers.pwd, deploy_path=deploy_path,
                   current_time = servers.id, local_path=package.path, file_name=package.name, package_type=package.type, address=address)
            logger.info(f'Deploy {package.name} success, operator: {username}, IP: {ip}')
            return result(msg=f'Deploy {package.name} success ~')
        except Servers.DoesNotExist:
            logger.error(f'You have no permission to access {host}, operator: {username}, IP: {ip}')
            return result(code=1, msg=f'You have no permission to access {host} ~')
        except MyException as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=err.msg)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Deploy failure ~ ')
    else:
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            groups = request.user.groups.all()
            host = request.GET.get('host')
            package_id = request.GET.get('id')
            servers = Servers.objects.get(host=host, group__in=groups)
            package = Packages.objects.get(id=package_id)
            check_deploy_status(host=servers.host, port=servers.port, user=servers.user, pwd=servers.pwd,
                                deploy_path=deploy_path, current_time=servers.id, package_type=package.type)
            logger.info(f'Deploy {package.name} success, operator: {username}, IP: {ip}')
            return result(msg=f'Deploy {package.name} success ~')
        except MyException as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=err.msg)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Deploy failure ~ ')


def uninstall_deploy(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            groups = request.user.groups.all()
            host = request.GET.get('host')
            package_id = request.GET.get('id')
            servers = Servers.objects.get(host=host, group__in=groups)
            package = Packages.objects.get(id=package_id)
            stop_deploy(host=servers.host, port=servers.port, user=servers.user, pwd=servers.pwd,
                        current_time=servers.id, package_type=package.type, deploy_path=deploy_path)
            logger.info(f'Uninstall success, operator: {username}, IP: {ip}')
            return result(msg='Uninstall success ~')
        except Servers.DoesNotExist:
            logger.error(f'You have no permission to access {host}, operator: {username}, IP: {ip}')
            return result(code=1, msg=f'You have no permission to access {host} ~')
        except MyException as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=err.msg)
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Uninstall failure, please try again ~ ')


def get_all_group(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            groups = Group.objects.all().order_by('-id')
            logger.info(f'Get All Groups success, operator: {username}, IP: {ip}')
            return result(data=json.loads(serializers.serialize('json', groups)))
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get Groups error ~')


def get_all_room(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            rooms = ServerRoom.objects.all().order_by('-create_time')
            logger.info(f'Get All Groups success, operator: {username}, IP: {ip}')
            return result(data=json.loads(serializers.serialize('json', rooms)))
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Get Groups error ~')

def package_home(request):
    if request.method == 'GET':
        username = request.user.username
        ip = request.headers.get('x-real-ip')
        groups = request.user.groups.all()
        host = request.GET.get('ip')
        try:
            if host:
                servers = Servers.objects.get(host=host, group__in=groups)
                packages = Packages.objects.all().order_by('-create_time')
                logger.info(f'Query package list success, operator: {username}, IP: {ip}')
                return render(request, 'packages.html', context={'servers': servers, 'packages': packages})
            else:
                packages = Packages.objects.all().order_by('-create_time')
                logger.info(f'Query package list success, operator: {username}, IP: {ip}')
                return render(request, 'packages.html', context={'packages': packages})
        except Servers.DoesNotExist:
            logger.error(f'You have no permission to access {host}, operator: {username}, IP: {ip}')
            return render(request, '404.html', context={'msg': f'You have no permission to access {host} ~'})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')


def package_upload(request):
    if request.method == 'POST':
        try:
            username = request.user.username
            ip = request.headers.get('x-real-ip')
            form = request.FILES['file']
            file_name = form.name
            # file_size = form.size
            # content_type = form.content_type
            if 'zip' not in file_name and 'tar.gz' not in file_name:
                logger.error(f'File {file_name} format is not supported, operator: {username}, IP: {ip}')
                return result(code=1, msg='File format is not supported ~')
            data = form.file
            system = request.POST.get('system')
            agent_type = request.POST.get('agent_type')
            arch = request.POST.get('arch')
            file_path = os.path.join(local_file_path, file_name)
            if os.path.exists(file_path):
                logger.error(f'File {file_name} is existed, operator: {username}, IP: {ip}')
                return result(code=1, msg=f'File {file_name} is existed ~')
            with open(file_path, 'wb') as f:
                f.write(data.read())
            Packages.objects.create(id=primaryKey(), name=file_name, path=file_path, system=system, arch=arch, type=agent_type, operator=username)
            logger.info(f'File {file_name} upload success, operator: {username}, IP: {ip}')
            return result(code=0, msg='upload file success ~')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='upload file failure ~')
