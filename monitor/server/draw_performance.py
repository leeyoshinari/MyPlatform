#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: leeyoshinari
import time
import logging
import traceback
from django.conf import settings
from common.generator import strfDeltaTime, local2utc, utc2local, toTimeStamp

logger = logging.getLogger('django')

def draw_data_from_db(room, group, host, startTime=None, endTime=None):
    """
    Get data from InfluxDB, and visualize
    :param host: client IP, required
    :param startTime: Start time; optional
    :param endTime: end time; optional
    :return:
    """
    post_data = {
        'time': '',
        'cpu_time': [],
        'cpu': [],
        'iowait': [],
        'usr_cpu': [],
        'mem': [],
        'mem_available': [],
        'jvm': [],
        'disk': [],
        'disk_r': [],
        'disk_w': [],
        'disk_d': [],
        'rec': [],
        'trans': [],
        'net': [],
        'tcp': [],
        'retrans': [],
        'port_tcp': [],
        'close_wait': [],
        'time_wait': [],
    }

    res = {'code': 0, 'flag': 1, 'msg': 'Successful!'}

    try:
        if not startTime:     # If there is a start time and an end time
            startTime = strfDeltaTime(-600)
        if 'T' not in startTime:
            startTime = local2utc(startTime, settings.GMT)

        s_time = time.time()
        if host != 'all':
            if endTime:
                endTime = local2utc(endTime, settings.GMT)
                sql = f"select c_time, cpu, iowait, usr_cpu, mem, mem_available, jvm, disk, disk_r, disk_w, disk_d, rec, trans, " \
                      f"net, tcp, retrans, port_tcp, close_wait, time_wait from \"server_{group}\" where room='{room}' and host='{host}' and time>='{startTime}' " \
                      f"and time<'{endTime}';"
            else:
                sql = f"select c_time, cpu, iowait, usr_cpu, mem, mem_available, jvm, disk, disk_r, disk_w, disk_d, rec, trans, " \
                      f"net, tcp, retrans, port_tcp, close_wait, time_wait from \"server_{group}\" where room='{room}' and host='{host}' and time>='{startTime}';"
        else:
            if endTime:
                endTime = local2utc(endTime, settings.GMT)
                sql = f"select first(c_time) as c_time, mean(cpu) as cpu, mean(iowait) as iowait, mean(usr_cpu) as usr_cpu, mean(mem) as mem, mean(mem_available) as mem_available, " \
                      f"mean(jvm) as jvm, mean(disk) as disk, mean(disk_r) as disk_r, mean(disk_w) as disk_w, mean(disk_d) as disk_d, mean(rec) as rec, mean(trans) as trans, " \
                      f"mean(net) as net, mean(tcp) as tcp, mean(retrans) as retrans, mean(port_tcp) as port_tcp, mean(close_wait) as close_wait, mean(time_wait) as time_wait " \
                      f"from \"server_{group}\" where room='{room}' and time>='{startTime}' and time<'{endTime}' group by time({settings.SAMPLING_INTERVAL}s) fill(linear);"
            else:
                sql = f"select first(c_time) as c_time, mean(cpu) as cpu, mean(iowait) as iowait, mean(usr_cpu) as usr_cpu, mean(mem) as mem, mean(mem_available) as mem_available, " \
                      f"mean(jvm) as jvm, mean(disk) as disk, mean(disk_r) as disk_r, mean(disk_w) as disk_w, mean(disk_d) as disk_d, mean(rec) as rec, mean(trans) as trans, " \
                      f"mean(net) as net, mean(tcp) as tcp, mean(retrans) as retrans, mean(port_tcp) as port_tcp, mean(close_wait) as close_wait, mean(time_wait) as time_wait " \
                      f"from \"server_{group}\" where room='{room}' and time>='{startTime}' group by time({settings.SAMPLING_INTERVAL}s) fill(linear);"
        logger.info(f'Execute sql: {sql}')
        last_time = startTime
        datas = settings.INFLUX_CLIENT.query(sql)
        if datas:
            for data in datas.get_points():
                if data['time'] == startTime: continue
                if data['c_time']:
                    post_data['cpu_time'].append(data['c_time'])
                    last_time = data['time']
                else:
                    continue
                post_data['cpu'].append(data['cpu'])
                post_data['iowait'].append(data['iowait'])
                # post_data['usr_cpu'].append(data['usr_cpu'])
                post_data['mem'].append(data['mem'])
                post_data['mem_available'].append(data['mem_available'])
                post_data['jvm'].append(data['jvm'])
                post_data['disk'].append(data['disk'])
                post_data['disk_r'].append(data['disk_r'])
                post_data['disk_w'].append(data['disk_w'])
                # post_data['disk_d'].append(data['disk_d'])
                post_data['rec'].append(data['rec'])
                post_data['trans'].append(data['trans'])
                post_data['net'].append(data['net'])
                post_data['tcp'].append(data['tcp'])
                post_data['retrans'].append(data['retrans'])
                post_data['port_tcp'].append(data['port_tcp'])
                post_data['close_wait'].append(data['close_wait'])
                post_data['time_wait'].append(data['time_wait'])
            post_data['time'] = last_time

        else:
            res['msg'] = 'No monitoring data is found, please check the time setting.'
            res['code'] = 1

        res.update({'post_data': post_data})
        logger.info(f'Time consuming to query is {time.time() - s_time}')

    except Exception as err:
        logger.error(traceback.format_exc())
        res['msg'] = str(err)
        res['code'] = 1

    del post_data
    return res


