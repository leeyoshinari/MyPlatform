#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import threading


def start_thread(func, data):
    t = threading.Thread(target=func, args=data)
    t.start()
