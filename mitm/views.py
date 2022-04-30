#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari


from django.shortcuts import render
from .models import Mitm

# Create your views here.


def home(request):
    if request.method == 'GET':
        datas = Mitm.objects.all().order_by('-update_time')
        return render(request, 'mitm/home.html', context={'datas': datas, 'types': ["直接拦截请求", "篡改请求或响应", "篡改响应值", "请求响应都篡改"]})
