#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import requests
import zipfile

def upload_file_by_path(file_path):
    return ''


def upload_file_by_bytes(file_bytes):
    pass


def download_file_to_path(url, file_path):
    with open(file_path, 'wb') as f:
        f.write(download_file_to_bytes(url))


def download_file_to_bytes(url):
    res = requests.get(url)
    return res.content


def delete_remote_file(url):
    pass


def zip_file(file_path, zip_file_path):
    file_list = os.listdir(file_path)
    archive = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for file in file_list:
        archive.write(os.path.join(file_path, file), file)
    archive.close()
