#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import requests


def upload_file_by_path(file_path):
    pass


def upload_file_by_bytes(file_bytes):
    pass


def download_file_to_path(url, file_path):
    with open(file_path, 'wb') as f:
        f.write(download_file_to_bytes(url))


def download_file_to_bytes(url):
    res = requests.get(url)
    return res.content
