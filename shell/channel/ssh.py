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
        logger.error('ssh connect timeout ~')
        client.close()
        return {'code': 1, 'msg': 'Session Connect Timeout ~'}
    except paramiko.ssh_exception.NoValidConnectionsError:
        logger.error('Unable to Connect Session ~ ')
        client.close()
        return {'code': 1, 'msg': 'Unable to connect ~'}
    except paramiko.ssh_exception.AuthenticationException:
        logger.error('Username or Password Error ~')
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


def execute_cmd(client,command):
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


def deploy_mon(host, port, user, pwd, current_time, local_path, file_name):
    data = connect_ssh(host, port, user, pwd, str(current_time))
    if data['code'] > 0:
        return data

    client = data['client']
    res = check_sysstat_version(client)
    if res['code'] > 0:
        client.close()
        return res

    try:
        # create folder
        res = execute_cmd(client, 'mkdir /home/monitor_server')
        logger.info(f'mkdir: run result -- {res}')
        # sftp
        sftp = client.open_sftp()
        sftp.put(local_path, f'/home/monitor_server/{file_name}')
        sftp.close()
        # unzip file
        res = execute_cmd(client, f'unzip -o /home/monitor_server/{file_name} -d /home/monitor_server')
        logger.info(f'unzip: run result -- {res}')
        # startup.sh in folder
        res = execute_cmd(client, 'ls /home/monitor_server/startup.sh')
        logger.info(f'Is there startup.sh: run result -- {res}')
        if not res:
            _ = execute_cmd(client, 'rm -rf /home/monitor_server')  # clear folder
            client.close()
            return {'code': 1, 'msg': 'startup.sh is missing, please put startup.sh into zip package ~'}
        # startup monitor
        res = execute_cmd(client, 'cd /home/monitor_server; sh startup.sh')
        logger.info(f'sh startup.sh: run result -- {res}')
        if not res:
            _ = execute_cmd(client, 'rm -rf /home/monitor_server')  # clear folder
            client.close()
            return {'code': 1, 'msg': 'monitor startup failure ~'}
        # get monitor port
        res = execute_cmd(client, "cat /home/monitor_server/config.ini |grep port |head -3 |grep =")
        agent_port = res.split('=')[-1].strip()
        # port is listened
        for i in range(3):
            time.sleep(1)
            res = execute_cmd(client, "netstat -nlp|grep " + agent_port + " |grep LISTEN")
            if res: break
        if not res:
            _ = execute_cmd(client, 'rm -rf /home/monitor_server')  # clear folder
            client.close()
            return {'code': 1, 'msg': 'monitor startup failure, please try again ~'}
        client.close()
        return {'code': 0, 'msg': 'deploy monitor success ~'}
    except:
        logger.error(traceback.format_exc())
        _ = execute_cmd(client, 'rm -rf /home/monitor_server')  # clear folder
        client.close()
        return {'code': 1, 'msg': 'deploy monitor failure ~'}


def stop_mon(host, port, user, pwd, current_time):
    data = connect_ssh(host, port, user, pwd, str(current_time))
    if data['code'] > 0:
        return data

    client = data['client']
    res = clear_deploy(client)
    client.close()
    return res


def clear_deploy(client):
    try:
        # get monitor port
        res = execute_cmd(client, "cat /home/monitor_server/config.ini |grep port |head -3 |grep =")
        agent_port = res.split('=')[-1].strip()
        # get pid
        res = execute_cmd(client, "netstat -nlp|grep " + agent_port + " |grep LISTEN")
        if res:
            pid = res.split('LISTEN')[-1].split('/')[0].strip()
            # kill -9 pid
            _ = execute_cmd(client, 'kill -9 ' + pid)
        # rm -rf
        _ = execute_cmd(client, 'rm -rf /home/monitor_server')
        res = execute_cmd(client, 'll /home/monitor_server')
        if res:
            return {'code': 1, 'msg': 'Stop monitor failure, please try again ~'}
        res = execute_cmd(client, "netstat -nlp|grep " + agent_port + " |grep LISTEN")
        if res:
            return {'code': 1, 'msg': 'Stop monitor failure, please try again ~'}
        return {'code': 0, 'msg': 'deploy monitor success ~'}
    except:
        logger.error(traceback.format_exc())
        return {'code': 1, 'msg': 'deploy monitor failure ~'}


def check_sysstat_version(client):
        """
        Check sysstat version
        """
        try:
            version = execute_cmd(client, "iostat -V |grep ersion |awk '{print $3}' |awk -F '.' '{print $1}'")
            v = int(version.strip())
            if v < 12:
                msg = 'The iostat version is too low, please upgrade to version 12+, download link: ' \
                      'http://sebastien.godard.pagesperso-orange.fr/download.html'
                logger.error(msg)
                return {'code': 1, 'msg': msg}
        except IndexError:
            logger.error(traceback.format_exc())
            msg = 'Please install or upgrade sysstat to version 12+, download link: ' \
                  'http://sebastien.godard.pagesperso-orange.fr/download.html'
            logger.error(msg)
            return {'code': 1, 'msg': msg}

        try:
            version = execute_cmd(client, "pidstat -V |grep ersion |awk '{print $3}' |awk -F '.' '{print $1}'")
            v = int(version.strip())
            if v < 12:
                msg = 'The pidstat version is too low, please upgrade to version 12+, download link: ' \
                      'http://sebastien.godard.pagesperso-orange.fr/download.html'
                logger.error(msg)
                return {'code': 1, 'msg': msg}
        except IndexError:
            logger.error(traceback.format_exc())
            msg = 'Please install or upgrade sysstat to version 12+, download link: ' \
                  'http://sebastien.godard.pagesperso-orange.fr/download.html'
            logger.error(msg)
            return {'code': 1, 'msg': msg}

        return {'code': 0, 'msg': None}

class UploadAndDownloadFile(object):
    def __init__(self, server_info):
        self.t = None
        self.sftp = None

        self.connect(server_info.host, server_info.port, server_info.user, server_info.pwd, str(server_info.id))

    def connect(self, host, port, user, password, current_time):
        self.t = paramiko.Transport((host, port))
        self.t.connect(username = user, password = parse_pwd(current_time, password))
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
