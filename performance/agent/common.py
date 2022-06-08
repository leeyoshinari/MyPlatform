#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import os
import configparser
import logging.handlers


cfg = configparser.ConfigParser()
cfg.read('config.ini', encoding='utf-8')


def get_config(key):
    return cfg.get('agent', key, fallback=None)


LEVEL = get_config('level')
backupcount = int(get_config('backupCount'))
log_path = get_config('logPath')

if not os.path.exists(log_path):
    os.mkdir(log_path)

log_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s[line:%(lineno)d] - %(message)s')
logger.setLevel(level=log_level.get(LEVEL))

file_handler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(log_path, 'monitor.log'), when='midnight', interval=1, backupCount=backupcount)
file_handler.suffix = '%Y-%m-%d.log'

# file_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_ip():
    """
    Get server's IP address
    :return: IP address
    """
    try:
        if get_config('host'):
            IP = get_config('host')
        else:
            result = os.popen("hostname -I |awk '{print $1}'").readlines()
            logger.debug(result)
            if result:
                IP = result[0].strip()
                logger.info(f'The IP address is: {IP}')
            else:
                logger.warning('Server IP address not found!')
                IP = '127.0.0.1'
    except:
        IP = '127.0.0.1'

    return IP
