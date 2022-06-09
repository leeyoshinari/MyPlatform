#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
from django.template import Library


register = Library()


@register.filter
def get_list(v1, v2):
    try:
        return v1[v2]
    except:
        return None


@register.filter
def get_argument_type(v1):
    try:
        if v1.get("request_body_json"):
            return 'json'
        else:
            return 'form'
    except:
        return 'json'


# @register.filter
# def get_value(v1):
#     try:
#         if v1.get("request_body_json"):
#             return 'json'
#         else:
#             return 'form'
#     except:
#         return 'json'


@register.filter
def get_value_from_list(v1, v2):
    try:
        if v2 == 'plan_type':
            return ['Thread', 'TPS'][v1]
        if v2 == 'plan_schedule':
            return ['Regular', 'Crontab'][v1]
        if v2 == 'task_status':
            return ['Pending', 'Running', 'Success', 'Stopped', 'Failure'][v1]
        if v2 == 'task_color':
            return ['gray', 'blue', 'green', 'orange', 'red'][v1]
        if v2 == 'server_color':
            return ['gray', 'green', 'red'][v1]
        if v2 == 'server_status':
            return ['gray', 'Idle', 'Busy'][v1]
    except:
        return None


@register.filter
def multiple(v1, v2):
    try:
        return int(v1 * v2 / 100)
    except:
        return 0


@register.filter
def parse_url_name(v1):
    return v1.split('/')[-1]