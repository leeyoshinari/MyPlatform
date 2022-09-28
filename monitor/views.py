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
from shell.models import Servers, GroupIdentifier
from common.Email import sendEmail
from common.Result import result
from .server.request import Request
from .server.process import Process


logger = logging.getLogger('django')

if settings.IS_MONITOR == 1:
    from .server.draw_performance import draw_data_from_db
    # from .server.draw_performance1 import draw_data_from_db
    monitor_server = Process()
    http = Request()


def home(request):
    if request.method == 'GET':
        try:
            groups = request.user.groups.all()
            servers = Servers.objects.values('host').filter(Q(is_monitor=1), Q(group__in=groups)).order_by('-id')
            agents = monitor_server.get_all_keys()
            datas = []
            for i in range(len(servers)):
                if 'server_' + servers[i]['host'] in agents:
                    datas.append(monitor_server.get_value_by_host('server_' + servers[i]['host']))
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
            servers = Servers.objects.values('host').filter(Q(is_monitor=1), Q(group__in=groups)).order_by('-id')
            keys = monitor_server.get_all_keys()
            datas = []
            for i in range(len(servers)):
                if 'server_' + servers[i]['host'] in keys:
                    datas.append(monitor_server.get_value_by_host('server_' + servers[i]['host']))
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
            port = monitor_server.get_value_by_host('server_' + ip, 'port')
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
            spec_host = request.GET.get('host')
            starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()-600))
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            groups = request.user.groups.all()
            servers = Servers.objects.values('host').filter(Q(is_monitor=1), Q(group__in=groups)).order_by('-id')
            keys = monitor_server.get_all_keys()
            hosts = []
            for i in range(len(servers)):
                if 'server_' + servers[i]['host'] in keys:
                    hosts.append(monitor_server.get_value_by_host('server_' + servers[i]['host']))

            if hosts:
                monitor_list = monitor_server.get_monitor(hosts=[hosts[0]])
                ports = [mon['port'] for mon in monitor_list]
            else:
                ports = []
            return render(request, 'monitor/visualize.html', context={'ip': hosts, 'port': ports, 'starttime': starttime,
                'endtime': endtime, 'row_name': ['75%', '90%', '95%', '99%'], 'spec': spec_host})
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
            return result(msg='registered successfully!', data={'host': settings.INFLUX_HOST, 'port': settings.INFLUX_PORT,
                                        'username': settings.INFLUX_USER_NAME, 'password': settings.INFLUX_PASSWORD,
                                        'database': settings.INFLUX_DATABASE, 'roomId': servers.room.id, 'groupKey': identifier.key})
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
        monitor_server.agent_setter(request.body)
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
            port = monitor_server.get_value_by_host('server_' + host, 'port')
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
        data = json.loads(request.body)
        host = data.get('host')
        room_id = data.get('roomId')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        type_ = data.get('type')
        port_pid = data.get('port')
        disk = data.get('disk')
        try:
            if host:
                servers = Servers.objects.filter(room_id=room_id, host=host)
                server_dict = monitor_server.get_value_by_host('Server_' + host)
                if servers and server_dict:
                    hosts = [host]
                else:
                    hosts = []
            else:
                servers = Servers.objects.filter(room_id=room_id)
                server_keys = monitor_server.get_all_keys()
                hosts = [s.host for s in servers if 'Server_' + s.host in server_keys]
            if hosts:
                if type_ == 'port':
                    res = draw_data_from_db(roomId=room_id, host=hosts, port=port_pid, startTime=start_time, endTime=end_time, disk=disk)
                    if res['code'] == 0:
                        raise Exception(res['message'])
                    res.update({'gc': monitor_server.get_gc(hosts, hosts['port'], f'getGC/{port_pid}')})
                    if res['gc'][0] == -1 and res['gc'][2] == -1:
                        res['flag'] = 0
                    return JsonResponse(res)

                if type_ == 'system':
                    res = draw_data_from_db(roomId=room_id, host=hosts, startTime=start_time, endTime=end_time, system=1, disk=disk)
                    if res['code'] == 0:
                        raise Exception(res['message'])
                    res['flag'] = 0
                    return JsonResponse(res)
            else:
                logger.error(f'Server room {room_id} has no registered agents.')
                return result(code=1, msg=f'Server room {room_id} has no registered agents.')

        except Exception as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=str(err))


def get_port_disk(request):
    """
     Get all the disk numbers and all monitored ports of the client.
    """
    if request.method == 'GET':
        host = request.GET.get('host')
        server_info = monitor_server.get_value_by_host('server_' + host)
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
        except Exception as err:
            logger.error(traceback.format_exc())
            return result(code=1, msg=err)