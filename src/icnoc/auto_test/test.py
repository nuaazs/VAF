"""
@file: test.py
@time: 2021/8/31 15:00
@desc:各模块时间测试
"""
# -*- coding: utf-8 -*-
import glob
import json
import multiprocessing
import subprocess
import time
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import random
from tqdm.contrib.concurrent import process_map
import requests
from tqdm import tqdm
import config as cfg
from logs import Logger

dt = datetime.now().strftime('%Y-%m-%d')
LOG = Logger(f'{dt}_local_test.log', level='debug').logger


def test_by_file(file):
    """
    通过文件上传测试
    Args:
        file:

    Returns:

    """
    request_file = {"wav_file": open(file, "rb")}
    wav_url = f"local://{file}"
    phone = os.path.basename(file).split("_")[0]
    values = {
        # todo
        # "spkid": str(phone),
        'spkid': str(random.randint(10000000000, 99999999999)),
        "wav_url": wav_url,
    }
    response = requests.request("POST", cfg.TEST_FILE_URL, files=request_file, data=values)
    if not response.ok:
        LOG.error(f'{file} request failed. Response info:{response.text}')
    else:
        LOG.info(f'File:{file},Response info:{response.text}')
        mark_file(response)


def mark_file(response):
    """
    标记文件
    Args:
        file:

    Returns:

    """
    download_used_time = response.json()['used_time']['download_used_time']
    vad_used_time = response.json()['used_time']['vad_used_time']
    resample_16k = response.json()['used_time']['resample_16k']
    encode_time = response.json()['used_time']['encode_time']
    test_used_time = response.json()['used_time']['test_used_time']

    other_total = response.elapsed.total_seconds() - download_used_time - vad_used_time - resample_16k - encode_time - test_used_time
    context = response.json()['used_time']
    context['other_total'] = other_total
    with open('test_report.txt', 'a') as f:
        f.writelines('{}\n'.format(context))


def main():
    start_time = time.time()
    files_original = glob.glob(cfg.WAV_PATH_GRAY + '/*/*.wav')
    random.seed(123)
    random.shuffle(files_original)
    files = files_original[:cfg.TEST_COUNT]

    LOG.info(f'Remain count:{len(files)}. Call time:{time.time() - start_time}')

    process_map(test_by_file, files, max_workers=cfg.WORKERS)

    # with multiprocessing.Pool(cfg.WORKERS) as p:
    #     list((tqdm(p.imap(test_by_file, files), total=len(files), desc='监视进度')))


def parse_data():
    """
    解析数据
    Returns:

    """
    download_used_time = vad_used_time = resample_16k = encode_time = \
        other_total = test_used_time = 0

    with open('test_report.txt', 'r') as f:
        li = f.readlines()

    li = [json.loads(i.strip().replace("'", '"')) for i in li]
    for i in li:
        download_used_time += i['download_used_time']
        vad_used_time += i['vad_used_time']
        resample_16k += i['resample_16k']
        encode_time += i['encode_time']
        test_used_time += i['test_used_time']
        other_total += i['other_total']
    LOG.info(f'coutn:{len(li)}')
    LOG.info(f'Mean download_used_time:{round(download_used_time / len(li), 2)}')
    LOG.info(f'Mean vad_used_time:{round(vad_used_time / len(li), 2)}')
    LOG.info(f'Mean resample_16k:{round(resample_16k / len(li), 2)}')
    LOG.info(f'Mean encode_time:{round(encode_time / len(li), 2)}')
    LOG.info(f'Mean test_used_time:{round(test_used_time / len(li), 2)}')
    LOG.info(f'Mean other_total:{round(other_total / len(li), 2)}')


if __name__ == "__main__":
    LOG.info(f'Start! Dir is:{cfg.WAV_PATH_GRAY}')
    t1 = time.time()
    if os.path.exists('test_report.txt'):
        os.remove('test_report.txt')
    main()
    parse_data()
    LOG.info(f'Call time:{time.time() - t1}')
