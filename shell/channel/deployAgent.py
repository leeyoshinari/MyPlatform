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
    while not channel.recv_ready():
        time.sleep(0.1)
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
        return data


def sftp_file(host, port, user, pwd, current_time, local_path, deploy_path, file_name):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(username=user, password=parse_pwd(current_time, pwd), hostname=host, port=port, timeout=10)
        sftp = client.open_sftp()
        sftp.put(local_path, f'{deploy_path}/{file_name}')
        sftp.close()
        logger.info(f'sftp {local_path} to {deploy_path}/{file_name}')
        unzip_file(client, deploy_path, file_name)
        client.close()
    except Exception as err:
        client.close()
        logger.error(err)
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure ~')


def deploy(host, port, user, pwd, deploy_path, current_time, local_path, file_name, package_type, address):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(username=user, password=parse_pwd(current_time, pwd), hostname=host, port=port, timeout=10)
        channel = client.invoke_shell()
        while channel.recv_ready():
            _ = channel.recv(1024)
            if not channel.recv_ready():
                break
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
            res = check_sysstat_version(channel)
            if res['code'] > 0:
                raise MyException(res['msg'])
            uninstall_agent(channel, monitor_path)
            _ = invoke_cmd(channel, f'mkdir {monitor_path}')
            sftp_file(host, port, user, pwd, current_time, local_path, monitor_path, file_name)
            deploy_agent(channel, monitor_path, file_name, address)
        if package_type == 'jmeter-agent':
            jmeter_path = os.path.join(deploy_path, 'JMeter')
            jmeter_agent_path = os.path.join(deploy_path, 'jmeter_agent')
            if not check_jmeter_status(channel, jmeter_path):
                logger.error(f'Not Found {jmeter_path}/bin/jmeter ~')
                raise MyException('Please deploy JMeter first ~')
            if not check_java_status(channel):
                logger.error('Not Found Java ~')
                raise MyException('Please deploy JAVA first ~')
            uninstall_agent(channel, jmeter_agent_path)
            _ = invoke_cmd(channel, f'mkdir {jmeter_agent_path}')
            sftp_file(host, port, user, pwd, current_time, local_path, jmeter_agent_path, file_name)
            deploy_agent(channel, jmeter_agent_path, file_name, address)
        if package_type == 'java':
            java_path = os.path.join(deploy_path, 'JAVA')
            uninstall_java(channel, java_path)
            _ = invoke_cmd(channel, f'mkdir {java_path}')
            sftp_file(host, port, user, pwd, current_time, local_path, java_path, file_name)
            deploy_java(channel, java_path, file_name)
        if package_type == 'jmeter':
            jmeter_path = os.path.join(deploy_path, 'JMeter')
            uninstall_jmeter(channel, jmeter_path)
            _ = invoke_cmd(channel, f'mkdir {jmeter_path}')
            sftp_file(host, port, user, pwd, current_time, local_path, jmeter_path, file_name)
            deploy_jmeter(channel, jmeter_path, file_name)
    except MyException as err:
        client.close()
        raise MyException(err.msg)
    client.close()


def check_deploy_status(host, port, user, pwd, deploy_path, current_time, package_type):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(username=user, password=parse_pwd(current_time, pwd), hostname=host, port=port, timeout=10)
        channel = client.invoke_shell()
        while channel.recv_ready():
            _ = channel.recv(1024)
            if not channel.recv_ready():
                break
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
            if not check_agent_status(channel, monitor_path):
                raise MyException('Deploy monitor-agent failure, please try later ~')
        if package_type == 'jmeter-agent':
            jmeter_path = os.path.join(deploy_path, 'jmeter_agent')
            if not check_agent_status(channel, jmeter_path):
                raise MyException('Deploy jmeter-agent failure, please try later ~')
        if package_type == 'java':
            if not check_java_status(channel):
                raise MyException('Deploy java failure, please try later ~')
        if package_type == 'jmeter':
            jmeter_path = os.path.join(deploy_path, 'JMeter')
            if not check_jmeter_status(channel, jmeter_path):
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
        channel = client.invoke_shell()
        while channel.recv_ready():
            _ = channel.recv(1024)
            if not channel.recv_ready():
                break

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
        uninstall_agent(channel, monitor_path)
    if package_type == 'jmeter-agent':
        jmeter_path = os.path.join(deploy_path, 'jmeter_agent')
        uninstall_agent(channel, jmeter_path)
    if package_type == 'java':
        java_path = os.path.join(deploy_path, 'JAVA')
        uninstall_java(channel, java_path)
    if package_type == 'jmeter':
        jmeter_path = os.path.join(deploy_path, 'JMeter')
        uninstall_jmeter(channel, jmeter_path)

    client.close()


def uninstall_agent(channel, install_path):
    try:
        res = invoke_cmd(channel, f'ls {install_path}')
        if 'config.conf' in res:
            # get monitor port
            res = invoke_cmd(channel, f"cat {install_path}/config.conf |grep port |head -3 |grep =")
            agent_port = res.split('=')[-1].strip()
            logger.info(f'Agent port is {agent_port}')
            # get pid
            pid = get_pid_by_port(channel, agent_port)
            if pid > 0:
                # kill -9 pid
                _ = invoke_cmd(channel, f'kill -9 {pid}')
            # check port again
            res = get_pid_by_port(channel, agent_port)
            if res:
                raise MyException('Uninstall failure, please try again ~')
            # rm -rf
            _ = invoke_cmd(channel, f'rm -rf {install_path}')
            res = invoke_cmd(channel, f'ls {install_path}')
            if 'config.conf' in res:
                raise MyException('Uninstall failure, please try again ~')
    except MyException as err:
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        raise MyException('Uninstall failure ~')