def get_lines(datas):
    """
    Calculate percentile
    :param datas
    :return:
    """
    cpu = datas['cpu']
    disk_r = datas['disk_r'] if datas['disk_r'] else [-1]
    disk_w = datas['disk_w'] if datas['disk_w'] else [-1]
    io = datas['io']
    rec = datas['rec'] if datas['rec'] else [-1]
    trans = datas['trans'] if datas['trans'] else [-1]
    nic = datas['nic']

    cpu.sort()
    disk_r.sort()
    disk_w.sort()
    io.sort()
    rec.sort()
    trans.sort()
    nic.sort()

    line75 = [round(cpu[int(len(cpu) * 0.75)], 2), round(disk_r[int(len(disk_r) * 0.75)], 2),
              round(disk_w[int(len(disk_w) * 0.75)], 2), round(io[int(len(io) * 0.75)], 3),
              round(rec[int(len(rec) * 0.75)], 2), round(trans[int(len(trans) * 0.75)], 2),
              round(nic[int(len(nic) * 0.75)], 3)]
    line90 = [round(cpu[int(len(cpu) * 0.9)], 2), round(disk_r[int(len(disk_r) * 0.9)], 2),
              round(disk_w[int(len(disk_w) * 0.9)], 2), round(io[int(len(io) * 0.9)], 3),
              round(rec[int(len(rec) * 0.9)], 2), round(trans[int(len(trans) * 0.9)], 2),
              round(nic[int(len(nic) * 0.9)], 3)]
    line95 = [round(cpu[int(len(cpu) * 0.95)], 2), round(disk_r[int(len(disk_r) * 0.95)], 2),
              round(disk_w[int(len(disk_w) * 0.95)], 2), round(io[int(len(io) * 0.95)], 3),
              round(rec[int(len(rec) * 0.95)], 2), round(trans[int(len(trans) * 0.95)], 2),
              round(nic[int(len(nic) * 0.95)], 3)]
    line99 = [round(cpu[int(len(cpu) * 0.99)], 2), round(disk_r[int(len(disk_r) * 0.99)], 2),
              round(disk_w[int(len(disk_w) * 0.99)], 2), round(io[int(len(io) * 0.99)], 3),
              round(rec[int(len(rec) * 0.99)], 2), round(trans[int(len(trans) * 0.99)], 2),
              round(nic[int(len(nic) * 0.99)], 3)]

    return {'line': [line75, line90, line95, line99]}


