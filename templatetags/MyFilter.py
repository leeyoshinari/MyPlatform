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
    except:
        return None
