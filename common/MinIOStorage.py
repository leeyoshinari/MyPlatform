#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import time
import traceback
from minio import Minio


class MinIOStorage:
    def __init__(self, host, access_key, secret_key):
        self.client = None
        self.host = host
        self.access_key = access_key
        self.secret_key = secret_key

        self.policy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":' \
                      '["s3:GetBucketLocation","s3:ListBucketMultipartUploads"],"Resource":' \
                      '["arn:aws:s3:::%s"]},{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":["s3:GetObject",' \
                      '"s3:ListMultipartUploadParts","s3:PutObject","s3:AbortMultipartUpload","s3:DeleteObject"],' \
                      '"Resource":["arn:aws:s3:::%s/*"]}]}'

        self.connect_minio()
        self.init_bucket()

        if not os.path.exists('temp'):
            os.mkdir('temp')

    def connect_minio(self):
        """
        connect MinIO
        """
        self.client = Minio(self.host, access_key=self.access_key, secret_key=self.secret_key, secure=False)

    def init_bucket(self):
        """
        init bucket, random bucket name
        """
        for i in range(100):
            _ = self.create_bucket(str((500 + i * 5) ^ (2521 - i * 2)))

    def generate_bucket_name(self):
        """
        random bucket name
        """
        random_i = int(time.time() * 100) % 100
        return str((500 + random_i * 5) ^ (2521 - random_i * 2))

    def create_bucket(self, bucket_name: str):
        """
        create bucket, and reset bucket strategy
        """
        try:
            if self.client.bucket_exists(bucket_name):
                # restart MinIO, request file may return 403, so need to reset bucket strategy
                self.client.set_bucket_policy(bucket_name, self.policy % (bucket_name, bucket_name))
                return f'{bucket_name} has been existed ~'
            self.client.make_bucket(bucket_name)
            self.client.set_bucket_policy(bucket_name, self.policy % (bucket_name, bucket_name))
            return f'{bucket_name} create success ~'
        except:
            raise

    def upload_file_by_path(self, object_name: str, file_path: str, content_type="application/octet-stream"):
        """
        upload local file to MinIO
        :param bucket_name: Name of the bucket.
        :param object_name: Object name in the bucket.
        :param file_path: Name of file to upload.
        :param content_type: Content type of the object.
        """
        try:
            bucket_name = self.generate_bucket_name()
            res = self.client.fput_object(bucket_name, object_name, file_path, content_type)
            return res
        except:
            return None

    def upload_file_bytes(self, object_name: str, data: bytes, length: int, content_type="application/octet-stream"):
        """
        upload bytes stream to MinIO
        :param bucket_name: Name of the bucket.
        :param object_name: Object name in the bucket.
        :param data: An object having callable read() returning bytes object.
        :param length: Data size; -1 for unknown size and set valid part_size.
        :param content_type: Content type of the object.
        """
        try:
            bucket_name = self.generate_bucket_name()
            res = self.client.put_object(bucket_name, object_name, data, length, content_type)
            return res
        except:
            return None

    def delete_file(self, bucket_name: str, object_names: list):
        """
        delete file from MinIO
        """
        try:
            self.client.remove_object(bucket_name, object_names)
        except:
            raise Exception(traceback.format_exc())

    def download_bytes(self, bucket_name: str, object_name: str):
        """
        download file stream from MinIO
        """
        try:
            res = self.client.get_object(bucket_name, object_name)
            return res
        except:
            return None

