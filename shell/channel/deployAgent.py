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


def invoke_cmd(channel, command, is_split=True, timeout=0.5):
    channel.send(f'{command}\n')
    time.sleep(timeout)
    data = channel.recv(1024).decode('utf-8')

    if is_split:
        try:
            res_list = data.split('\n')
            logger.info(f'{command} : {res_list[1]}')
            return res_list[1]
        except IndexError:
            logger.info(f'{command} : {res_list}')
            return ''
    else:
        logger.info(f'{command} : {data}')
        return data


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

    try:
        if package_type == 'monitor-agent':
            monitor_path = os.path.join(deploy_path, 'monitor_agent')
            res = check_sysstat_version(client)
            if res['code'] > 0:
                raise MyException(res['msg'])
            deploy_agent(client, local_path, monitor_path, file_name, address)
        if package_type == 'collector-agent':
            collector_path = os.path.join(deploy_path, 'collector_agent')
            deploy_agent(client, local_path, collector_path, file_name, address)
        if package_type == 'nginx-agent':
            nginx_path = os.path.join(deploy_path, 'nginx_agent')
            deploy_agent(client, local_path, nginx_path, file_name, address)
        if package_type == 'jmeter-agent':
            jmeter_path = os.path.join(deploy_path, 'JMeter')
            jmeter_agent_path = os.path.join(deploy_path, 'jmeter_agent')
            agent_status = check_jmeter_agent_status(client, jmeter_path)
            if agent_status > 0:
                msg = [f'Not Found {jmeter_path}/bin/jmeter', 'Not Found Java']
                logger.error(msg[agent_status - 1])
                raise MyException(msg[agent_status - 1])
            deploy_agent(client, local_path, jmeter_agent_path, file_name, address)
        if package_type == 'java':
            java_path = os.path.join(deploy_path, 'JAVA')
            deploy_java(client, local_path, java_path, file_name)
        if package_type == 'jmeter':
            jmeter_path = os.path.join(deploy_path, 'JMeter')
            deploy_jmeter(client, local_path, jmeter_path, file_name)
    except MyException as err:
        client.close()
        raise MyException(err.msg)
    client.close()


def check_deploy_status(host, port, user, pwd, deploy_path, current_time, package_type):
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

    try:
        if package_type == 'monitor-agent':
            monitor_path = os.path.join(deploy_path, 'monitor_agent')
            if not check_agent_status(client, monitor_path):
                raise MyException('Deploy monitor-agent failure, please try later ~')
        if package_type == 'collector-agent':
            collector_path = os.path.join(deploy_path, 'collector_agent')
            if not check_agent_status(client, collector_path):
                raise MyException('Deploy collector-agent failure, please try later ~')
        if package_type == 'nginx-agent':
            nginx_path = os.path.join(deploy_path, 'nginx_agent')
            if not check_agent_status(client, nginx_path):
                raise MyException('Deploy nginx-agent failure, please try later ~')
        if package_type == 'jmeter-agent':
            jmeter_path = os.path.join(deploy_path, 'jmeter_agent')
            if not check_agent_status(client, jmeter_path):
                raise MyException('Deploy jmeter-agent failure, please try later ~')
        if package_type == 'java':
            if not check_java_status(client):
                raise MyException('Deploy java failure, please try later ~')
        if package_type == 'jmeter':
            jmeter_path = os.path.join(deploy_path, 'JMeter')
            if not check_jmeter_status(client, jmeter_path):
                raise MyException('Deploy JMeter failure, please try later ~')
    except MyException as err:
        client.close()
        raise MyException(err.msg)
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
    if package_type == 'collector-agent':
        collector_path = os.path.join(deploy_path, 'collector_agent')
        uninstall_agent(client, collector_path)
    if package_type == 'nginx-agent':
        nginx_path = os.path.join(deploy_path, 'nginx_agent')
        uninstall_agent(client, nginx_path)
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
        res = execute_cmd(client, f'ls {install_path} |xargs')
        if res:
            # get monitor port
            res = execute_cmd(client, f"cat /{install_path}/config.conf |grep port |head -3 |grep =")
            agent_port = res.split('=')[-1].strip()
            logger.info(f'Agent port is {agent_port}')
            # get pid
            res = execute_cmd(client, f"netstat -nlp|grep {agent_port} |grep LISTEN")
            logger.info(f'Agent status is {res}')
            if res:
                pid = res.split('LISTEN')[-1].split('/')[0].strip()
                # kill -9 pid
                _ = execute_cmd(client, 'kill -9 ' + pid)
            # check port again
            res = execute_cmd(client, f"netstat -nlp|grep {agent_port} |grep LISTEN")
            logger.info(f'Kill Agent, status is {res}')
            if res:
                raise MyException('Uninstall failure, please try again ~')
            # rm -rf
            _ = execute_cmd(client, f'rm -rf {install_path}')
            res = execute_cmd(client, f'ls {install_path} |xargs')
            if res:
                raise MyException('Uninstall failure, please try again ~')
        else:
            logger.info('Have been uninstalled ~')
    except MyException as err:
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        raise MyException('Uninstall failure ~')


