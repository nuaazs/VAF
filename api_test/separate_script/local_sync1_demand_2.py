import os
import datetime
import json
import time
import requests
from multiprocessing.dummy import Pool as ThreadPool


class ARGS:
    IP = "127.0.0.1"
    # 端口
    PORT = "8187"
    # 方式  default： test | register
    PATH = "test"
    # default： url | file
    MODE = "url"
    # 本地wav路径
    WAV_PATH = "/mnt/panjiawei/test/wav"
    # 黑裤桶名
    BLACK_BUCKETS_NAME = "check"
    URL_REGISTER = r"http://{0}:{1}/{2}/{3}".format(IP, PORT, "register", MODE)
    # 灰库桶名
    GRAY_BUCKETS_NAME = "check"
    URL_TEST = r"http://{0}:{1}/{2}/{3}".format(IP, PORT, "test", MODE)
    # 地址
    URL_PATH = "http://192.168.3.202:9000"
    # 文件获取方式
    PATTERN = "rclone"


def access_file(file_name):
    if ARGS.PATTERN == "rclone":
        str = r"rclone lsl minio:/%s | awk '{print $4}'" % (file_name)
        with os.popen(str) as f1:
            return f1.read().strip().split("\n")


def data_test(wav):
    """
    wav: wav name
    """
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    phone = int(time.time() * 1000000)
    values = {
        "spkid": str(phone),
        "show_phone": "15151832002",
        "call_begintime": begintime,
        "call_endtime": endtime,
    }

    wav_url = ARGS.URL_PATH + "/" + ARGS.GRAY_BUCKETS_NAME + "/" + wav

    values = {
        "spkid": str(phone),
        "show_phone": "15151832002",
        "wav_url": wav_url,
        "call_begintime": begintime,
        "call_endtime": endtime,
    }
    resp = requests.request("POST", ARGS.URL_TEST, data=values)

    resp_json = resp.json()
    print(wav_url)
    print(json.dumps(resp_json, sort_keys=False, indent=4))


def data_requests(wav):
    """
    get data
    """
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    phone = int(time.time() * 1000000)
    values = {
        "spkid": str(phone),
        "show_phone": "15151832002",
        "call_begintime": begintime,
        "call_endtime": endtime,
    }

    wav_url = ARGS.URL_PATH + "/" + ARGS.BLACK_BUCKETS_NAME + "/" + wav

    values = {
        "spkid": str(phone),
        "show_phone": "15151832002",
        "wav_url": wav_url,
        "call_begintime": begintime,
        "call_endtime": endtime,
    }
    resp = requests.request("POST", ARGS.URL_REGISTER, data=values)

    resp_json = resp.json()

    print(json.dumps(resp_json, sort_keys=False, indent=4))


def run():
    wavs_black_outdated = set(access_file("18file"))
    wavs_gray_outdated = set(access_file("18file"))
    while True:
        time.sleep(1)
        wavs_black_new = set(access_file(ARGS.BLACK_BUCKETS_NAME))
        wavs_gray_new = set(access_file(ARGS.GRAY_BUCKETS_NAME))
        # black storeroom
        add_wavs = wavs_black_new - wavs_black_outdated
        pool = ThreadPool(10)
        print(add_wavs)
        try:
            pool.map(data_test, add_wavs)
        except:
            print("灰库发生问题了")
        wavs_black_outdated.update(add_wavs)

        # gray storeroom
        add_wavs = wavs_gray_new - wavs_gray_outdated
        try:
            pool.map(data_requests, add_wavs)
        except:
            print("黑库发生问题了")
        wavs_gray_outdated.update(add_wavs)
        pool.close()
        pool.join()
        break  # ------------------------------------ 记得关闭 -----------------


if __name__ == "__main__":
    run()