def deploy_agent(channel, deploy_path, file_name, address):
    try:
        _ = invoke_cmd(channel, f'chmod 777 {deploy_path}/server')
        _ = invoke_cmd(channel, f'echo "address = {address}" >> {deploy_path}/config.conf')
        # startup monitor
        _ = invoke_cmd(channel, f"echo '#!/bin/sh' >> {deploy_path}/start.sh")
        _ = invoke_cmd(channel, f"echo 'nohup ./server > /dev/null 2>&1 &' >> {deploy_path}/start.sh")
        _ = invoke_cmd(channel, f"echo 'sleep 5' >> {deploy_path}/start.sh")
        _ = invoke_cmd(channel, f'cd {deploy_path}; sh start.sh')
    except MyException as err:
        _ = invoke_cmd(channel, f'rm -rf {deploy_path}')
        raise MyException(err.msg)
    except:
        logger.error(traceback.format_exc())
        _ = invoke_cmd(channel, f'rm -rf {deploy_path}')  # clear folder
        raise MyException('Deploy failure ~')


def deploy_jmeter(channel, deploy_path, file_name):
    try:
        jmeter_executor = os.path.join(deploy_path, 'bin', 'jmeter')
        res = invoke_cmd(channel, f'ls {jmeter_executor}')
        if 'cannot' in res:
            logger.error(f'Not Found {jmeter_executor} ~')
            raise MyException('Deploy failure, please deploy JMeter again ~')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure, please try again ~')


def deploy_java(channel, deploy_path, file_name):
    try:
        _ = invoke_cmd(channel, f'chmod -R 755 {deploy_path}')
        # clear Java variables from /etc/profile
        _ = invoke_cmd(channel, "sed -i '/JAVA_HOME/d' /etc/profile")
        _ = invoke_cmd(channel, "sed -i '/JAVA_BIN/d' /etc/profile")
        _ = invoke_cmd(channel, "sed -i '/JRE_HOME/d' /etc/profile")
        # write Java variables
        _ = invoke_cmd(channel, f"echo 'export JAVA_HOME={deploy_path}' >> /etc/profile")
        _ = invoke_cmd(channel, f"echo 'export JAVA_BIN={deploy_path}/bin' >> /etc/profile")
        _ = invoke_cmd(channel, f"echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile")
        _ = invoke_cmd(channel, 'source /etc/profile')
        _ = invoke_cmd(channel, 'sh /etc/profile')
        _ = invoke_cmd(channel, 'source /etc/profile')
    except:
        logger.error(traceback.format_exc())
        raise MyException('Deploy failure, please try again ~')


def unzip_file(client, deploy_path, file_name):
    try:
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


def uninstall_jmeter(channel, install_path):
    # rm -rf
    _ = invoke_cmd(channel, f'rm -rf {install_path}')
    res = invoke_cmd(channel, f'ls {install_path}')
    if 'bin' in res:
        raise MyException('Uninstall failure, please try again ~')


def uninstall_java(channel, install_path):
    # rm -rf
    _ = invoke_cmd(channel, f'rm -rf {install_path}')
    res = invoke_cmd(channel, f'ls {install_path}')
    if 'bin' in res:
        raise MyException('Uninstall failure, please try again ~')
    # clear Java variables from /etc/profile
    _ = invoke_cmd(channel, "sed -i '/JAVA_HOME/d' /etc/profile")
    _ = invoke_cmd(channel, "sed -i '/JAVA_BIN/d' /etc/profile")
    _ = invoke_cmd(channel, "sed -i '/JRE_HOME/d' /etc/profile")
    if check_java_status(channel):
        logger.warning('Uninstall JAVA failure ~')
        raise MyException('Uninstall JAVA failure ~')


def check_agent_status(channel, deploy_path):
    try:
        res = invoke_cmd(channel, f'ls {deploy_path}')
        if res:
            res = invoke_cmd(channel, f"cat {deploy_path}/config.conf |grep port |head -3 |grep =")
            agent_port = res.split('=')[-1].strip()
            logger.info(f'Agent port is {agent_port}')
            res = get_pid_by_port(channel, agent_port)
            if res > 0:
                return True
            else:
                return False
        else:
            logger.error(f'Not found files in {deploy_path}')
            return False
    except:
        logger.error(traceback.format_exc())
        return False


def check_java_status(channel):
    res = invoke_cmd(channel, 'java -version', is_split=False, timeout=1)
    if 'Environment' in res:
        return True
    else:
        return False


def check_jmeter_status(channel, deploy_path):
    jmeter_executor = os.path.join(deploy_path, 'bin', 'jmeter')
    res = invoke_cmd(channel, f'{jmeter_executor} -v |grep Apache', is_split=False, timeout=3)
    if 'Copyright' in res:
        return True
    else:
        return False


def get_pid_by_port(channel, port):
    res = invoke_cmd(channel, f"netstat -nlp|grep {port} |grep LISTEN")
    if res:
        pid = res.split('LISTEN')[-1].split('/')[0].strip()
        try:
            return int(pid)
        except ValueError:
            return 0
    else:
        return 0


def check_sysstat_version(channel):
    """
    Check sysstat version
    """
    try:
        version = invoke_cmd(channel, "iostat -V |grep ersion |awk '{print $3}' |awk -F '.' '{print $1}'")
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
        version = invoke_cmd(channel, "pidstat -V |grep ersion |awk '{print $3}' |awk -F '.' '{print $1}'")
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
