# -*- coding: utf-8 -*-
# 本地linux的minio名称 -> 可在linux上面的 ~/.config/rclone/rclone.conf 文件中查看

import glob
import multiprocessing
import subprocess
import time
import os
from datetime import datetime

import requests
from logs import Logger

from minio import Minio

dt = datetime.now().strftime('%Y-%m-%d')
LOG = Logger(f'{dt}_auto_test.log', level='debug').logger

MINIO_HOST = 'http://172.16.185.59:9901'
TEST_URL = 'http://172.16.185.192:8888/test/url'  # 服务地址
BUCKETS_NAME_BLACK = "black-raw"  # 黑库桶名
BUCKETS_NAME_GRAY = "raw"  # 灰库桶名
WAV_PATH_GRAY = '/home/recbak/gray/20221127'

client = Minio(
    "192.168.3.202:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


def rclone_job(file):
    # command = f"rclone sync {file} minio:/{BUCKETS_NAME_GRAY}"
    # subprocess.call(command, shell=True)

    file_name = os.path.basename(file)
    payload = {
        'spkid': file_name.split('.')[0].replace('_', ''),
        'show_phone': '123',
        'wav_url': f'{MINIO_HOST}/{BUCKETS_NAME_GRAY}/{file_name}'
    }
    response = requests.request("POST", TEST_URL, data=payload)
    if not response.ok:
        LOG.error(f'{file} request failed. Response info:{response.text}')
    else:
        LOG.info(f'File:{file},Response info:{response.text}')


def main():
    start_time = time.time()
    # 方式1
    objects = client.list_objects(BUCKETS_NAME_GRAY, recursive=True)
    files = []
    for obj in objects:
        files.append(obj.object_name)
        print(len(files))

    # 方式2
    # files = glob.glob(WAV_PATH_GRAY + '/*')
    print(f'Total count:{len(files)},call time:{time.time() - start_time}')

    # pool = multiprocessing.Pool(32)
    # pool.map(rclone_job, files)


if __name__ == "__main__":
    LOG.info(f'Start! Dir is:{WAV_PATH_GRAY}')
    t1 = time.time()
    main()
    LOG.info(f'Call time:{time.time() - t1}')
