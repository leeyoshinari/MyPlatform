#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import json
import logging
import traceback
from django.conf import settings


logger = logging.getLogger('django')

def get_value_by_host(host_key, k=None):
    try:
        server_dict = json.loads(settings.REDIS.get(host_key))
        if k:
            return server_dict[k]
        else:
            return server_dict
    except:
        logger.error(traceback.format_exc())
        return None


def get_all_host():
    agents = []
    try:
        keys = settings.REDIS.keys('jmeterServer_*')
        for key in keys:
            agents.append(json.loads(settings.REDIS.get(key)))
    except:
        logger.error(traceback.format_exc())
    return agents


def get_all_keys():
    return settings.REDIS.keys('jmeterServer_*')
