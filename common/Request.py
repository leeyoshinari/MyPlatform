#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: leeyoshinari

import requests


def get(host, interface, cookies=None, timeout=None):
    """get"""
    if timeout is None:
        timeout = 60

    headers = {
        'cookie': cookies
    }
    url = 'http://{}{}'.format(host, interface)
    res = requests.get(url=url, headers=headers, timeout=timeout)
    return res

def post(host, interface, json, cookies=None, timeout=None):
    """post"""
    if timeout is None:
        timeout = 60

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json; charset=UTF-8",
        "Cookie": cookies
    }

    url = 'http://{}{}'.format(host, interface)
    res = requests.post(url=url, json=json, headers=headers, timeout=timeout)
    return res

def post_form(url, data, cookies=None, timeout=None):
    if timeout is None:
        timeout = 60

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": cookies
    }

    res = requests.post(url=url, data=data, headers=headers, timeout=timeout)
    return res
