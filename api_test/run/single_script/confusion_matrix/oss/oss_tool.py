# @Time    : 2022-07-27  18:57:38
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/oss.py
# @Describe: Minio sdk for python.
import os
from minio import Minio
from minio import Minio
from minio.commonconfig import GOVERNANCE
from minio.retention import Retention

from datetime import datetime
from datetime import timedelta
import cfg


class OSS:
    """
    minio operation
    """
    def __init__(self, buckets_name) -> None:
        self.host = f"{cfg.MINIO['host']}:{cfg.MINIO['port']}"
        self.client = self.Connecting_minio()
        self.buckets_name = buckets_name
        self.check_buckets()




    def Connecting_minio(self):
        ACCESS_KEY = cfg.MINIO['access_key']
        SECRET_KEY = cfg.MINIO['secret_key']
        client = Minio(
                self.host,
                access_key=ACCESS_KEY,
                secret_key=SECRET_KEY,
                secure=False
            )
        return client


    def remove_list_object(self, list_objects):
        for wav in list_objects:
            file_name = wav.object_name
            self.client.remove_object(self.buckets_name, file_name)


    def read_object(self):
        list_objects = self.client.list_objects(self.buckets_name)
        return list_objects


    def remove_all_object(self):
        self.remove_list_object(self.read_object())


    def check_buckets(self) :
        """ 
        Check that the bucket exists.
        """
        found = self.client.bucket_exists(self.buckets_name)
        if not found:
            self.client.make_bucket(self.buckets_name, object_lock=True)
        else:
            print("Bucket '" + self.buckets_name +"' already exists")

        # found = self.client.bucket_exists("preprocessed")
        # if not found:
        #     self.client.make_bucket(bucket_name="preprocessed",object_lock=True)
        # else:
        #     print("Bucket 'preprocessed' already exists")
        return self.client

    # def get_object(self, object_name):
    #     return self.client.get_object(self.buckets_name, object_name)

    def get_object_list(self, object_name_list):
        res = []
        for object_name in object_name_list:
            res.append(self.client.get_object(self.buckets_name, object_name))
        return res
        
    def fget_object(self, object_name, file_path):
        self.client.fget_object(self.buckets_name, object_name, os.path.join(file_path, object_name))








    def get_object_name(self): # 获取桶对象名称
        list_objects = self.client.list_objects(self.buckets_name)
        res = []
        for i in list_objects:
            res.append(i.object_name)
        return res

    def get_object_name_v2(self, buckets_name): # 获取桶对象名称
        list_objects = self.client.list_objects(buckets_name)
        res = []
        for i in list_objects:
            res.append(i.object_name)
        return res

    def upload_file(self, bucket_name, filepath, filename, save_days = 30):  # 上传对象
        """ 
        bucket_name: 
            minip桶名称  example --> 'raw'
        filepath:
            file path  example --> "/VAF-System/demo_flask/utils/orm.py"
        filename:
            file name  example --> 'orm.py'
        save_days:
            -  example --> 30

        """
        # Upload data with tags, retention and legal-hold.
        date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0,
        ) + timedelta(days=save_days)

        if save_days < 0:
            result = self.client.fput_object(bucket_name, filename, filepath, True)
        else:
            result = self.client.fput_object(
                bucket_name, filename, filepath,
                retention=Retention(GOVERNANCE, date),
                legal_hold=True,
            )
        print(
            "created {0} object; etag: {1}, version-id: {2}".format(
                result.object_name, result.etag, result.version_id,
            ),
        )

        return f"http://{self.host}/{bucket_name}/{filename}"
