#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import time
import socket
import logging
import traceback
import paramiko
from .ssh import execute_cmd, parse_pwd
from common.customException import MyException


logger = logging.getLogger('django')


def deploy(host, port, user, pwd, deploy_path, current_time, local_path, file_name, package_type, address):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(username=user, password=parse_pwd(current_time, pwd), hostname=host, port=port, timeout=10)
    except socket.timeout:
        logger.error(f'{host} ssh connect timeout ~')
        client.close()
        raise MyException('Session Connect Timeout ~')
    except paramiko.ssh_exception.NoValidConnectionsError:
        logger.error(f'{host} Unable to Connect Session ~ ')
        client.close()
        raise MyException('Unable to connect ~')
    except paramiko.ssh_exception.AuthenticationException:
        logger.error(f'{host} Username or Password Error ~')
        client.close()
        raise MyException('Username or password error ~')
    except:
        logger.error(traceback.format_exc())
        client.close()
        raise MyException('Session Connect Error ~')

    if package_type == 'monitor-agent':
        monitor_path = os.path.join(deploy_path, 'monitor_agent')
        res = check_sysstat_version(client)
        if res['code'] > 0:
            raise MyException(res['msg'])
        deploy_agent(client, local_path, monitor_path, file_name, address)
    if package_type == 'jmeter-agent':
        jmeter_path = os.path.join(deploy_path, 'jmeter_agent')
        check_jmeter(client, jmeter_path)
        check_java(client)
        deploy_agent(client, local_path, jmeter_path, file_name, address)
    if package_type == 'java':
        java_path = os.path.join(deploy_path, 'JAVA')
        deploy_java(client, local_path, java_path, file_name)
    if package_type == 'jmeter':
        jmeter_path = os.path.join(deploy_path, 'JMeter')
        deploy_jmeter(client, local_path, jmeter_path, file_name)

    client.close()


