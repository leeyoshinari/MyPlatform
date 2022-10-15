#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import json
import logging
import traceback
from django.shortcuts import render
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from shell.models import Servers, GroupIdentifier, ServerRoom
from common.Email import sendEmail
from common.Result import result
from .server.request import Request
from .server.process import Process
from .server.draw_performance import draw_data_from_db


logger = logging.getLogger('django')

monitor_server = Process()
http = Request()


def home(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            groups = request.user.groups.all()
            servers = Servers.objects.values('host').filter(group__in=groups).order_by('-id')
            agents = monitor_server.get_all_keys()
            datas = [monitor_server.get_value_by_host('Server_' + s['host']) for s in servers if 'Server_' + s['host'] in agents]
            logger.info(f'Get monitor servers list, operator: {username}')
            return render(request, 'monitor/home.html', context={'datas': datas})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def start_monitor(request):
    """
    Start monitoring
    """
    if request.method == 'GET':
        try:
            groups = request.user.groups.all()
            servers = Servers.objects.values('host').filter(group__in=groups).order_by('-id')
            keys = monitor_server.get_all_keys()
            datas = [monitor_server.get_value_by_host('Server_' + s['host']) for s in servers if 'Server_' + s['host'] in keys]
            monitor_list = monitor_server.get_monitor(hosts=datas)
            return render(request, 'monitor/runMonitor.html', context={'ip': datas, 'foos': monitor_list})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def get_monitor(request):
    """
    Get the list of monitoring ports
    """
    if request.method == 'GET':
        ip = request.GET.get('host')
        monitor_list = []
        try:
            port = monitor_server.get_value_by_host('Server_' + ip, 'port')
            post_data = {
                'host': ip,
            }
            res = http.request('post', ip, port, 'getMonitor', json=post_data)
            if res.status_code == 200:
                response = json.loads(res.content.decode())
                logger.debug(f'The return value of server {ip} of getting monitoring list is {response}')
                if response['code'] == 0:
                    for i in range(len(response['data']['port'])):
                        monitor_list.append({
                            'host': response['data']['host'][i],
                            'port': response['data']['port'][i],
                            'pid': response['data']['pid'][i],
                            'isRun': ['stopped', 'monitoring', 'queuing'][response['data']['isRun'][i]],
                            'startTime': response['data']['startTime'][i]})

                    return result(msg='Successful!', data=monitor_list)
                else:   # If an exception is returned, skip
                    logger.warning(f'It returns an exception from server {ip} when getting monitoring list. Exception is {response["msg"]}')
                    return result(code=1, msg=response["msg"])
            else:   # If an exception is returned, skip
                logger.warning(f'The monitoring list from server {ip} is abnormal, the response status code is {res.status_code}.')
                return result(code=1, msg="System exception!")
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg="System exception!")


def visualize(request):
    """
    Visualization
    """
    if request.method == 'GET':
        try:
            username = request.user.username
            spec_host = request.GET.get('host')
            spec_host = spec_host if spec_host else 'all'
            spec_group = request.GET.get('group')
            spec_room = request.GET.get('room')
            starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()-1800))
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            groups = request.user.groups.all()
            if spec_group:
                servers = Servers.objects.values('host', 'room_id').filter(group_id=spec_group).order_by('-id')
            else:
                servers = Servers.objects.values('host', 'room_id').filter(group__in=groups).order_by('-id')
            room_list = [s['room_id'] for s in servers]
            rooms = ServerRoom.objects.values('id', 'name').filter(id__in=set(room_list)).order_by('-id')
            keys = monitor_server.get_all_keys()
            hosts = [monitor_server.get_value_by_host('Server_' + s['host']) for s in servers if 'Server_' + s['host'] in keys]
            if not hosts:
                logger.error(f'You have no servers to view, please check permission ~')
                return render(request, '404.html')
            logger.info(f'Access visualization page, operaotr: {username}')
            return render(request, 'monitor/visualize.html', context={'ip': hosts, 'groups': groups,'rooms': rooms, 'starttime': starttime,
                'endtime': endtime, 'row_name': ['75%', '90%', '95%', '99%'], 'spec_host': spec_host, 'spec_group': spec_group, 'spec_room': spec_room})
        except:
            logger.error(traceback.format_exc())
            return render(request, '404.html')
    else:
        return render(request, '404.html')


