#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import requests
import zipfile

def upload_file_by_path(store_type, file_path):
    """
        store_type: 1-MinIO, 2-other,todo
    """
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


def delete_local_file(path):
    result = {'code': 0, 'msg': f'Path: {path} is deleted failure ~'}
    try:
        allfiles = os.listdir(path)
        if len(allfiles) == 0:
            os.rmdir(path)
            result['msg'] = f'Path: {path} has empty ~'
        else:
            for fp in allfiles:
                os.remove(os.path.join(path, fp))
            os.rmdir(path)
            result['msg'] = f'Path: {path} is deleted success ~'
    except:
        result['code'] = 1
    return result



def zip_file(file_path, zip_file_path):
    file_list = os.listdir(file_path)
    archive = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for file in file_list:
        archive.write(os.path.join(file_path, file), file)
    archive.close()


def unzip_file(source_path, target_path):
    f = zipfile.ZipFile(source_path)
    f.extractall(target_path)
    f.close()
