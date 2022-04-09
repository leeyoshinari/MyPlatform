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
from shell.models import Servers
from common.Email import sendEmail
from common.Result import result
from .server.request import Request
from .server.process import Process
from .server.draw_performance import draw_data_from_db
# from .server.draw_performance1 import draw_data_from_db


logger = logging.getLogger('django')
monitor_server = Process()
http = Request()


def home(request):
    if request.method == 'GET':
        try:
            groups = request.user.groups.all()
            servers = Servers.objects.values('host').filter(Q(is_monitor=0), Q(group__in=groups)).order_by('-id')
            datas = []
            for i in range(len(servers)):
                ind = monitor_server.agents['ip'].index(servers[i]['host']) if servers[i]['host'] in monitor_server.agents['ip'] else -1
                if ind == -1:
                    continue
                else:
                    datas.append({'ip': monitor_server.agents['ip'][ind],
                                  'port': monitor_server.agents['port'][ind],
                                  'system': monitor_server.agents['system'][ind],
                                  'cpu': monitor_server.agents['cpu'][ind],
                                  'mem': monitor_server.agents['mem'][ind],
                                  'disk': monitor_server.agents['disk_size'][ind],
                                  'net': monitor_server.agents['network_speed'][ind],
                                  'cpu_usage': monitor_server.agents['cpu_usage'][ind],
                                  'mem_usage': monitor_server.agents['mem_usage'][ind] * 100,
                                  'disk_usage': monitor_server.agents['disk_usage'][ind] * 100})
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
            servers = Servers.objects.values('host').filter(Q(is_monitor=0), Q(group__in=groups)).order_by('-id')
            datas = []
            for i in range(len(servers)):
                ind = monitor_server.agents['ip'].index(servers[i]['host']) if servers[i]['host'] in monitor_server.agents['ip'] else -1
                if ind == -1:
                    continue
                else:
                    datas.append(monitor_server.agents['ip'][ind])
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
            port = monitor_server.agents['port'][monitor_server.agents['ip'].index(ip)]
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
                    logger.warning(f'It returns an exception from server {ip} when getting monitoring list. '
                                   f'Exception is {response["msg"]}')
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
    starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()-600))
    endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    groups = request.user.groups.all()
    servers = Servers.objects.values('host').filter(Q(is_monitor=1), Q(group__in=groups)).order_by('-id')
    hosts = []
    disks = []
    for i in range(len(servers)):
        ind = monitor_server.agents['ip'].index(servers[i]['host'])
        if ind == -1:
            continue
        else:
            hosts.append(monitor_server.agents['ip'][ind])
            disks.append(monitor_server.agents['disk'][ind])

    if hosts:
        monitor_list = monitor_server.get_monitor(hosts=hosts[0])
        ports = [mon['port'] for mon in monitor_list]
    else:
        ports = []
    return render(request, 'monitor/visualize.html', context={'disks': disks, 'ip': hosts, 'port': ports, 'starttime': starttime,
        'endtime': endtime, 'row_name': ['75%', '90%', '95%', '99%']})


def course_zh_CN(request):
    return render(request, 'monitor/course_zh_CN.html', context={})


def course_en(request):
    return render(request, 'monitor/course_en.html', context={})

def registers(request):
    """
    register
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        logger.debug(f'The request parameters are {data}')
        monitor_server.agents = data
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
            ind = monitor_server.agents['ip'].index(host)
            res = http.request('post', host, monitor_server.agents['port'][ind], 'runMonitor', json=post_data)

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
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        type_ = data.get('type')
        port_pid = data.get('port')
        disk = data.get('disk')
        if host in monitor_server.agents['ip']:
            try:
                if type_ == 'port':
                    res = draw_data_from_db(host=host, port=port_pid, startTime=start_time, endTime=end_time, disk=disk)
                    if res['code'] == 0:
                        raise Exception(res['message'])
                    res.update({'gc': monitor_server.get_gc(host, monitor_server.agents['port'][monitor_server.agents['ip'].index(host)],
                                                    f'getGC/{port_pid}')})
                    if res['gc'][0] == -1 and res['gc'][2] == -1:
                        res['flag'] = 0
                    return JsonResponse(res)

                if type_ == 'system':
                    res = draw_data_from_db(host=host, startTime=start_time, endTime=end_time, system=1, disk=disk)
                    if res['code'] == 0:
                        raise Exception(res['message'])
                    res['flag'] = 0
                    return JsonResponse(res)

            except Exception as err:
                logger.error(traceback.format_exc())
                return result(code=1, msg=str(err))
        else:
            logger.error(f'{host} agent may not register.')
            return result(code=1, msg=f'{host} agent may not register.')


def get_port_disk(request):
    """
     Get all the disk numbers and all monitored ports of the client.
    """
    if request.method == 'GET':
        host = request.GET.get('host')
        if host in monitor_server.agents['ip']:
            try:
                disks = monitor_server.agents['disk'][monitor_server.agents['ip'].index(host)]
                monitor_list = monitor_server.get_monitor(hosts=[host])
                return result(msg='Successful!', data={'disk': disks, 'port': monitor_list['port']})
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