def course_zh_CN(request):
    return render(request, 'monitor/course_zh_CN.html', context={})


def course_en(request):
    return render(request, 'monitor/course_en.html', context={})

def register_first(request):
    """
    register
    """
    if request.method == 'POST':
        logger.debug(f'The request parameters are {request.body}')
        datas = json.loads(request.body)
        try:
            servers = Servers.objects.get(host=datas['host'])
            identifier = GroupIdentifier.objects.get(group_id=servers.group_id)
            datas.update({'roomId': servers.room.id, 'groupKey': identifier.key})
            monitor_server.agent_setter(datas)
            return result(msg='registered successfully!', data={'influx': {'host': settings.INFLUX_HOST, 'port': settings.INFLUX_PORT,
                      'username': settings.INFLUX_USER_NAME, 'password': settings.INFLUX_PASSWORD, 'database': settings.INFLUX_DATABASE},
                      'redis': {'host': settings.REDIS_HOST, 'port': settings.REDIS_PORT, 'password': settings.REDIS_PWD,
                       'db': settings.REDIS_DB}, 'roomId': servers.room.id, 'groupKey': identifier.key})
        except Servers.DoesNotExist:
            logger.error(f"Host: {datas['host']} is not set in 'shell->server'")
            return result(code=1, msg=f"Host: {datas['host']} is not set in 'shell->server'")
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Register Error ~')

def registers(request):
    """
    register
    """
    if request.method == 'POST':
        logger.debug(f'The request parameters are {request.body}')
        monitor_server.agent_setter(json.loads(request.body))
        return result(msg='registered successfully!')

