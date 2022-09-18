#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

class MyException(Exception):
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return self.msg
