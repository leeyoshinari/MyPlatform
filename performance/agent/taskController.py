#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import requests

class Task(object):
    def __init__(self):
        pass

    def save_file(self, files):
        pass

    def upload_file_by_path(self, file_path):
        pass

    def upload_file_by_bytes(self, file_bytes):
        pass

    def download_file_to_path(self, url, file_path):
        with open(file_path, 'wb') as f:
            f.write(self.download_file_to_bytes(url))

    def download_file_to_bytes(self, url):
        res = requests.get(url)
        return res.content

if __name__ == '__main__':
    t = Task()
    t.download_file_to_bytes('http://127.0.0.1:8000/tencent/static/files/1651999794686/工作簿1.csv')
