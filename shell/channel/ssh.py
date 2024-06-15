#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import io
import re
import time
import socket
import logging
import traceback
import paramiko
from threading import Thread

logger = logging.getLogger('django')


class SSH:
    def __init__(self, websocket):
        self.websocket = websocket
        self.ssh_client = paramiko.SSHClient()
        self.keepalive_last_time = time.time()
        self.transport = None
        self.channel = None

    def connect(self, host, user, password=None, ssh_key=None, port=22, timeout=10,
                term='xterm', pty_width=40, pty_height=24, current_time=None):
        try:
            # Allow trusted hosts to be added to "host_allow" list.
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if ssh_key:
                key = get_key_obj(paramiko.RSAKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.DSSKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.ECDSAKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.Ed25519Key, pkey_obj=ssh_key, password=password)

                self.ssh_client.connect(username=user, hostname=host, port=port, pkey=key, timeout=timeout)
            else:
                self.ssh_client.connect(username=user, password=parse_pwd(current_time, password), hostname=host, port=port, timeout=timeout)

            self.transport = self.ssh_client.get_transport()
            self.channel = self.transport.open_session()
            self.channel.get_pty(term=term, width=pty_width, height=pty_height)
            self.channel.invoke_shell()
            logger.info('ssh connect success ~ ')

            Thread(target=self.backend_to_frontend).start()
            Thread(target=self.heart_beat_check).start()

        except socket.timeout:
            logger.error('ssh connect timeout! ')
            self.close('Session Connect Timeout ~ ')
        except paramiko.ssh_exception.NoValidConnectionsError:
            logger.error('Unable to connect ~ ')
            self.close('Unable to Connect Session ~ ')
        except paramiko.ssh_exception.AuthenticationException:
            logger.error('Username or password error ~')
            self.close('Username or Password Error ~')
        except:
            logger.error(traceback.format_exc())
            self.close()

    def exec_command(self,command):
        _, stdout, _ = self.ssh_client.exec_command(command)
        result = stdout.read().decode("utf-8")
        return result

    def resize_pty(self, cols, rows):
        self.channel.resize_pty(width=cols, height=rows)

    def django_to_ssh(self, data):
        try:
            self.channel.send(data)
        except:
            logger.error(traceback.format_exc())
            self.close()

    def backend_to_frontend(self):
        """
            backend data trans to frontend to display
        """
        try:
            while True:
                try:
                    data = self.channel.recv(1024).decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(self.channel.recv(1024))
                    data = self.channel.recv(1024).decode('unicode_escape')
                self.keepalive_last_time = time.time()
                if not len(data):
                    break
                self.websocket.send(data)
                logger.debug(f'back to front data: {data}')
            self.websocket.close()
            logger.info('exit ssh and socket success ~ ')
        except:
            logger.error(self.channel.recv(1024))
            logger.error(traceback.format_exc())
            self.close()

    def close(self, msg = 'Session is already in CLOSED state ~'):
        self.websocket.send(msg)
        self.ssh_client.close()
        self.websocket.close()

    def heart_beat_check(self):
        try:
            while True:
                if time.time() - self.keepalive_last_time < 600 and self.ssh_client.get_transport():
                    time.sleep(10)
                    logger.info('heart beat check ... ... ')
                    continue
                else:
                    self.ssh_client.close()
                    break
            self.websocket.send('Session is already in CLOSED state ~')
            logger.info('close ssh success ~ ')
        except:
            logger.error(traceback.format_exc())
            self.ssh_client.close()
            logger.info('close ssh success ~ ')


def get_key_obj(pkeyobj, pkey_file=None, pkey_obj=None, password=None):
    if pkey_file:
        with open(pkey_file) as fo:
            try:
                pkey = pkeyobj.from_private_key(fo, password=password)
                return pkey
            except:
                pass
    else:
        try:
            pkey = pkeyobj.from_private_key(pkey_obj, password=password)
            return pkey
        except:
            pkey_obj.seek(0)


