#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari
import json
import logging
import traceback
from .request import Request
from django.conf import settings


logger = logging.getLogger('django')


class Process(object):
    def __init__(self):
        self.request = Request()
        # self._agents = {'host': [], 'port': [], 'system': [], 'cpu': [], 'mem': [], 'time': [], 'disk': [], 'nic': [],
        #                 'network_speed': [], 'disk_size': [], 'mem_usage': [], 'cpu_usage': [], 'disk_usage': []}

    def agent_setter(self, value):
        logger.debug(f'The client registration data is {value}')
        key = 'Server_' + value['host']
        settings.REDIS.set(key, json.dumps(value, ensure_ascii=False), ex=settings.HEARTBEAT)
        logger.info(f'Monitor {key} server registered successfully!')

    def get_gc(self, ip, port, interface):
        """
        Get GC data of port
        :param ip: clent IP
        :param port: client monitoring port
        :param interface: interface
        :return:
        """
        try:
            res = self.request.request('get', ip, port, interface)
            if res.status_code == 200:
                response = json.loads(res.content.decode())
                logger.debug(f'The GC data of the port {port} of the server {ip} is {response}')
                if response['code'] == 0:
                    return response['data']
                else:
                    logger.error(response['msg'])
                    return [-1, -1, -1, -1, '-', -1]
            else:
                logger.error(f'The response status code of getting GC data of the '
                             f'port {port} of the server {ip} is {res.status_code}.')
                return [-1, -1, -1, -1, '-', -1]
        except:
            logger.error(traceback.format_exc())
            return [-1, -1, -1, -1, '-', -1]

    def get_monitor(self, hosts=None):
        """
         Get the list of monitoring ports.
        :return:
        """
        monitor_list = []
        try:
            if hosts:
                for host in hosts:
                    post_data = {
                        'host': host['host'],
                    }
                    res = self.request.request('post', host['host'], host['port'], 'getMonitor', json=post_data)
                    if res.status_code == 200:
                        response = json.loads(res.content.decode())
                        logger.debug(f'The return value of server {host["host"]} of getting monitoring list is {response}.')
                        if response['code'] == 0:
                            for i in range(len(response['data']['port'])):
                                monitor_list.append({
                                    'host': response['data']['host'][i],
                                    'port': response['data']['port'][i],
                                    'pid': response['data']['pid'][i],
                                    'isRun': ['stopped', 'monitoring', 'queuing'][response['data']['isRun'][i]],
                                    'startTime': response['data']['startTime'][i]})
            else:
                keys = self.get_all_keys()
                for key in keys:  # Traverse all clients IP addresses
                    ip = key.split('_')[-1]
                    post_data = {
                        'host': ip,
                    }
                    try:
                        res = self.request.request('post', ip, self.get_value_by_host(key, 'port'), 'getMonitor', json=post_data)
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
                    except Exception as err:
                        logger.error(err)
                        continue
        except:
            logger.error(traceback.format_exc())

        return monitor_list

    def get_value_by_host(self, host_key, k=None):
        try:
            server_dict = json.loads(settings.REDIS.get(host_key))
            if k:
                return server_dict[k]
            else:
                return server_dict
        except:
            logger.error(traceback.format_exc())
            return None

    def get_all_host(self):
        agents = []
        try:
            keys = settings.REDIS.keys('Server_*')
            for key in keys:
                agents.append(json.loads(settings.REDIS.get(key)))
        except:
            logger.error(traceback.format_exc())
        return agents

    def get_all_keys(self):
        return settings.REDIS.keys('Server_*')