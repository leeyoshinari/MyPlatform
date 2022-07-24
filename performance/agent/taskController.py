#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import re
import time
import json
import threading
import traceback
import requests
import redis
import zipfile
import influxdb
from common import get_config, logger, get_ip

class Task(object):
    def __init__(self):
        self.IP = get_ip()
        self.status = 0     # 0 idle, 1 busy, -1 pending
        self.task_id = None
        self.plan_id = None
        self.agent_num = 1
        self.pattern = 'summary\+(\d+)in.*=(\d+.\d+)/sAvg:(\d+)Min:(\d+)Max:(\d+)Err:(\d+)\(.*Active:(\d+)Started'
        self.influx_host = '127.0.0.1'
        self.influx_port = 8086
        self.influx_username = 'root'
        self.influx_password = '123456'
        self.influx_database = 'test'
        self.redis_host = '127.0.0.1'
        self.redis_port = 6379
        self.redis_password = '123456'
        self.redis_db = 0
        self.get_configure_from_server()

        self.jmeter_path = get_config('jmeterPath')
        self.jmeter_executor = os.path.join(self.jmeter_path, 'bin', 'jmeter')
        self.jmeter_file_path = os.path.join(self.jmeter_path, 'results')
        self.setprop_path = os.path.join(self.jmeter_path, 'setprop.bsh')

        self.influx_client = None
        self.redis_client = None

        self.check_env()
        self.write_setprop()
        self.modify_properties()

    def start_thread(self, func, data):
        t = threading.Thread(target=func, args=data)
        t.start()

    def check_env(self):
        if not os.path.exists(self.jmeter_path):
            logger.error(f'The Jmeter path: {self.jmeter_path} is not exist ~')

        res = os.popen(f'{self.jmeter_executor} -v').read()
        if 'Copyright' not in res:
            logger.error(f'Not Found JMeter ~')

        res = os.popen('java -version').read()
        if 'version' not in res:
            logger.error('Not Found Java ~')

        if not os.path.exists(self.jmeter_file_path):
            os.mkdir(self.jmeter_file_path)

    def write_setprop(self):
        try:
            if not os.path.exists(self.setprop_path):
                with open(self.setprop_path, 'w', encoding='utf-8') as f:
                    f.write('import org.apache.jmeter.util.JMeterUtils;\ngetprop(p){\n    return JMeterUtils.getPropDefault(p,"");\n}\n'
                            'setprop(p,v){\n    JMeterUtils.getJMeterProperties().setProperty(p, v);\n}\nsetprop(args[0], args[1]);')
                    logger.info('setprop.bsh is written success ~')
            else:
                logger.info('setprop.bsh has been exist ~')
        except:
            logger.error(traceback.format_exc())

    def modify_properties(self):
        properties_path = os.path.join(self.jmeter_path, 'bin', 'jmeter.properties')
        _ = os.popen(f"sed -i 's|.*summariser.interval.*|summariser.interval=6|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*beanshell.server.port.*|beanshell.server.port=9000|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*beanshell.server.file.*|beanshell.server.file=../extras/startup.bsh|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*jmeter.save.saveservice.samplerData.*|jmeter.save.saveservice.samplerData=true|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*jmeter.save.saveservice.response_data.*|jmeter.save.saveservice.response_data=true|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*jmeter.save.saveservice.response_data.on_error.*|jmeter.save.saveservice.response_data.on_error=true|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*summariser.ignore_transaction_controller_sample_result.*|summariser.ignore_transaction_controller_sample_result=true|g' {properties_path}")
        _ = os.popen(f"sed -e 's/^M//g' {properties_path}")


    def get_configure_from_server(self):
        url = f'http://{get_config("address")}/performance/task/register'
        post_data = {
            'host': self.IP,
            'port': get_config('port'),
            'status': self.status
        }

        while True:
            try:
                res = self.request_post(url, post_data)
                logger.info(f"The result of registration is {res.content.decode('unicode_escape')}")
                if res.status_code == 200:
                    response_data = json.loads(res.content.decode('unicode_escape'))
                    if response_data['code'] == 0:
                        self.influx_host = response_data['data']['influx']['host']
                        self.influx_port = response_data['data']['influx']['port']
                        self.influx_username = response_data['data']['influx']['username']
                        self.influx_password = response_data['data']['influx']['password']
                        self.influx_database = response_data['data']['influx']['database']
                        self.redis_host = response_data['data']['redis']['host']
                        self.redis_port = response_data['data']['redis']['port']
                        self.redis_password = response_data['data']['redis']['password']
                        self.redis_db = response_data['data']['redis']['db']
                        break

                time.sleep(1)

            except:
                logger.error(traceback.format_exc())
                time.sleep(1)

    def register(self):
        url = f'http://{get_config("address")}/performance/task/register'
        post_data = {
            'host': self.IP,
            'port': get_config('port'),
            'status': self.status
        }
        res = self.request_post(url, post_data)
        logger.info("Agent register successful ~")

    def connect_influx(self):
        self.influx_client = influxdb.InfluxDBClient(self.influx_host, self.influx_port, self.influx_username,
                                                     self.influx_password, self.influx_database)

    def connect_redis(self):
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password,
                                        db=self.redis_db, decode_responses=True)

    def check_status(self, is_run=True):
        try:
            res = os.popen('ps -ef|grep jmeter |grep -v grep').read()
            if res and is_run:  # 是否启动成功
                return True
            elif not res and not is_run:    # 是否停止成功
                return True
            else:
                return False
        except:
            logger.error(traceback.format_exc())

    def send_message(self, task_type, post_data):
        try:
            url = f'http://{get_config("address")}/performance/task/register/getMessage'
            post_data = {
                'taskId': self.task_id,
                'type': task_type,
                'data': post_data
            }
            res = self.request_post(url, post_data)
            logger.info("Send message successful ~")
        except:
            logger.error("Send message failure ~")

    def write_to_influx(self, datas):
        d = [json.loads(r) for r in datas]
        data = [sum(r) for r in zip(*d)]
        line = [{'measurement': self.IP,
                 'tags': {'type': str(self.task_id)},
                 'fields': {'samples': data[0], 'tps': data[1], 'rt': data[2], 'min': data[3],
                            'max': data[4], 'err': data[5], 'active': data[6]}}]
        self.influx_client.write_points(line)  # write to database

    def parse_log(self, log_path):
        while not os.path.exists(log_path):
            time.sleep(0.5)

        position = 0
        with open(log_path, mode='r', encoding='utf-8') as f1:
            while True:
                line = f1.readline().strip()
                if 'summary' in line:
                    logger.info(f'JMeter run log - {self.task_id} - {line}')
                    # data = {'samples': 0, 'tps': 0, 'rt': 0, 'min': 0, 'max': 0, 'err': 0, 'active': 0}
                    # data = [0, 0, 0, 0, 0, 0, 0]
                    res = re.findall(self.pattern, line.replace(' ', ''))[0]
                    data = list(map(float, res))
                    self.write_to_redis(data)

                cur_position = f1.tell()  # 记录上次读取文件的位置
                if cur_position == position:
                    time.sleep(0.2)
                    continue
                else:
                    position = cur_position
                    time.sleep(0.2)

                if self.status == 0:
                    break

    def write_to_redis(self, data):
        if self.redis_client.llen(f'task_{self.task_id}') == self.agent_num:
            res = self.redis_client.lrange(f'task_{self.task_id}', 0, self.agent_num)
            self.redis_client.ltrim(f'task_{self.task_id}', self.agent_num, self.agent_num)
            self.write_to_influx(res)
        _ = self.redis_client.lpush(f'task_{self.task_id}', str(data))

    def save_file(self, files):
        pass

    def upload_file_by_path(self, file_path):
        pass

    def upload_file_by_bytes(self, file_bytes):
        pass

    def download_log(self, task_id):
        jtl_path = os.path.join(self.jmeter_file_path, task_id, task_id + '.jtl')
        jmeter_log_path = os.path.join(self.jmeter_file_path, task_id, task_id + '.log')
        zip_file_path = os.path.join(self.jmeter_file_path, task_id, task_id + '.zip')
        archive = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
        if os.path.exists(jtl_path):
            archive.write(jtl_path, task_id + '.jtl')
        archive.write(jmeter_log_path, task_id + '.log')
        archive.close()
        with open(zip_file_path, 'rb', encoding='utf-8') as f:
            res = f.read()
        os.remove(zip_file_path)
        return res

    def download_file_to_path(self, url, file_path):
        with open(file_path, 'wb') as f:
            f.write(self.download_file_to_bytes(url))

    def download_file_to_bytes(self, url):
        res = requests.get(url)
        return res.content

    def unzip_file(self, source_path, target_path):
        f = zipfile.ZipFile(source_path)
        f.extractall(target_path)
        f.close()

    def run_task(self, task_id, file_path, agent_num, is_debug):
        if self.check_status(is_run=True):
            self.kill_process()

        #flag = 0    # 0-run task fail, 1-run task success
        try:
            self.connect_redis()
            self.connect_influx()
            local_file_path = os.path.join(self.jmeter_file_path, task_id + '.zip')
            target_file_path = os.path.join(self.jmeter_file_path, task_id)
            self.download_file_to_path(file_path, local_file_path)
            self.unzip_file(local_file_path, target_file_path)
            if not os.path.exists(target_file_path):
                logger.error('Not Found file after unzip')
                return {'code': 1, 'msg': 'Not Found file after unzip'}
            file_list = os.listdir(target_file_path)
            jmx_files = [file for file in file_list if '.jmx' in file]
            if not jmx_files:
                logger.error('Not Found jmx file ~')
                return {'code': 1, 'msg': 'Not Found jmx file, please zip file again ~'}
            jmx_file_path = os.path.join(target_file_path, jmx_files[0])
            log_path = os.path.join(target_file_path, task_id + '.log')
            jtl_file_path = os.path.join(target_file_path, task_id + '.jtl')
            if is_debug:
                res = os.popen(f'nohup {self.jmeter_executor} -n -t {jmx_file_path} -l {jtl_file_path} -j {log_path} &').read()
            else:
                res = os.popen(f'nohup {self.jmeter_executor} -n -t {jmx_file_path} -j {log_path} &').read()
            time.sleep(1)
            if self.check_status(is_run=True):
                self.status = 1
                self.task_id = task_id
                self.agent_num = agent_num
                flag = 1
                logger.info(f'{jmx_file_path} run successful, task id: {task_id}')
                self.start_thread(self.parse_log, (os.path.join(self.jmeter_file_path, task_id, task_id + '.log'),))
            else:
                flag = 0
                logger.error(f'{jmx_file_path} run failure, task id: {task_id}')
        except:
            flag = 0
            logger.error(traceback.format_exc())
        self.send_message('run_task', flag)

    def stop_task(self, task_id):
        flag = 1  # 0-stop task fail, 1-stop task success
        if self.check_status(is_run=True):
            try:
                self.kill_process()
                time.sleep(1)
                if self.check_status(is_run=False):
                    self.status = 0
                    self.task_id = None
                    flag = 1
                    del self.redis_client, self.influx_client
                    logger.info(f'task {task_id} stop successful ~')
                else:
                    flag = 0
                    logger.error(f'task {task_id} stop failure ~')
            except:
                flag = 0
                logger.error(traceback.format_exc())
        self.send_message('stop_task', flag)


    def kill_process(self):
        try:
            res = os.popen("ps -ef|grep jmeter |grep -v grep |awk '{print $2}' |xargs kill -9").read()
        except:
            logger.error(traceback.format_exc())

    def change_TPS(self, TPS):
        try:
            res = os.popen(f'java -jar {self.jmeter_path}/lib/bshclient.jar localhost 9000 {self.setprop_path} number_threads {TPS}').read()
            logger.info(f'Current TPS is {TPS}')
            return {'code': 0, 'msg': 'Change TPS successful ~'}
        except:
            logger.error(traceback.format_exc())
            return {'code': 1, 'msg': 'Change TPS failure ~'}

    def request_post(self, url, post_data):
        header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json; charset=UTF-8"}
        res = requests.post(url=url, json=post_data, headers=header)
        logger.info(url)
        return res

if __name__ == '__main__':
    # t = Task()
    RedisHost = '101.200.52.208'
    RedisPort = 6369
    RedisPassword = 'leeyoshi'
    RedisDB = 1
    r = redis.Redis(host=RedisHost, port=RedisPort, password=RedisPassword, db=RedisDB, decode_responses=True)
    a = r.lpush('task_1', str([8.0, 1.3, 389.0, 348.0, 453.0, 1.0, 200.0]))
    print(a)
    rr = r.lrange('task_1', 1, 2)
    print(rr)
