#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari
import time
import json
import logging
import traceback
import threading
import influxdb
from .request import Request
from django.conf import settings


logger = logging.getLogger('django')


class Process(object):
    def __init__(self):
        self.request = Request()
        self._agents = {'ip': [], 'port': [], 'system': [], 'cpu': [], 'mem': [], 'time': [], 'disk': [], 'nic': [],
                        'network_speed': [], 'disk_size': [], 'mem_usage': [], 'cpu_usage': [], 'disk_usage': []}

        # data expiration time
        # conn = influxdb.InfluxDBClient(settings.INFLUX_HOST, settings.INFLUX_PORT, settings.INFLUX_USER_NAME,
        #                                settings.INFLUX_PASSWORD, settings.INFLUX_DATABASE)
        # conn.query(f'alter retention policy "autogen" on "{settings.INFLUX_DATABASE}" duration '
        #            f'{settings.INFLUX_EXPIRY_TIME}d REPLICATION 1 SHARD DURATION {settings.INFLUX_SHARD_DURATION} default;')
        logger.info(f'InfuxDb data expiration time is {settings.INFLUX_EXPIRY_TIME} days')

        t = threading.Thread(target=self.check_status, args=())  # Check the online status of the clients.
        t.start()

    @property
    def agents(self):
        return self._agents

    @agents.setter
    def agents(self, value):
        logger.debug(f'The client registration data is {value}')
        ip = value['host']
        if ip in self._agents['ip']:
            ind = self._agents['ip'].index(ip)
            self._agents['cpu_usage'][ind] = value['cpu_usage']
            self._agents['mem_usage'][ind] = value['mem_usage']
            self._agents['disk_usage'][ind] = value['disk_usage']
            self._agents['time'][ind] = time.time()
            logger.info(f'{ip} server has been registered.')
        else:
            self._agents['ip'].append(value['host'])
            self._agents['port'].append(value['port'])
            self._agents['system'].append(value['system'])
            self._agents['cpu'].append(value['cpu'])
            self._agents['mem'].append(value['mem'])
            self._agents['time'].append(time.time())
            self._agents['disk'].append(value['disks'].split(','))
            self._agents['nic'].append(value['nic'])
            self._agents['disk_size'].append(value['disk_size'])
            self._agents['network_speed'].append(value['network_speed'])
            self._agents['cpu_usage'].append((value['cpu_usage']))
            self._agents['mem_usage'].append((value['mem_usage']))
            self._agents['disk_usage'].append((value['disk_usage']))
            logger.info(f'{ip} server registered successfully!')

    def check_status(self):
        """
         Check the online status of the clients, and remove it when offline.
        :return:
        """
        while True:
            time.sleep(5)
            for i in range(len(self._agents['ip'])):
                if time.time() - self._agents['time'][i] < 12:
                    ip = self._agents['ip'].pop(i)
                    self._agents['port'].pop(i)
                    self._agents['system'].pop(i)
                    self._agents['cpu'].pop(i)
                    self._agents['mem'].pop(i)
                    self._agents['time'].pop(i)
                    self._agents['disk'].pop(i)
                    self._agents['nic'].pop(i)
                    self._agents['network_speed'].pop(i)
                    self._agents['disk_size'].pop(i)
                    self._agents['cpu_usage'].pop(i)
                    self._agents['mem_usage'].pop(i)
                    self._agents['disk_usage'].pop(i)
                    logger.warning(f"The client server {ip} is in an abnormal state, and has been offline.")
                    break

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
                        'host': host,
                    }
                    port = self._agents['port'][self._agents['ip'].index(host)]
                    res = self.request.request('post', host, port, 'getMonitor', json=post_data)
                    if res.status_code == 200:
                        response = json.loads(res.content.decode())
                        logger.debug(f'The return value of server {host} of getting monitoring list is {response}.')
                        if response['code'] == 0:
                            for i in range(len(response['data']['port'])):
                                monitor_list.append({
                                    'host': response['data']['host'][i],
                                    'port': response['data']['port'][i],
                                    'pid': response['data']['pid'][i],
                                    'isRun': ['stopped', 'monitoring', 'queuing'][response['data']['isRun'][i]],
                                    'startTime': response['data']['startTime'][i]})
            else:
                for ip, port in zip(self._agents['ip'], self._agents['port']):  # Traverse all clients IP addresses
                    post_data = {
                        'host': ip,
                    }
                    try:
                        res = self.request.request('post', ip, port, 'getMonitor', json=post_data)
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
