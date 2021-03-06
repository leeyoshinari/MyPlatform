#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import re
import time
import json
import logging.handlers
import traceback
import threading
import urllib.parse
import redis
import mitmproxy.http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import ctx, http

# ---------- start configure -----------------------
# MitmProxy configure
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 12021

# Redis configure
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = '123456'
REDIS_DB = 1

# log configure
LEVEL = 'INFO'
log_path = 'logs'
# ---------- end configure -----------------------

if not os.path.exists(log_path):
    os.mkdir(log_path)

log_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s:%(thread)d - %(filename)s[line:%(lineno)d] - %(message)s')
logger.setLevel(level=log_level.get(LEVEL))
current_day = time.strftime('%Y-%m-%d')
log_name = os.path.join(log_path, current_day + '.log')
file_handler = logging.handlers.RotatingFileHandler(filename=log_name, maxBytes=10*1024*1024, backupCount=10)
# file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class RequestEvent(object):
    def __init__(self):
        self._data = []
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB,
                             decode_responses=True)

        thread_01 = threading.Thread(target=self.get_from_redis)
        thread_01.setDaemon(True)
        thread_01.start()

    def get_from_redis(self):
        while True:
            time.sleep(2)
            if not self.r.get('mitmproxy'):
                continue
            self._data = json.loads(self.r.get('mitmproxy'))
            logger.info(self._data)
            self.r.delete('mitmproxy')


    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        pass

    def request(self, flow: mitmproxy.http.HTTPFlow):
        request_dict = {'url': '', 'method': '', 'scheme': '', 'hostname': '', 'port': 80, 'path': '',
                        'query': '', 'data': '', 'fragment': '', 'origin_data': ''}

        url_parse = urllib.parse.urlparse(flow.request.url)      # ??????url
        request_dict['url'] = flow.request.url
        request_dict['method'] = flow.request.method  # ????????????
        request_dict['scheme'] = url_parse.scheme   # ??????
        request_dict['hostname'] = url_parse.hostname   # ??????
        request_dict['port'] = flow.request.port    # ??????
        request_dict['path'] = url_parse.path  # ????????????

        logger.info(f'{request_dict["scheme"]} - {request_dict["method"]} - {request_dict["hostname"]}:'
                    f'{request_dict["port"]} - {request_dict["path"]}')

        result = self.intercept(request_dict)
        if result['flag']:  # http????????????????????????
            if result['rule_data']['fields']['method'] == 0: # ????????????
                request_dict['query'] = self.decode_query(urllib.parse.unquote(url_parse.query))  # URL??????????????????
                request_dict['fragment'] = url_parse.fragment
                data = flow.request.get_text()
                request_dict['data'] = self.decode_data(data) if data else data  # post???????????????
                logger.debug(f"URL??????????????????????????????????????????{request_dict['query']}")
                logger.debug(f"POST?????????????????????????????????????????????{request_dict['data']}")

                data = self.return_response(result['rule_data'], request_dict)
                flow.response = http.Response.make(status_code=data['status_code'], content=data['content'])
                logger.info(f"{request_dict['url']} ??????????????????")

            if result['rule_data']['fields']['method'] == 1:  # ??????????????????
                request_dict['origin_data'] = flow.request.get_text()
                url, data = self.falsify_request(result['rule_data']['fields']['response'], request_dict)
                flow.request.url = url
                flow.request.text = data
                logger.info(f"{request_dict['url']} ???????????????????????????")

    def response(self, flow: mitmproxy.http.HTTPFlow):
        response_dict = {'url': '', 'hostname': '', 'path': '', 'data': ''}
        url_parse = urllib.parse.urlparse(flow.request.url)  # ??????url
        response_dict['url'] = flow.request.url
        response_dict['hostname'] = url_parse.hostname  # ??????
        response_dict['path'] = url_parse.path  # ????????????

        result = self.intercept(response_dict)
        if result['flag']:  # http????????????????????????
            if result['rule_data']['fields']['method'] == 1:  # ???????????????
                response_dict['data'] = flow.response.get_text()
                data = self.falsify_response(result['rule_data']['fields']['response'], response_dict)
                flow.response.text = data
                logger.info(f"{response_dict['url']} ????????????????????????")

    def intercept(self, request_dict):
        """
        ??????
        :param request_dict:
        :return:
        """
        flag = 0    # Whether match mitm rule
        index = 0
        try:
            for i in range(len(self._data)):
                rule = self._data[i]
                index = i
                if rule['fields']['domain'] and rule['fields']['url_path']:
                    if self.recompile(rule['fields']['domain'], request_dict["hostname"], is_re=rule['fields']['is_regular']):
                        flag = 1
                        break
                    elif self.recompile(rule['fields']['url_path'], request_dict["path"], is_re=rule['fields']['is_regular']):
                        flag = 1
                        break
                    else:
                        continue
                elif rule['fields']['domain'] and not rule['fields']['url_path']:
                    if self.recompile(rule['fields']['domain'], request_dict["hostname"], is_re=rule['fields']['is_regular']):
                        flag = 1
                        break
                elif rule['fields']['url_path'] and not rule['fields']['domain']:
                    if self.recompile(rule['fields']['url_path'], request_dict["path"], is_re=rule['fields']['is_regular']):
                        flag = 1
                        break
                else:
                    continue
        except Exception:
            logger.error(traceback.format_exc())

        return {"flag": flag, "rule_data": self._data[index] if flag else None}

    def return_response(self, rule_data, request_dict):
        status_code = rule_data['fields']['status_code']
        if not status_code:
            status_code = 200

        try:
            if rule_data['fields']['is_file'] == 1:
                with open(rule_data['fields']['response'], 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = rule_data['fields']['response']
            try:
                content = json.dumps(self.replace_param(json.loads(content), request_dict))
            except:
                logger.error(traceback.format_exc())

        except Exception as err:
            logger.error(traceback.format_exc())
            status_code = 500
            content = str(err)

        return {'status_code': status_code, 'content': content}

    def falsify_request(self, fields, request_dict):
        """
        ??????????????????
        :param fields: ?????????????????????
        :param request_dict: ???????????????????????????
        :return:
        """
        try:
            fields = json.loads(fields)
            url_dict = fields.get('requestUrl')
            body_dict = fields.get('requestBody')
            if url_dict:
                for k, v in url_dict.items():
                    url = self.tamper_url(k, urllib.parse.quote(v), request_dict['url'])
                    request_dict['url'] = url

            if body_dict:
                for k, v in body_dict.items():
                    data = self.tamper_body(k, v, request_dict['origin_data'])
                    request_dict['origin_data'] = data
        except:
            logger.error(traceback.format_exc())

        return request_dict['url'], request_dict['origin_data']

    def tamper_url(self, key, value, url):
        pattern = f'{key}=(.*?)&|{key}=(.*?)+'
        url = re.sub(pattern, f'{key}={value}&', url)
        return url

    def tamper_body(self, key, value, data, is_request = True):
        try:
            data_dic = json.loads(data)
            keys = [self.str_2_num(k) for k in key.split('.')]
            self.get_dict(keys, value, data_dic)
            return json.dumps(data_dic)
        except:
            if is_request:
                logger.warning(f"POST???????????????????????????{data}")
                return self.tamper_url(key, value, data)
            else:
                logger.warning(f"???????????????Json?????????{data}")
                return data

    def falsify_response(self, fields, response_dict):
        """
        ???????????????
        :param fields: ?????????????????????
        :param response_dict: ?????????
        :return:
        """
        try:
            fields = json.loads(fields)
            res_dict = fields.get('responseBody')
            if res_dict:
                for k, v in res_dict.items():
                    data = self.tamper_body(k, v, response_dict['data'], is_request=False)
                    response_dict['data'] = data
        except:
            logger.error(traceback.format_exc())
        return response_dict['data']

    def get_dict(self, keys, value, data):
        if len(keys) == 1:
            data[keys[0]] = value
        else:
            k = keys.pop(0)
            try:
                return self.get_dict(keys, value, data[k])
            except:
                logger.error(traceback.format_exc())
                data[k] = value

    @staticmethod
    def str_2_num(value: str):
        try:
            return int(value)
        except Exception as err:
            return value

    @staticmethod
    def replace_param(content, request_dict):
        """
        ??????mock??????????????????????????????????????????????????????????????????
        - ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        - ??????????????????ID?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        :param content: ???????????????????????????????????? dict or list
        :param request_dict: ?????????????????????request_dict['hostname'] ?????????
                request_dict['path'] ???????????????
                request_dict['query'] ???URL?????????????????????GET???POST?????????????????????
                request_dict['data'] ???POST???????????????
        :return: ?????????????????????
        """
        try:
            if request_dict['path'] == '':
                # ???????????? ??????????????????????????????
                pass
        except:
            logger.error(traceback.format_exc())

        return content

    @staticmethod
    def decode_query(query: str):
        data = {}
        if not query:
            return data
        params = query.split('&')
        for param in params:
            k, v = param.split('=')
            data.update({k: v})

        return data

    def decode_data(self, data: str):
        try:
            return json.loads(data)
        except Exception as err:
            logger.error(f'{err} -- {data}')
            # logger.error(traceback.format_exc())
            return self.decode_query(data)

    @staticmethod
    def recompile(pattern, string, is_re = 1):
        if is_re:
            res = re.search(pattern, string)
            if res:
                return True
            else:
                return False
        else:
            return pattern == string


class ProxyMaster(DumpMaster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_run(self):
        try:
            DumpMaster.run(self)
        except KeyboardInterrupt:
            self.shutdown()


def start_proxy():
    options = Options(listen_host=PROXY_HOST, listen_port=PROXY_PORT, http2=True)
    proxy = ProxyMaster(options, with_termlog=False, with_dumper=False)
    r_e = RequestEvent()
    proxy.addons.add(r_e)
    proxy.start_run()


if __name__ == '__main__':
    start_proxy()
