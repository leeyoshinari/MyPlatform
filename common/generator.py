#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time


def primaryKey():
    return int(time.time() * 10000)


def strfTime():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def strfDeltaTime(delta = 0):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - delta))


def toTimeStamp(strf_time):
    return time.mktime(time.strptime(strf_time, '%Y-%m-%d %H:%M:%S'))
