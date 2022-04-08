#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: leeyoshinari

import requests


class Request(object):
    def __init__(self):
        pass

    def get(self, ip, port, interface, timeout):
        """get"""
        url = 'http://{}:{}/{}'.format(ip, port, interface)
        res = requests.get(url=url, timeout=timeout)
        return res

    def post(self, ip, port, interface, json, headers, timeout):
        """post"""
        if headers is None:
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json; charset=UTF-8"}

        url = 'http://{}:{}/{}'.format(ip, port, interface)
        res = requests.post(url=url, json=json, headers=headers, timeout=timeout)
        return res

    def request(self, method, ip, port, interface, json=None, headers=None, timeout=None):
        try:
            if timeout is None:
                timeout = 3

            if method == 'get':
                res = self.get(ip, port, interface, timeout)
            elif method == 'post':
                res = self.post(ip, port, interface, json, headers, timeout)
            else:
                raise Exception('Other request methods are not supported!')

            return res
        except:
            raise

    def __del__(self):
        pass