def deploy_agent(client, local_path, deploy_path, file_name, address):
    try:
        uninstall_agent(client, deploy_path)
        deploy_first_step(client, local_path, deploy_path, file_name)
        _ = execute_cmd(client, f'chmod 777 {deploy_path}/server')
        logger.info(f'chmod 777 {deploy_path}/server')
        _ = execute_cmd(client, f'echo "address = {address}" >> {deploy_path}/config.conf')
        logger.info(f'write address {address} to {deploy_path}/config.conf')
        # startup monitor
        _ = execute_cmd(client, f"echo '#!/bin/sh' >> {deploy_path}/start.sh")
        _ = execute_cmd(client, f"echo 'nohup ./server > /dev/null 2>&1 &' >> {deploy_path}/start.sh")
        _ = execute_cmd(client, f"echo 'sleep 5' >> {deploy_path}/start.sh")
        if 'jmeter_agent' in deploy_path:
            channel = client.invoke_shell()
            while channel.recv_ready():
                _ = channel.recv(1024)
                if not channel.recv_ready():
                    break
            _ = invoke_cmd(channel, f'cd {deploy_path}; sh start.sh', is_split=False, timeout=3)
        else:
            _ = execute_cmd(client, f'cd {deploy_path}; sh start.sh')
    except MyException as err:
        _ = execute_cmd(client, f'rm -rf {deploy_path}')
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        _ = execute_cmd(client, f'rm -rf {deploy_path}')  # clear folder
        raise MyException('Deploy failure ~')


def deploy_jmeter(client, local_path, deploy_path, file_name):
    try:
        uninstall_jmeter(client, deploy_path)
        deploy_first_step(client, local_path, deploy_path, file_name)
        jmeter_executor = os.path.join(deploy_path, 'bin', 'jmeter')
        res = execute_cmd(client, f'ls {jmeter_executor} |xargs')
        if 'cannot' in res:
            logger.error(f'Not Found {jmeter_executor} ~')
            raise MyException('Deploy failure, please deploy JMeter again ~')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure, please try again ~')


def deploy_java(client, local_path, deploy_path, file_name):
    try:
        uninstall_java(client, deploy_path)
        deploy_first_step(client, local_path, deploy_path, file_name)
        _ = execute_cmd(client, f'chmod -R 755 {deploy_path}')
        # clear Java variables from /etc/profile
        _ = execute_cmd(client, "sed -i '/JAVA_HOME/d' /etc/profile")
        _ = execute_cmd(client, "sed -i '/JAVA_BIN/d' /etc/profile")
        _ = execute_cmd(client, "sed -i '/JRE_HOME/d' /etc/profile")
        logger.info(f'delete java variable from /etc/profile')
        # write Java variables
        _ = execute_cmd(client, f"echo 'export JAVA_HOME={deploy_path}' >> /etc/profile")
        _ = execute_cmd(client, f"echo 'export JAVA_BIN={deploy_path}/bin' >> /etc/profile")
        _ = execute_cmd(client, f"echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile")
        logger.info(f'write java variable to /etc/profile')
        _ = execute_cmd(client, 'source /etc/profile')
        _ = execute_cmd(client, 'sh /etc/profile')
        _ = execute_cmd(client, 'source /etc/profile')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure, please try again ~')


