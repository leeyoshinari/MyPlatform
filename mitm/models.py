#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

from django.db import models
# Create your models here.

class Mitm(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='主键')
    name = models.CharField(null=True, max_length=50, verbose_name='规则名字')
    domain = models.CharField(null=True, max_length=50, verbose_name='域名或IP:PORT')
    url_path = models.CharField(null=True, max_length=100, verbose_name='url 路径')
    status_code = models.IntegerField(null=True, verbose_name='状态码')
    response = models.TextField(null=True, verbose_name='响应值')
    is_file = models.IntegerField(verbose_name='响应值是否是文件， 0 or 1')
    is_regular = models.IntegerField(verbose_name='拦截规则匹配方式')
    method = models.IntegerField(verbose_name='拦截方式，拦截请求 or 篡改数据')
    is_valid = models.IntegerField(verbose_name='是否启用规则')
    update_time = models.DateTimeField(verbose_name='更新时间')
    creator = models.CharField(max_length=50, verbose_name='创建人')
    modifier = models.CharField(max_length=50, verbose_name='修改人')
    objects = models.Manager()

    class Meta:
        db_table = 'mitmproxy'
