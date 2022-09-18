#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari


from django.http import JsonResponse

def result(code=0, msg=None, data=None):
    return JsonResponse({'code': code, 'msg': msg, 'data': data}, json_dumps_params={'ensure_ascii': False})


def json_result(data):
    return JsonResponse(data)