def deploy_first_step(client, local_path, deploy_path, file_name):
    try:
        # create folder
        _ = execute_cmd(client, f'mkdir {deploy_path}')
        logger.info(f'mkdir {deploy_path}')
        # sftp
        sftp = client.open_sftp()
        sftp.put(local_path, f'{deploy_path}/{file_name}')
        sftp.close()
        logger.info(f'sftp {local_path} to {deploy_path}/{file_name}')
        # unzip file
        if 'zip' in file_name:
            cmd = f'unzip -o -q {deploy_path}/{file_name} -d {deploy_path}'
        else:
            cmd = f'tar -zxf {deploy_path}/{file_name} -C {deploy_path}'
        _ = execute_cmd(client, cmd)
        logger.info(cmd)
        _ = execute_cmd(client, f'rm -rf {deploy_path}/{file_name}')
        res = execute_cmd(client, f'ls {deploy_path} |xargs')
        logger.debug(res)
        if res:
            folders = len(res.split(' '))
            if folders == 1:
                file_path = os.path.join(deploy_path, res)
                _ = execute_cmd(client, f'mv -f {file_path}/* {deploy_path}')
                logger.info(f'move files to {deploy_path}')
                _ = execute_cmd(client, f'rm -rf {file_path}')
        else:
            raise MyException(f'Not found file in {deploy_path}')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure ~')


def uninstall_jmeter(client, install_path):
    # rm -rf
    _ = execute_cmd(client, f'rm -rf {install_path}')
    res = execute_cmd(client, f'ls {install_path} |xargs')
    if 'bin' in res:
        raise MyException('Uninstall failure, please try again ~')


def uninstall_java(client, install_path):
    uninstall_jmeter(client, install_path)
    # clear Java variables from /etc/profile
    _ = execute_cmd(client, "sed -i '/JAVA_HOME/d' /etc/profile")
    _ = execute_cmd(client, "sed -i '/JAVA_BIN/d' /etc/profile")
    _ = execute_cmd(client, "sed -i '/JRE_HOME/d' /etc/profile")
    if check_java_status(client):
        logger.warning('Uninstall JAVA failure ~')
        raise MyException('Uninstall JAVA failure ~')


def check_agent_status(client, deploy_path):
    try:
        res = execute_cmd(client, f'ls {deploy_path} |xargs')
        if 'cannot' not in res:
            res = execute_cmd(client, f"cat {deploy_path}/pid").strip()
            logger.info(f'Agent pid is {res}')
            res = execute_cmd(client, f"pwdx {res}").strip()
            logger.info(f'Agent pid status: {res}')
            if deploy_path in res:
                return True
            else:
                return False
        else:
            logger.error(f'Not found files in {deploy_path}')
            return False
    except:
        logger.error(traceback.format_exc())
        return False


def check_jmeter_agent_status(client, jmeter_path):
    channel = client.invoke_shell()
    while channel.recv_ready():
        _ = channel.recv(1024)
        if not channel.recv_ready():
            break
    res = invoke_cmd(channel, 'java -version', is_split=False, timeout=1)
    if 'Environment' not in res:
        return 1

    jmeter_executor = os.path.join(jmeter_path, 'bin', 'jmeter')
    res = invoke_cmd(channel, f'{jmeter_executor} -v |grep Apache', is_split=False, timeout=3)
    if 'Copyright' not in res:
        return 2
    return 0


def check_java_status(client):
    channel = client.invoke_shell()
    while channel.recv_ready():
        _ = channel.recv(1024)
        if not channel.recv_ready():
            break
    res = invoke_cmd(channel, 'java -version', is_split=False, timeout=1)
    if 'Environment' in res:
        return True
    else:
        return False


def check_jmeter_status(client, deploy_path):
    channel = client.invoke_shell()
    while channel.recv_ready():
        _ = channel.recv(1024)
        if not channel.recv_ready():
            break
    jmeter_executor = os.path.join(deploy_path, 'bin', 'jmeter')
    res = invoke_cmd(channel, f'{jmeter_executor} -v |grep Apache', is_split=False, timeout=3)
    if 'Copyright' in res:
        return True
    else:
        return False


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
    except ValueError:
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
    except ValueError:
        logger.error(traceback.format_exc())
        msg = 'Please install or upgrade sysstat to version 12+, download link: ' \
              'http://sebastien.godard.pagesperso-orange.fr/download.html'
        logger.error(msg)
        return {'code': 1, 'msg': msg}

    return {'code': 0, 'msg': None}
