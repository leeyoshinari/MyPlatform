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
    except TypeError:
        logger.debug(traceback.format_exc())
        return None
    except:
        logger.error(traceback.format_exc())
        return None


def get_all_host(k='jmeterServer_*'):
    agents = []
    try:
        keys = settings.REDIS.keys(k)
        for key in keys:
            agents.append(json.loads(settings.REDIS.get(key)))
    except TypeError:
        logger.debug(traceback.format_exc())
    except:
        logger.error(traceback.format_exc())
    return agents


def get_all_keys(k='jmeterServer_*'):
    return settings.REDIS.keys(k)