def stop_deploy(host, port, user, pwd, current_time, package_type, deploy_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(username=user, password=parse_pwd(current_time, pwd), hostname=host, port=port, timeout=10)
    except socket.timeout:
        logger.error(f'{host} ssh connect timeout ~')
        client.close()
        raise MyException('Session Connect Timeout ~')
    except paramiko.ssh_exception.NoValidConnectionsError:
        logger.error(f'{host} Unable to Connect Session ~ ')
        client.close()
        raise MyException('Unable to connect ~')
    except paramiko.ssh_exception.AuthenticationException:
        logger.error(f'{host} Username or Password Error ~')
        client.close()
        raise MyException('Username or password error ~')
    except:
        logger.error(traceback.format_exc())
        client.close()
        raise MyException('Session Connect Error ~')

    if package_type == 'monitor-agent':
        monitor_path = os.path.join(deploy_path, 'monitor_agent')
        uninstall_agent(client, monitor_path)
    if package_type == 'jmeter-agent':
        jmeter_path = os.path.join(deploy_path, 'jmeter_agent')
        uninstall_agent(client, jmeter_path)
    if package_type == 'java':
        java_path = os.path.join(deploy_path, 'JAVA')
        uninstall_java(client, java_path)
    if package_type == 'jmeter':
        jmeter_path = os.path.join(deploy_path, 'JMeter')
        uninstall_jmeter(client, jmeter_path)

    client.close()


def uninstall_agent(client, install_path):
    try:
        res = execute_cmd(client, f'ls {install_path}')
        if res:
            # get monitor port
            res = execute_cmd(client, f"cat /{install_path}/config.conf |grep port |head -3 |grep =")
            agent_port = res.split('=')[-1].strip()
            # get pid
            res = execute_cmd(client, f"netstat -nlp|grep {agent_port} |grep LISTEN")
            if res:
                pid = res.split('LISTEN')[-1].split('/')[0].strip()
                # kill -9 pid
                _ = execute_cmd(client, 'kill -9 ' + pid)
            # check port again
            res = execute_cmd(client, f"netstat -nlp|grep {agent_port} |grep LISTEN")
            if res:
                raise MyException('Uninstall failure, please try again ~')
            # rm -rf
            _ = execute_cmd(client, f'rm -rf {install_path}')
            res = execute_cmd(client, f'ls {install_path}')
            if res:
                raise MyException('Uninstall failure, please try again ~')
    except MyException as err:
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        raise MyException('Uninstall failure ~')


def deploy_agent(client, local_path, deploy_path, file_name, address):
    try:
        res = execute_cmd(client, f'ls {deploy_path}')
        if res:
            logger.info(f'cmd: rm -rf {deploy_path}')
            _ = execute_cmd(client, f'rm -rf {deploy_path}')
        deploy_first_step(client, local_path, deploy_path, file_name)
        _ = execute_cmd(client, f'echo "address = {address}" >> {deploy_path}/config.conf')
        # startup monitor
        _ = execute_cmd(client, f'nohup {deploy_path}/server > /dev/null 2>&1 &')
        # get monitor port
        res = execute_cmd(client, f"cat {deploy_path}/config.conf |grep port |head -3 |grep =")
        agent_port = res.split('=')[-1].strip()
        # port is listened
        for i in range(3):
            time.sleep(1)
            res = execute_cmd(client, "netstat -nlp|grep " + agent_port + " |grep LISTEN")
            if res: break
        if not res:
            _ = execute_cmd(client, f'rm -rf {deploy_path}')  # clear folder
            raise MyException('Startup failure, please try again ~')
    except MyException as err:
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        _ = execute_cmd(client, f'rm -rf {deploy_path}')  # clear folder
        raise MyException('Deploy failure ~')


def deploy_jmeter(client, local_path, deploy_path, file_name):
    try:
        deploy_first_step(client, local_path, deploy_path, file_name)
        jmeter_executor = os.path.join(deploy_path, 'bin', 'jmeter')
        res = execute_cmd(client, f'ls {jmeter_executor}')
        if 'cannot' in res:
            logger.error(f'Not Found {jmeter_executor} ~')
            raise MyException('Deploy failure, please deploy JMeter again ~')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure, please try again ~')


def deploy_java(client, local_path, deploy_path, file_name):
    try:
        res = execute_cmd(client, 'whereis java')
        if len(res) > 10:
            logger.warning('JAVA has been deployed ~')
            raise MyException('JAVA has been deployed ~')
        deploy_first_step(client, local_path, deploy_path, file_name)
        _ = execute_cmd(client, f'chmod -R 755 {deploy_path}')
        # clear Java variables from /etc/profile
        _ = execute_cmd(client, "sed -i '/JAVA_HOME/d' /etc/profile")
        _ = execute_cmd(client, "sed -i '/JAVA_BIN/d' /etc/profile")
        _ = execute_cmd(client, "sed -i '/JRE_HOME/d' /etc/profile")
        # write Java variables
        _ = execute_cmd(client, f"echo 'export JAVA_HOME={deploy_path}' >> /etc/profile")
        _ = execute_cmd(client, f"echo 'export JAVA_BIN={deploy_path}/bin' >> /etc/profile")
        _ = execute_cmd(client, f"echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile")
        _ = execute_cmd(client, 'source /etc/profile')
        _ = execute_cmd(client, 'sh /etc/profile')
        _ = execute_cmd(client, 'source /etc/profile')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure, please try again ~')


def deploy_first_step(client, local_path, deploy_path, file_name):
    try:
        # create folder
        res = execute_cmd(client, f'mkdir {deploy_path}')
        logger.info(f'mkdir: run result -- {res}')
        # sftp
        sftp = client.open_sftp()
        sftp.put(local_path, f'{deploy_path}/{file_name}')
        sftp.close()
        # unzip file
        if 'zip' in file_name:
            cmd = f'unzip -o {deploy_path}/{file_name} -d {deploy_path}'
        else:
            cmd = f'tar -zxvf {deploy_path}/{file_name}'
        _ = execute_cmd(client, cmd)
        _ = execute_cmd(client, f'rm -rf {deploy_path}/{file_name}')
        res = execute_cmd(client, f'ls {deploy_path}')
        logger.debug(res)
        if res:
            folders = len(res.split(' '))
            if folders == 1:
                file_path = os.path.join(deploy_path, res)
                _ = execute_cmd(client, f'mv -f {file_path}/* {deploy_path}')
                _ = execute_cmd(client, f'rm -rf {file_path}')
        else:
            raise MyException(f'Not found file in {deploy_path}')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure ~')


def uninstall_jmeter(client, install_path):
    # rm -rf
    _ = execute_cmd(client, f'rm -rf {install_path}')
    res = execute_cmd(client, f'ls {install_path}')
    if res:
        raise MyException('Uninstall failure, please try again ~')


def uninstall_java(client, install_path):
    uninstall_jmeter(client, install_path)
    # clear Java variables from /etc/profile
    _ = execute_cmd(client, "sed -i '/JAVA_HOME/d' /etc/profile")
    _ = execute_cmd(client, "sed -i '/JAVA_BIN/d' /etc/profile")
    _ = execute_cmd(client, "sed -i '/JRE_HOME/d' /etc/profile")
    res = execute_cmd(client, 'whereis java')
    if len(res) > 10:
        logger.warning('Uninstall JAVA failure ~')
        raise MyException('Uninstall JAVA failure ~')


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


def check_jmeter(client, deploy_path):
    """ Check jmeter"""
    try:
        jmeter_executor = os.path.join(deploy_path, 'bin', 'jmeter')
        res = execute_cmd(client, f'{jmeter_executor} -v')
        if 'Copyright' not in res:
            logger.error(f'Not Found {jmeter_executor} ~')
            raise MyException('Please deploy JMeter first ~')
    except MyException as err:
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        raise MyException('Check JMeter failure, please try to deploy JMeter ~')


def check_java(client):
    """ Check Java"""
    try:
        res = execute_cmd(client, 'whereis java')
        if len(res) < 10:
            logger.error('Not Found Java ~')
            raise MyException('Please deploy JAVA first ~')
    except MyException as err:
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        raise MyException('Check JAVA failure, please try to deploy JAVA ~')
