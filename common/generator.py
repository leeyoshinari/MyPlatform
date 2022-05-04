#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
import random


def primaryKey():
    return int(time.time() * 1000)


def strfTime():
    return time.strftime('%Y-%m-%d %H:%M:%S')