def query_nginx_detail_summary(group_key, source, order_key, order_by, start_time, end_time, limit_num, path):
    res = {'code': 0, 'msg': 'Successful!'}
    try:
        post_data = []
        if not start_time:
            start_time = strfDeltaTime(-600)
        if not end_time:
            end_time = strfDeltaTime()
        if 'T' not in start_time:
            start_time = local2utc(start_time, settings.GMT)
        if 'T' not in end_time:
            end_time = local2utc(end_time, settings.GMT)
        s_time = time.time()
        if path:
            path = path.replace('/', '\/')
            sql = f"select count(rt) as sample, mean(rt) as rt, sum(size) as size, sum(error) as error from nginx_{group_key} " \
                  f"where source='{source}' and path=~/{path}/ and time > '{start_time}' and time < '{end_time}' group by path;"
        else:
            sql = f"select count(rt) as sample, mean(rt) as rt, sum(size) as size, sum(error) as error from nginx_{group_key} " \
                  f"where source='{source}' and time > '{start_time}' and time < '{end_time}' group by path;"
        logger.info(f'Execute sql: {sql}')
        datas = settings.INFLUX_CLIENT.query(sql)
        if datas:
            duration = toTimeStamp(utc2local(end_time, settings.GMT)) - toTimeStamp(utc2local(start_time, settings.GMT))
            for data in datas._get_series():
                post_data.append({'path': data.get('tags').get('path'), 'sample': data.get('values')[0][1], 'qps': data.get('values')[0][1]/duration, 'rt': data.get('values')[0][2], 'size': data.get('values')[0][3]/1048576, 'error': data.get('values')[0][4]})
        else:
            res['msg'] = 'No Nginx summary data is found, please check it again.'
            res['code'] = 1
        post_data.sort(key=lambda x: (-x[order_key]))
        res.update({'data': post_data[:limit_num]})
        logger.info(f'Time consuming to query is {time.time() - s_time}')
    except:
        logger.error(traceback.format_exc())
        res['msg'] = 'Query Nginx summary data error, please check it again ~'
        res['code'] = 1

    del post_data
    return res


def query_nginx_detail_by_path(group_key, source, path, start_time, end_time):
    post_data = {
        'time': '',
        'c_time': [],
        'qps': [],
        'rt': [],
        'size': [],
        'error': []
    }
    res = {'code': 0, 'msg': 'Successful!'}
    try:
        if not start_time:
            start_time = strfDeltaTime(-600)
        if not end_time:
            end_time = strfDeltaTime()
        if 'T' not in start_time:
            start_time = local2utc(start_time, settings.GMT)
        end_time = local2utc(end_time, settings.GMT)
        s_time = time.time()
        sql = f"select first(c_time) as c_time, count(rt) as qps, mean(rt) as rt, sum(size) as size, sum(error) as error from nginx_{group_key} " \
              f"where source='{source}' and path='{path}' and time > '{start_time}' and time < '{end_time}' group by time(1s) fill(linear);"
        logger.info(f'Execute sql: {sql}')
        last_time = start_time
        datas = settings.INFLUX_CLIENT.query(sql)
        if datas:
            for data in datas.get_points():
                if data['time'] == start_time: continue
                if data['c_time']:
                    post_data['c_time'].append(data['c_time'])
                    last_time = data['time']
                else:
                    continue
                post_data['qps'].append(data['qps'])
                post_data['rt'].append(data['rt'])
                post_data['size'].append(data['size']/1048576)
                post_data['error'].append(data['error'])
            post_data['time'] = last_time
        else:
            res['msg'] = 'No Nginx data is found, please check it again.'
            res['code'] = 1
        res.update({'data': post_data})
        logger.info(f'Time consuming to query is {time.time() - s_time}')
    except:
        logger.error(traceback.format_exc())
        res['msg'] = 'Query Nginx data error, please check it again ~'
        res['code'] = 1

    del post_data
    return res
