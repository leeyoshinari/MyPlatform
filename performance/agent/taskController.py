#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
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
        self.jmeter_path = get_config('jmeterPath')
        self.jmeter_executor = os.path.join(self.jmeter_path, 'bin', 'jmeter')
        self.jmeter_file_path = os.path.join(self.jmeter_path, 'results')
        self.setprop_path = os.path.join(self.jmeter_path, 'setprop.bsh')

        self.influx_host = '127.0.0.1'
        self.influx_port = 8086
        self.influx_username = 'root'
        self.influx_password = '123456'
        self.influx_database = 'test'
        self.redis_host = '127.0.0.1'
        self.redis_port = 6379
        self.redis_password = '123456'
        self.redis_db = 0

        self.influx_client = None
        self.redis_client = None

        self.get_configure_from_server()

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
            else:
                logger.info('setprop.bsh has been exist ~')
        except:
            logger.error(traceback.format_exc())

    def modify_properties(self):
        properties_path = os.path.join(self.jmeter_path, 'bin', 'jmeter.properties')

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
            if self.status == -1:
                res = os.popen('ps -ef|grep jmeter').read()
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

    def write_data_to_influx(self):
        line = [{'measurement': self.IP,
                 'tags': {'type': str(self.task_id)},
                 'fields': {
                     'samples': 0.0,
                     'rt': 0.0,
                     'error': 0.0,
                     'tps': 0.0,
                 }}]
        self.influx_client.write_points(line)  # write to database

    def parse_log(self, log_path):
        while not os.path.exists(log_path):
            time.sleep(0.5)

        position = 0
        with open('access.log', mode='r', encoding='utf8') as f1:
            while True:
                line = f1.readline().strip()
                if 'summary' in line:
                    logger.info(f'JMeter run log - {self.task_id} - {line}')
                    datas = self.parse_str(line)

                cur_position = f1.tell()  # 记录上次读取文件的位置
                if cur_position == position:
                    time.sleep(0.1)
                    continue
                else:
                    position = cur_position
                    time.sleep(0.1)

    def parse_str(self, line):
        data = {'samples': 0, 'rt': 0, 'error': 0, 'tps': 0, 'total_samples': 0}
        return data

    def write_to_redis(self, data):
        pass

    def save_file(self, files):
        pass

    def upload_file_by_path(self, file_path):
        pass

    def upload_file_by_bytes(self, file_bytes):
        pass

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

    def run_task(self, task_id, file_path, agent_num):
        flag = 0    # 0-run task fail, 1-run task success
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
            html_file_path = os.path.join(target_file_path, 'html')
            jtl_file_path = os.path.join(target_file_path, 'jtl')
            res = os.popen(f'{self.jmeter_executor} -n -t {jmx_file_path} -l test_report1.csv -e -o {html_file_path}').read()
            time.sleep(1)
            if self.check_status(is_run=True):
                self.status = 1
                self.task_id = task_id
                self.agent_num = agent_num
                flag = 1
                logger.info(f'{jmx_file_path} run successful, task id: {task_id}')
            else:
                flag = 0
                logger.error(f'{jmx_file_path} run failure, task id: {task_id}')
        except:
            flag = 0
            logger.error(traceback.format_exc())
        self.send_message('run_task', flag)

    def stop_task(self, task_id):
        try:
            res = os.popen(f'ps -ef|grep jmete').read()
            time.sleep(1)
            if self.check_status(is_run=False):
                self.status = 0
                self.task_id = None
                del self.redis_client, self.influx_client
                logger.info(f'task {task_id} stop successful ~')
            else:
                logger.error(f'task {task_id} stop failure ~')
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
    t = Task()
    t.download_file_to_bytes('http://127.0.0.1:8000/tencent/static/files/1651999794686/工作簿1.csv')
