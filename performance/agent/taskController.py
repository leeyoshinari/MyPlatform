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
from common import get_config, logger, get_ip, toTimeStamp

bean_shell_server_port = 15225

class Task(object):
    def __init__(self):
        self.IP = get_ip()
        self.status = 0     # 0 idle, 1 busy, -1 pending
        self.current_tps = 0
        self.task_id = None
        self.task_key = None
        self.plan_id = None
        self.number_samples = 1
        self.start_time = 0
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
        # self.key_expire = 604800
        self.get_configure_from_server()

        self.jmeter_path = get_config('jmeterPath')
        self.jmeter_executor = os.path.join(self.jmeter_path, 'bin', 'jmeter')
        self.setprop_path = os.path.join(self.jmeter_path, 'setprop.bsh')
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')

        self.influx_client = None
        self.redis_client = None

        self.check_env()
        self.write_setprop()
        self.modify_properties()
        self.start_thread(self.register, ())

    def start_thread(self, func, data):
        t = threading.Thread(target=func, args=data)
        t.start()

    def check_env(self):
        if not os.path.exists(self.jmeter_path):
            logger.error(f'The Jmeter path: {self.jmeter_path} is not exist ~')

        res = os.popen(f'{self.jmeter_executor} -v').read()
        if 'Copyright' not in res:
            logger.error(f'Not Found JMeter ~')

        res = os.popen('whereis java').read()
        if len(res) < 10:
            logger.error('Not Found Java ~')

        if not os.path.exists(self.file_path):
            os.mkdir(self.file_path)

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
        _ = os.popen(f"sed -i 's|.*summariser.interval.*|summariser.interval=10|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*beanshell.server.port.*|beanshell.server.port={bean_shell_server_port}|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*beanshell.server.file.*|beanshell.server.file=../extras/startup.bsh|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*jmeter.save.saveservice.samplerData.*|jmeter.save.saveservice.samplerData=true|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*jmeter.save.saveservice.response_data.*|jmeter.save.saveservice.response_data=true|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*jmeter.save.saveservice.response_data.on_error.*|jmeter.save.saveservice.response_data.on_error=true|g' {properties_path}")
        _ = os.popen(f"sed -i 's|.*summariser.ignore_transaction_controller_sample_result.*|summariser.ignore_transaction_controller_sample_result=false|g' {properties_path}")
        _ = os.popen(f"sed -e 's/^M//g' {properties_path}")
        logger.info(f'Modify {properties_path} success ~')


    def get_configure_from_server(self):
        url = f'http://{get_config("address")}/performance/task/register'
        post_data = {
            'host': self.IP,
            'port': get_config('port'),
            'status': self.status,
            'tps': self.current_tps
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
                        self.key_expire =response_data['data']['key_expire']
                        break

                time.sleep(1)

            except:
                logger.error(traceback.format_exc())
                time.sleep(1)

    def register(self):
        url = f'http://{get_config("address")}/performance/task/register'
        while True:
            post_data = {
                'host': self.IP,
                'port': get_config('port'),
                'status': self.status,
                'tps': self.current_tps
            }
            res = self.request_post(url, post_data)
            logger.info(f"Agent register successful, status code is {res.status_code}, status: {self.status}, TPS: {self.current_tps}")
            time.sleep(9)

    def connect_influx(self):
        self.influx_client = influxdb.InfluxDBClient(self.influx_host, self.influx_port, self.influx_username,
                                                     self.influx_password, self.influx_database)

    def connect_redis(self):
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password,
                                        db=self.redis_db, decode_responses=True)

    def check_status(self, is_run=True):
        try:
            res = os.popen('ps -ef|grep jmeter |grep -v grep').readlines()
            if res and is_run:  # 是否启动成功
                return True
            elif not res and not is_run:    # 是否停止成功
                return True
            else:
                return False
        except:
            logger.error(traceback.format_exc())

    def force_stop_test(self, duration, schedule, run_type):
        stop_time = self.start_time + duration
        if schedule == 1 and run_type == 1:
            stop_time += 600
        while self.status == 1:
            if stop_time < time.time():
                self.stop_task(self.task_id)
            else:
                time.sleep(1)

    def send_message(self, task_type, flag):
        try:
            url = f'http://{get_config("address")}/performance/task/register/getMessage'
            post_data = {
                'host': self.IP,
                'taskId': self.task_id,
                'type': task_type,
                'data': flag
            }
            res = self.request_post(url, post_data)
            response = json.loads(res.content.decode())
            if response['code'] == 0:
                logger.info(f"Send message successful, data: {post_data}, response: {response}")
                return True
            else:
                logger.error(f"Send message failure, msg: {response['msg']}")
                return False
        except:
            logger.error("Send message failure ~")
            return False

    def write_to_influx(self, datas):
        d = [json.loads(r) for r in datas]
        data = [sum(r) for r in zip(*d)]
        line = [{'measurement': 'performance_jmeter_task',
                 'tags': {'task': str(self.task_id), 'host': 'all'},
                 'fields': {'c_time': time.strftime("%Y-%m-%d %H:%M:%S"), 'samples': data[0], 'tps': data[1],
                            'avg_rt': data[2], 'min_rt': data[3], 'max_rt': data[4], 'err': data[5], 'active': data[6]}}]
        self.influx_client.write_points(line)  # write to database

    def parse_log(self, log_path):
        while not os.path.exists(log_path):
            time.sleep(0.5)

        position = 0
        index = 0
        with open(log_path, mode='r', encoding='utf-8') as f1:
            while True:
                line = f1.readline().strip()
                if 'Summariser: summary +' in line:
                    logger.info(f'JMeter run log - {self.task_id} - {line}')
                    if index > 1:   # 前两次结果不写入，等待summary输出频率稳定
                        self.redis_client.set(f'{self.task_id}_host_{self.IP}', 1, ex=30)
                        c_time = line.split(',')[0].strip()
                        res = re.findall(self.pattern, line.replace(' ', ''))[0]
                        logger.debug(res)
                        self.current_tps = res[1]
                        data = list(map(float, res))
                        self.write_to_redis(data)
                        lines = [{'measurement': 'performance_jmeter_task',
                                 'tags': {'task': str(self.task_id), 'host': self.IP},
                                 'fields': {'c_time': c_time, 'samples': data[0], 'tps': data[1], 'avg_rt': data[2],
                                            'min_rt': data[3], 'max_rt': data[4], 'err': data[5], 'active': data[6]}}]
                        self.influx_client.write_points(lines)  # write to database
                        if res[-1] == '0':
                            self.start_thread(self.stop_task, (self.task_id,))
                            break
                        index += 1
                        last_time = time.time()
                    else:
                        self.change_init_TPS()
                        index += 1

                if index > 10 and time.time() - last_time > 300:
                    self.status = 0

                if self.status == 0:
                    self.start_thread(self.stop_task, (self.task_id,))
                    break

                cur_position = f1.tell()  # 记录上次读取文件的位置
                if cur_position == position:
                    time.sleep(0.2)
                    continue
                else:
                    position = cur_position
                    time.sleep(0.2)

    def write_to_redis(self, data):
        total_num = len(self.redis_client.keys(self.task_id + '_host_*'))
        if self.redis_client.llen(self.task_key) == total_num:
            res = self.redis_client.lrange(self.task_key, 0, total_num - 1)
            self.redis_client.ltrim(self.task_key, total_num + 1, total_num + 1)  # remove all
            self.write_to_influx(res)
        _ = self.redis_client.lpush(self.task_key, str(data))
        if self.redis_client.llen(self.task_key) == total_num:
            res = self.redis_client.lrange(self.task_key, 0, total_num - 1)
            self.redis_client.ltrim(self.task_key, total_num + 1, total_num + 1)  # remove all
            self.write_to_influx(res)
        self.redis_client.expire(self.task_key, 300)

    def save_file(self, files):
        pass

    def upload_file_by_path(self, file_path):
        pass

    def upload_file_by_bytes(self, file_bytes):
        pass

    def download_log(self, task_id):
        jtl_path = os.path.join(self.file_path, task_id, task_id + '.jtl')
        jmeter_log_path = os.path.join(self.file_path, task_id, task_id + '.log')
        zip_file_path = os.path.join(self.file_path, task_id, task_id + '.zip')
        archive = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
        if os.path.exists(jtl_path):
            archive.write(jtl_path, task_id + '.jtl')
        archive.write(jmeter_log_path, task_id + '.log')
        archive.close()
        logger.info(f'JMeter log file download success, filePath: {zip_file_path}')
        with open(zip_file_path, 'rb') as f:
            res = f.read()
        os.remove(zip_file_path)
        return res

    def download_file_to_path(self, url, file_path):
        with open(file_path, 'wb') as f:
            f.write(self.download_file_to_bytes(url))
        logger.info(f'Download file: {url} to {file_path} success ~')

    def download_file_to_bytes(self, url):
        res = requests.get(url)
        return res.content

    def unzip_file(self, source_path, target_path):
        f = zipfile.ZipFile(source_path)
        f.extractall(target_path)
        f.close()
        logger.info(f'unzip file: {source_path} to {target_path} success ~')

    def run_task(self, data):
        if self.check_status(is_run=True):
            self.kill_process()

        task_id = data.get('taskId')
        #flag = 0    # 0-run task fail, 1-run task success
        try:
            self.connect_redis()
            self.connect_influx()
            local_file_path = os.path.join(self.file_path, task_id + '.zip')
            target_file_path = os.path.join(self.file_path, task_id)
            self.download_file_to_path(data.get('filePath'), local_file_path)
            self.unzip_file(local_file_path, target_file_path)
            if not os.path.exists(target_file_path):
                logger.error('Not Found file after unzip')
                return {'code': 1, 'msg': 'Not Found file after unzip'}
            jmx_files = [file for file in os.listdir(target_file_path) if file.endswith('.jmx')]
            if not jmx_files:
                logger.error('Not Found jmx file ~')
                return {'code': 1, 'msg': 'Not Found jmx file, please zip file again ~'}
            jmx_file_path = os.path.join(target_file_path, jmx_files[0])
            log_path = os.path.join(target_file_path, task_id + '.log')
            jtl_file_path = os.path.join(target_file_path, task_id + '.jtl')
            if data.get('isDebug') == 1:
                cmd = f'nohup {self.jmeter_executor} -n -t {jmx_file_path} -l {jtl_file_path} -j {log_path} >/dev/null 2>&1 &'
            else:
                cmd = f'nohup {self.jmeter_executor} -n -t {jmx_file_path} -j {log_path} >/dev/null 2>&1 &'
            res = os.popen(cmd).read()
            logger.info(f'Run JMeter success, shell: {cmd}')
            time.sleep(5)
            if self.check_status(is_run=True):
                self.status = 1
                self.task_id = task_id
                self.task_key = f"task_{task_id}"
                self.number_samples = data.get('numberSamples')
                self.start_time = time.time()
                flag = 1
                logger.info(f'{jmx_file_path} run successful, task id: {self.task_id}')
                self.start_thread(self.parse_log, (os.path.join(self.file_path, self.task_id, self.task_id + '.log'),))
                if data.get('schedule') == 1 and data.get('type') == 1:
                    self.start_thread(self.auto_change_tps, (data.get('timeSetting'), data.get('targetNum'),))
                self.start_thread(self.force_stop_test, (data.get('duration'), data.get('schedule'), data.get('type'),))
            else:
                flag = 0
                logger.error(f'{jmx_file_path} run failure, task id: {task_id}')
        except:
            flag = 0
            logger.error(traceback.format_exc())
        if flag == 1:
            _ = self.send_message('run_task', flag)

    def stop_task(self, task_id):
        flag = 1  # 0-stop task fail, 1-stop task success
        if self.check_status(is_run=True):
            try:
                self.kill_process()
                time.sleep(2)
                if self.check_status(is_run=False):
                    self.status = 0
                    self.current_tps = 0
                    self.number_samples = 1
                    flag = 1
                    del self.redis_client, self.influx_client
                    logger.info(f'task {task_id} stop successful ~')
                else:
                    logger.error(f'task {task_id} stop failure ~')
                    return False
            except:
                logger.error(traceback.format_exc())
                return False
        else:
            logger.error(f'task {task_id} has stopped ~')

        if self.send_message('stop_task', flag):
            return True
        else:
            return False

    def kill_process(self):
        try:
            res = os.popen("ps -ef|grep jmeter |grep -v grep |awk '{print $2}' |xargs kill -9").read()
        except:
            logger.error(traceback.format_exc())

    def change_TPS(self, TPS):
        try:
            cmd = f'java -jar {self.jmeter_path}/lib/bshclient.jar localhost {bean_shell_server_port} {self.setprop_path} throughput {TPS}'
            res = os.popen(cmd).read()
            logger.info(f'Change TPS to {TPS}, CMD: {cmd}')
            return {'code': 0, 'msg': 'Change TPS successful ~'}
        except:
            logger.error(traceback.format_exc())
            return {'code': 1, 'msg': 'Change TPS failure ~'}

    def auto_change_tps(self, time_setting, target_num):
        scheduler = []
        for s in time_setting:
            scheduler.append({'timing': toTimeStamp(s['timing']), 'value': float(s['value'])})

        while scheduler:
            s = scheduler[0]
            if s['timing'] < time.time():
                _ = self.change_TPS(int(target_num * self.number_samples * s['value'] * 0.6 / len(self.redis_client.keys(self.task_id + '_host_*'))))
                scheduler.pop(0)
            time.sleep(0.1)
        logger.info(f'Task {self.task_id} auto change TPS is completed ~')


    def change_init_TPS(self):
        try:
            tps = 120 * self.number_samples
            _ = self.change_TPS(tps)
        except:
            logger.error(traceback.format_exc())

    def request_post(self, url, post_data):
        header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json; charset=UTF-8"}
        res = requests.post(url=url, json=post_data, headers=header)
        logger.debug(url)
        return res

if __name__ == '__main__':
    RedisHost = '101.200.52.208'
    RedisPort = 6369
    RedisPassword = 'leeyoshi'
    RedisDB = 1
    r = redis.Redis(host=RedisHost, port=RedisPort, password=RedisPassword, db=RedisDB, decode_responses=True)
    print(r.get('123'))

