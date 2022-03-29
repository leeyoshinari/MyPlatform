#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import time
import json
import logging
import traceback
from threading import Thread
from shell.models import Servers
from channels.generic.websocket import WebsocketConsumer
from .ssh import SSH

logger = logging.getLogger('django')


class WebSSH(WebsocketConsumer):
    message = {'code': 0, 'msg': None}
    """
    code:
        0: ssh 连接正常, websocket 正常
        1: 发生未知错误, 关闭 ssh 和 websocket 连接

    msg:
        code 为 0 时, msg 为 ssh 返回的数据, 前端页面将获取 ssh 返回的数据并写入终端页面
        code 为 1 时, msg 为具体的错误信息
    """

    def connect(self):
        """
        打开 websocket 连接, 通过前端传入的参数尝试连接 ssh 主机
         :return:
        """
        self.accept()
        logger.info('socket connect success! ')

    def sshConnect(self,ssh_args):
        auth = ssh_args.get('auth')
        # ssh_key_name = ssh_args.get('ssh_key')
        ssh_key_name=""

        self.ssh = SSH(websocket=self, message=self.message)

        ssh_connect_dict = {
            'host': ssh_args.get('host'),
            'user': ssh_args.get('user'),
            'password': ssh_args.get('password'),
            'port': int(ssh_args.get('port')),
            'timeout': 30,
            'pty_width': ssh_args.get('width'),
            'pty_height': ssh_args.get('height'),
            'current_time': str(ssh_args.get('time'))
        }

        # 不需要
        if auth == 'key':
            ssh_key_file = os.path.join('tmp', ssh_key_name)
            with open(ssh_key_file, 'r') as f:
                ssh_key = f.read()

            from six import StringIO
            string_io = StringIO()
            string_io.write(ssh_key)
            string_io.flush()
            string_io.seek(0)
            ssh_connect_dict['ssh_key'] = string_io

            os.remove(ssh_key_file)

        self.ssh.connect(**ssh_connect_dict)

    def disconnect(self, close_code):
        try:
            self.ssh.close()
        except:
            pass


    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get('type')=="web":
            try:
                info=Servers.objects.get(host=data.get('host'))
                ssh_args={"width":int(data['cols']),"height":int(data['rows']),"auth":"pwd","host":info.host,"user":info.user,"password":info.pwd,"port":info.port, 'time': info.id}
                self.sshConnect(ssh_args)
                logger.info(f'ssh connect info: {ssh_args}')
            except Exception as err:
                logger.error(err)
                logger.error(traceback.format_exc())
        else:
            logger.info(f'input linux command is: {data}')
            if data['code'] == 0:  # send data
                Thread(target=self.ssh.django_to_ssh, args=(data['data'],)).start()
            elif data['code'] == 2: # close session
                self.ssh.close()
            elif data['code'] == 1: # setting terminal size
                self.ssh.resize_pty(cols=data['cols'], rows=data['rows'])
            elif data['code'] == 3:
                self.ssh.upload_file_by_byte(data['data'])
