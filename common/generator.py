#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import datetime


def primaryKey():
    return int(time.time() * 10000)


def strfTime():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def strfDeltaTime(delta = 0):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + delta))


def toTimeStamp(strf_time, delta = 0):
    return time.mktime(time.strptime(strf_time, '%Y-%m-%d %H:%M:%S')) + delta


def utc2local(utc_time: str, gmt: int):
    """
    UTC time to local time.
    UTC time format: 2020-02-02T02:02:02.202002Z, formatting UTC timestamp according to "%Y-%m-%dT%H:%M:%S.%fZ".
    :param utc_time: UTC time
    :param gmt: time zone
    :return: local time
    """
    local_format = "%Y-%m-%d %H:%M:%S"
    # The format "%Y-%m-%dT%H:%M:%S.%fZ" only match 6 decimal places, if it is greater than 6 digits,
    # it needs to be divided by ".", and then converted.
    # utc_format = "%Y-%m-%dT%H:%M:%S"
    # local_time = datetime.datetime.strptime(utc_time.split('.')[0], utc_format) + datetime.timedelta(hours=8)
    utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"    # The format "%Y-%m-%dT%H:%M:%S.%fZ" only match 6 decimal places
    local_time = datetime.datetime.strptime(utc_time, utc_format) + datetime.timedelta(hours=gmt)
    return local_time.strftime(local_format)


def local2utc(local_time: str, gmt: int):
    """
    Local time to UTC time
    :param local_time: local time
    :param gmt: time zone
    :return: UTC time
    """
    local_format = "%Y-%m-%d %H:%M:%S"
    utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    utc_time = datetime.datetime.strptime(local_time, local_format) - datetime.timedelta(hours=gmt)
    return utc_time.strftime(utc_format)
