# coding = utf-8
# @Time    : 2022-09-05  15:08:59
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Minio upload files.

from datetime import timedelta
from minio.commonconfig import GOVERNANCE
from minio.retention import Retention
from datetime import datetime
from minio import Minio
from datetime import timedelta
from utils.log.log_wraper import logger
import os
import cfg


def check(bucket_name_list=cfg.BUCKETS):
    # check minio connection
    try:
        logger.info("\t\t\t -> * Checking minio connection ... ")
        HOST = f"{cfg.MINIO['host']}:{cfg.MINIO['port']}"
        ACCESS_KEY = cfg.MINIO["access_key"]
        SECRET_KEY = cfg.MINIO["secret_key"]
        client = Minio(HOST, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
        for bucket_name in bucket_name_list:
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info(f"\t\t\t -> * Bucket:{bucket_name} not exist, now creating ... ")
            if bucket_name == "testing":
                for filename in os.listdir(f"./test_wavs"):
                    filepath = f"./test_wavs/{filename}"
                    result = client.fput_object(
                        bucket_name,
                        filename,
                        filepath,
                    )

        logger.info(f"\t\t\t -> * Minio test: Pass ! ")
        return True, ""
    except Exception as e:
        print(e)
        logger.error(f"\t\t\t -> * Minio test: Error !!! ")
        logger.error(f"\t\t\t -> * Minio Error Message: {e}")
        return False, e