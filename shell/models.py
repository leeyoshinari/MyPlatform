#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

from django.db import models
from django.contrib.auth.models import Group

# Create your models here.

class ServerRoom(models.Model):
    id = models.CharField(max_length=16, primary_key=True, verbose_name='primary key')
    name = models.CharField(max_length=32, verbose_name='server room name')
    type = models.IntegerField(default=0, verbose_name='server room type. 0-use to application, 1-use to middleware, 2-use to pressure test')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()
    class Meta:
        db_table = 'server_room'


class GroupIdentifier(models.Model):
    id = models.CharField(max_length=16, primary_key=True, verbose_name='primary key')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='group id')
    key = models.CharField(max_length=32, verbose_name='group unique identifier')
    prefix = models.CharField(max_length=32, verbose_name='url path prefix')
    objects = models.Manager()
    class Meta:
        db_table = 'group_identifier'


class Servers(models.Model):
    id = models.CharField(max_length=16, primary_key=True, verbose_name='primary key')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='group id')
    room = models.ForeignKey(ServerRoom, on_delete=models.PROTECT, verbose_name='server rooom')
    name = models.CharField(max_length=64, verbose_name='server name')
    host = models.CharField(max_length=20, verbose_name='server IP')
    port = models.IntegerField(default=22, verbose_name='ssh port')
    user = models.CharField(max_length=25, verbose_name='ssh login username')
    pwd = models.CharField(max_length=64, verbose_name='ssh login password')
    system = models.CharField(max_length=64, verbose_name='system')
    cpu = models.IntegerField(default=0, verbose_name='cpu cores (logical core)')
    arch= models.CharField(max_length=10, verbose_name='system architecture')
    mem = models.FloatField(default=0.0, verbose_name='memory(G)')
    disk = models.CharField(max_length=8, verbose_name='disk')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    creator = models.CharField(max_length=50, verbose_name='creator')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'server'
        indexes = [models.Index(fields=['host'])]


class Packages(models.Model):
    id = models.CharField(max_length=16, primary_key=True, verbose_name='primary key')
    name = models.CharField(max_length=64, verbose_name='package name')
    type = models.CharField(max_length=16, verbose_name='package type, monitor-agent, jmeter-agent, java, jmeter')
    system = models.CharField(max_length=64, verbose_name='system')
    arch = models.CharField(max_length=10, verbose_name='system architecture')
    path = models.CharField(max_length=128, verbose_name='package store path')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='Create time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='Update time')
    operator = models.CharField(max_length=50, verbose_name='operator')
    objects = models.Manager()

    class Meta:
        db_table = 'packages'