def connect_ssh(host, port, user, pwd, current_time):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(username=user, password=parse_pwd(current_time, pwd), hostname=host, port=port, timeout=10)
        return {'code': 0, 'client': client}
    except socket.timeout:
        logger.error(f'{host} ssh connect timeout ~')
        client.close()
        return {'code': 1, 'msg': 'Session Connect Timeout ~'}
    except paramiko.ssh_exception.NoValidConnectionsError:
        logger.error(f'{host} Unable to Connect Session ~ ')
        client.close()
        return {'code': 1, 'msg': 'Unable to connect ~'}
    except paramiko.ssh_exception.AuthenticationException:
        logger.error(f'{host} Username or Password Error ~')
        client.close()
        return {'code': 1, 'msg': 'Username or password error ~'}
    except:
        logger.error(traceback.format_exc())
        client.close()
        return {'code': 1, 'msg': 'Session Connect Error ~'}


def get_server_info(host, port, user, pwd, current_time):
    try:
        data = connect_ssh(host, port, user, pwd, current_time)
        if data['code'] == 1:
            return data

        client = data['client']

        try:
            results = execute_cmd(client, 'cat /etc/redhat-release')    # system release version
            logger.debug(f'The system release version is {results}')
            system_version = results.strip().replace('Linux ', '').replace('release ', '').replace('(Core)', '')
        except Exception as err:
            logger.warning(err)
            results = execute_cmd(client, 'cat /proc/version')   # system kernel version
            logger.debug(f'The system kernel version is{results}')
            res = re.findall(r"gcc.*\((.*?)\).*GCC", results.strip())
            if res:
                system_version = res[0]
            else:
                res = re.findall(r"gcc.*\((.*?)\)", results.strip())
                system_version = res[0]

        total_disk = 0
        results = execute_cmd(client, 'df -m')
        logger.debug(f'The data of disk is {results}')
        results = results.strip().split('\n')
        for line in results:
            res = line.split()
            if '/dev/' in res[0]:
                size = float(res[1])
                total_disk += size

        total_disk_h = total_disk / 1024
        if total_disk_h > 1024:
            total = round(total_disk_h / 1024, 2)
            total_disk_h = f'{total}T'
        else:
            total = round(total_disk_h, 2)
            total_disk_h = f'{total}G'

        logger.info(f'The total size of disks is {total_disk_h}')

        results = execute_cmd(client, 'cat /proc/meminfo| grep "MemTotal"')
        total_mem = float(results.split(':')[-1].split('k')[0].strip()) / 1048576  # 1048576 = 1024 * 1024
        logger.info(f'The total memory is {total_mem}G')

        results = execute_cmd(client, 'cat /proc/cpuinfo| grep "processor"| wc -l')
        cpu_cores = int(results.strip())
        logger.info(f'The number of cores all CPU is {cpu_cores}')

        results = execute_cmd(client, 'uname -m')
        cpu_arch = results.strip()
        logger.info(f'The system architecture is {cpu_arch}')
        client.close()

        return {'code': 0, 'cpu': cpu_cores, 'mem': round(total_mem, 2), 'disk': total_disk_h,
                'arch': cpu_arch, 'system': system_version}

    except:
        logger.error(traceback.format_exc())
        client.close()
        return {'code': 1, 'msg': 'error ~'}


def execute_cmd(client, command):
    _, stdout, _ = client.exec_command(command)
    result = stdout.read().decode("utf-8").strip()
    return result


def parse_pwd(current_time, password):
    p = ''
    time_len = len(current_time)
    for i in range(len(password)):
        if i < time_len:
            p += chr(ord(password[i]) ^ int(current_time[i]))
        else:
            p += chr(ord(password[i]) ^ int(current_time[i - time_len]))

    return p


class UploadAndDownloadFile(object):
    def __init__(self, server_info):
        self.t = None
        self.sftp = None

        self.connect(server_info.host, server_info.port, server_info.user, server_info.pwd, str(server_info.id))

    def connect(self, host, port, user, password, current_time):
        self.t = paramiko.Transport((host, port))
        self.t.connect(username=user, password=parse_pwd(current_time, password))
        self.sftp = paramiko.SFTPClient.from_transport(self.t)

    def upload(self, local_path, remote_path):
        try:
            self.sftp.put(local_path, remote_path)
            return {'code': 0, 'msg': 'upload file success ~'}
        except:
            logger.error(traceback.format_exc())
            return {'code': 1, 'msg': 'upload file failure ~', 'data': local_path}

    def download(self, file_path):
        try:
            fp = io.BytesIO()
            self.sftp.getfo(file_path, fp)
            fp.seek(0)
            return fp
        except:
            raise

    def __del__(self):
        self.sftp.close()
        self.t.close()


if __name__ == '__main__':
    print(parse_pwd('1649577', 'Isw}`uGh'))
