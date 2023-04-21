# -*- coding: utf-8 -*-
import glob
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

LOG = Logger(f'{dt}_auto_test.log', level='debug').logger


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
    mark_file(file)


def mark_file(spkid):
    """
    标记文件
    Args:
        file:

    Returns:

    """
    with open('processed_list.txt', 'a') as f:
        f.writelines(f'{spkid}\n')  # os.getpid() 是进程编号


def main():
    start_time = time.time()
    # todo
    files_original = glob.glob(cfg.WAV_PATH_GRAY + '/*/*.wav')
    random.seed(123)
    random.shuffle(files_original)

    with open(f'files_original-{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.txt', 'w') as f:
        f.writelines(f'{files_original}')

    if os.path.exists("processed_list.txt"):
        with open('processed_list.txt', 'r') as f:
            processed_list = [line.strip() for line in f.readlines()]
        files = list(set(files_original).difference(set(processed_list)))
        LOG.info(f'Processed count:{len(processed_list)},remain count:{len(files)}')
    else:
        files = files_original

    LOG.info(f'Remain count:{len(files)}. Call time:{time.time() - start_time}')

    # process_map(test_by_file, files, max_workers=cfg.WORKERS)

    with multiprocessing.Pool(cfg.WORKERS) as p:
        p.map(test_by_file, files)

    # with multiprocessing.Pool(cfg.WORKERS) as p:
    #     list((tqdm(p.imap(test_by_file, files), total=len(files), desc='监视进度')))

    os.rename('processed_list.txt', f'processed_list.txt.{dt}')
    LOG.info(f'Rename processed_list.txt to processed_list.txt.{dt}')


if __name__ == "__main__":
    LOG.info(f'Start! Dir is:{cfg.WAV_PATH_GRAY}')
    t1 = time.time()
    main()
    LOG.info(f'Call time:{time.time() - t1}')
