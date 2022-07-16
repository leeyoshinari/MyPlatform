#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

from django.db import models
from django.contrib.auth.models import Group

# Create your models here.
class Servers(models.Model):
    id = models.CharField(max_length=16, primary_key=True, verbose_name='主键')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='组名id')
    name = models.CharField(max_length=64, verbose_name='服务器名字')
    host = models.CharField(max_length=20, verbose_name='服务器ip')
    port = models.IntegerField(default=22, verbose_name='服务器 ssh 端口')
    user = models.CharField(max_length=25, verbose_name='ssh 登陆用户名')
    pwd = models.CharField(max_length=64, verbose_name='ssh 登陆密码')
    system = models.CharField(max_length=64, verbose_name='操作系统')
    cpu = models.IntegerField(default=0, verbose_name='服务器cpu核数（逻辑核）')
    arch= models.CharField(max_length=10, verbose_name='系统架构')
    mem = models.FloatField(default=0.0, verbose_name='服务器内存（单位G）')
    disk = models.CharField(max_length=8, verbose_name='磁盘大小')
    is_monitor = models.IntegerField(default=0, verbose_name='是否监控服务器使用情况')
    objects = models.Manager()

    class Meta:
        db_table = 'server'
        indexes = [models.Index(fields=['host'])]