def run_monitor(request):
    """
    start/stop monitoring port.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            host = data.get('host')
            port = data.get('port')
            is_run = data.get('isRun')  # Whether to start monitoring，0-stop monitoring, 1-start monitoring
            post_data = {
                'host': host,
                'port': port,
                'isRun': str(is_run)
            }
            port = monitor_server.get_value_by_host('Server_' + host, 'port')
            res = http.request('post', host, port, 'runMonitor', json=post_data)

            if res.status_code == 200:
                return HttpResponse(content=res.content.decode())
            else:
                return result(code=1, msg=f"System exception, the message comes from {host}")

        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='System exception!')


def plot_monitor(request):
    """
    Visualize
    """
    if request.method == 'POST':
        username = request.user.username
        host = request.POST.get('host')
        group_id = request.POST.get('group')
        room_id = request.POST.get('room')
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')
        try:
            group_identifier = GroupIdentifier.objects.values('key').get(group_id=group_id)
            if host == 'all':
                res = draw_data_from_db(room=room_id, group=group_identifier['key'], host=host, startTime=start_time, endTime=end_time)
                if res['code'] == 1:
                    raise Exception(res['message'])
                servers = Servers.objects.filter(group_id=group_id, room_id=room_id)
                server_keys = monitor_server.get_all_keys()
                hosts = [s.host for s in servers if 'Server_' + s.host in server_keys]
                monitor_data = [monitor_server.get_value_by_host('Server_' + host) for host in hosts]
                gc = [d['gc'] for d in monitor_data if d['gc'][0] > -1 and d['gc'][2] > -1]
                if gc:
                    ffgc = [d['ffgc'] for d in monitor_data]
                    gc_data = [sum(r) for r in zip(*gc)]
                    gc_data.append(min(ffgc))
                    res.update({'gc': gc_data})
                else:
                    res['flag'] = 0
                return JsonResponse(res)
            else:
                servers = Servers.objects.filter(group_id=group_id, room_id=room_id, host=host)
                server_dict = monitor_server.get_value_by_host('Server_' + host)
                if servers and server_dict:
                    res = draw_data_from_db(room=room_id, group=group_identifier['key'], host=host, startTime=start_time, endTime=end_time)
                    if res['code'] == 1:
                        raise Exception(res['message'])
                    monitor_data = monitor_server.get_value_by_host('Server_' + host)
                    res.update({'gc': monitor_data['gc']})
                    res['gc'].append(monitor_data['ffgc'])
                    if res['gc'][0] == -1 and res['gc'][2] == -1:
                        res['flag'] = 0
                    return JsonResponse(res)
                else:
                    logger.error(f'Server {host} has not monitored. operator: {username}')
                    return result(code=1, msg=f'Server {host} has not monitored.')
        except Exception as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=str(err))


def get_port_disk(request):
    """
     Get all the disk numbers and all monitored ports of the client.
    """
    if request.method == 'GET':
        host = request.GET.get('host')
        server_info = monitor_server.get_value_by_host('Server_' + host)
        if server_info:
            try:
                disks = server_info['disk']
                monitor_list = [p['port'] for p in monitor_server.get_monitor(hosts=[server_info])]
                return result(msg='Successful!', data={'disk': disks, 'port': monitor_list})
            except:
                logger.error(traceback.format_exc())
                return result(code=1, msg="System Exception")
        else:
            return result(code=1, msg=f"{host} agent may not register.")


def notice(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            emailObj = {
                'smtp': settings.EMAIL_SMTP, 'senderName': settings.EMAIL_SENDER_NAME,
                'senderEmail': settings.EMAIL_SENDER_EMAIL, 'password': settings.EMAIL_PASSWORD,
                'receiverName': settings.EMAIL_RECEIVER_NAME, 'receiverEmail': settings.EMAIL_RECEIVER_EMAIL,
                'msg': data.get('msg'), 'subject': 'Server Monitoring'
            }
            sendEmail(emailObj)
            return result(msg='Send Email Successful!')
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Send Email Failure!')


def change_group(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            groups = request.user.groups.all()
            group_id = request.GET.get('group')
            # if group_id not in groups:
            #     return result(code=1, msg='You have no permission to access this group ~')
            servers = Servers.objects.values('host', 'room_id').filter(group_id=group_id)
            keys = monitor_server.get_all_keys()
            hosts = [monitor_server.get_value_by_host('Server_' + s['host']) for s in servers if 'Server_' + s['host'] in keys]
            hosts.sort(key=lambda x:(-x['cpu_usage'], -x['io_usage'], -x['net_usage'], -x['mem_usage']))
            room_list = [s['room_id'] for s in servers]
            rooms_obj = ServerRoom.objects.values('id', 'name').filter(id__in=set(room_list)).order_by('-id')
            rooms = [{'id': r['id'], 'name': r['name']} for r in rooms_obj]
            logger.info(f'Query all servers and rooms in group {group_id}, operator: {username}')
            return result(msg='Query success ~', data={'hosts': hosts, 'rooms': rooms})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Error, please try later ~')


def change_room(request):
    if request.method == 'GET':
        try:
            username = request.user.username
            group_id = request.GET.get('group')
            room_id = request.GET.get('room')
            servers = Servers.objects.values('host').filter(group_id=group_id, room_id=room_id)
            keys = monitor_server.get_all_keys()
            hosts = [monitor_server.get_value_by_host('Server_' + s['host']) for s in servers if 'Server_' + s['host'] in keys]
            hosts.sort(key=lambda x: (-x['cpu_usage'], -x['io_usage'], -x['net_usage'], -x['mem_usage']))
            logger.info(f'Query all servers in group {group_id} and room {room_id}, operator: {username}')
            return result(msg='Query success ~', data={'hosts': hosts})
        except:
            logger.error(traceback.format_exc())
            return result(code=1, msg='Error, please try later ~')


