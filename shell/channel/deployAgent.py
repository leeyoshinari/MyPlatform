#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import time
import logging
import traceback
from .ssh import connect_ssh, execute_cmd


logger = logging.getLogger('django')


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
        return {'code': 0, 'msg': 'Stop monitor success ~'}
    except:
        logger.error(traceback.format_exc())
        return {'code': 1, 'msg': 'Stop monitor failure ~'}


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