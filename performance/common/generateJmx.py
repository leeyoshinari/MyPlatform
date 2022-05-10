#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import traceback
import xml.etree.ElementTree as ET

class JMeter:
    def __init__(self):
        self.jmeter_header = '<?xml version="1.0" encoding="UTF-8"?>'

        self.test_plan = ''

    def write_jmx(self):
        pass

    def generate_test_plan(self, plans):
        plan = plans
        pass