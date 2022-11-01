import os
import datetime
import json
import time
import requests
import numpy as np
import pandas as pd
import wget
import random
from multiprocessing.dummy import Pool as ThreadPool

from wav_joint import file_dispose


class ARGS:
    IP = "127.0.0.1"
    # 端口
    PORT = "8186"
    # 方式  default： test | register
    PATH = "test"
    # default： url | file
    MODE = "url"
    # 本地wav路径
    WAV_PATH = "/mnt/panjiawei/test/wav"
    # 黑裤桶名
    BLACK_BUCKETS_NAME = "black"
    url_register = r"http://{0}:{1}/{2}/{3}".format(IP, PORT, "register", MODE)
    # 灰库桶名
    GRAY_BUCKETS_NAME = "gray"
    url_test = r"http://{0}:{1}/{2}/{3}".format(IP, PORT, "test", MODE)
    # 地址
    url_path = "http://192.168.3.202:9000"
    
    # 文件获取方式
    PATTERN = "rclone"
    # 相似度
    similarity = 0.8
    # 合格音频长度(s)
    wav_time = 50
    is_storage = True
    url = r"http://{0}:{1}/{2}/{3}".format(IP, PORT, PATH, MODE)
    # 音频文件质量达标大小 M
    wav_size = 2


def access_file(file_name):
    res = []
    if ARGS.PATTERN == "rclone":
        str = r"rclone lsl minio:/%s | awk '{print $1, $4}'"%(file_name)
        with os.popen(str) as f1:
            data = f1.read().strip().split("\n")
        for i in data:
            res.append(i.split(' '))
    return np.array(res)


def data_requests(wavs, pattern):
    # 测试读取数据
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    is_storage = ARGS.is_storage
    for step, wav in enumerate(wavs):
        print(step, wav)
        phone = random.randint(11111111111, 99999999999)
        values = {"spkid": str(phone),"show_phone": "15151832002","call_begintime":begintime,"call_endtime":endtime}

        wav_url = ""
        pattern = "file"
        if  pattern == "file":
            wav_url = "/mnt/panjiawei/run/data/black/"+wav
            request_file = {'wav_file':open(wav_url, 'rb')}
            start = datetime.datetime.now()
            resp = requests.request("POST", ARGS.url, files = request_file, data = values)
            time_used = datetime.datetime.now() - start
        
        resp_json = resp.json()
        print(json.dumps(resp_json, sort_keys=False, indent=4))

def data_test_gray(wav):
    """ gray
    wav: wav name 
    """
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    phone = int(time.time() * 1000000)
    # values = {"spkid": str(phone),"show_phone": "15151832002","call_begintime":begintime,"call_endtime":endtime}

    wav_url = ARGS.url_path + "/" + ARGS.GRAY_BUCKETS_NAME + "/" + wav
    # wav_url = r"http://192.168.3.202:9000/black/19986868686/1.wav"
    print(wav_url)
    values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
    url = "http://127.0.0.1:8186/test/url"

    resp = requests.request("POST", url, data = values)

    resp_json = resp.json()
    print(wav_url)
    print(json.dumps(resp_json, sort_keys=False, indent=4))


def file_tets_requests(wav, url):
    """
    get data
    """
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    phone = int(time.time() * 1000000)

    wav_url = ARGS.URL_PATH + "/" + ARGS.BLACK_BUCKETS_NAME + "/" + wav

    values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
    resp = requests.request("POST", url, data = values)
    resp_json = resp.json()
    print(json.dumps(resp_json, sort_keys=False, indent=4))


def json_wav(wavs_black_data, bucket_name):
    temporary_path = "./temporary/"
    # 质量
    quality = 1024 * 1024 * ARGS.wav_size
    # 拼接
    wavs_conformity= []
    for size, name in wavs_black_data:
        if int(size) < 50:
            continue
        if int(size) > quality:
            wavs_conformity.append(name)
        else:
            file_phone = name.split("/")[0]
            new_path = os.path.join(temporary_path, file_phone)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            print(new_path)
            print("%s/%s/%s"%(ARGS.url_path, bucket_name, name), os.path.join(temporary_path, name))
            wget.download("%s/%s/%s"%(ARGS.url_path, bucket_name, name), os.path.join(temporary_path, name))
            
    for _phone_name in os.listdir(temporary_path):
        new_path = os.path.join(temporary_path, _phone_name)
        new_file_name = file_dispose(new_path, bucket_name)  # 返回本地拼接后文件地址
        if new_file_name == []:
            return wavs_conformity
        print(new_file_name)
        if bucket_name == "black":
            url_register = ARGS.url_register
            for wav in new_file_name:
                file_tets_requests(wav, url_register)
            # 注册
        if bucket_name == "gray":
            # 测试
            url_test = ARGS.url_test
            for wav in new_file_name:
                file_tets_requests(wav, url_test)
    return wavs_conformity


def run():
    wavs_black_data = access_file("black")
    wavs_black_outdated = set(json_wav(wavs_black_data, "black"))
    wavs_gray_data = access_file("gray")
    wavs_gray_outdated = set(json_wav(wavs_gray_data, "gray"))
    wavs_black_outdated = {""}
    wavs_gray_outdated = {""}
    # while True:
    for i in range(3):
        # time.sleep(1)
        wavs_black_data_new = access_file(ARGS.BLACK_BUCKETS_NAME)
        wavs_gray_data_new = access_file(ARGS.GRAY_BUCKETS_NAME)
        wavs_black_new = set(json_wav(wavs_black_data_new, ARGS.BLACK_BUCKETS_NAME))
        wavs_gray_new = set(json_wav(wavs_gray_data_new, ARGS.GRAY_BUCKETS_NAME))
        # black storeroom
        add_wavs = wavs_black_new - wavs_black_outdated
        print(add_wavs)
        add_wavs = {'19991227709/4.wav', '19989180455/1.wav', '19991533500/1.wav', '19991227709/10.wav', '19991227709/14.wav', '19987564291/1.wav', '19993947576/1.wav', '19991227709/3.wav', '19988562332/1.wav', '19991227709/13.wav', '19987604831/1.wav', '19991227709/1.wav', '19990581797/2.wav', '19991641234/1.wav', '19990502504/1.wav', '19991227709/9.wav', '19990581313/7.wav', '19987811208/1.wav', '19990581797/1.wav', '19990581313/9.wav', '19991227709/15.wav', '19993809629/1.wav', '19990755039/1.wav', '19991227709/12.wav', '19990581313/10.wav', '19991227709/5.wav', '19990581313/6.wav', '19990341511/1.wav', '19990222995/2.wav', '19992012987/1.wav', '19991641234/2.wav', '19990581313/2.wav', '19986868686/1.wav', '19989167122/1.wav', '19990222995/1.wav', '19991227709/6.wav', '19990581313/1.wav', '19991227709/2.wav', '19991227709/11.wav', '19990581313/8.wav', '19990581313/3.wav'}
        wavs_gray_new = {'19991227709/4.wav', '19989180455/1.wav', '19991533500/1.wav', '19991227709/10.wav', '19991227709/14.wav', '19987564291/1.wav', '19993947576/1.wav', '19991227709/3.wav', '19988562332/1.wav', '19991227709/13.wav', '19987604831/1.wav', '19991227709/1.wav', '19990581797/2.wav', '19991641234/1.wav', '19990502504/1.wav', '19991227709/9.wav', '19990581313/7.wav', '19987811208/1.wav', '19990581797/1.wav', '19990581313/9.wav', '19991227709/15.wav', '19993809629/1.wav', '19990755039/1.wav', '19991227709/12.wav', '19990581313/10.wav', '19991227709/5.wav', '19990581313/6.wav', '19990341511/1.wav', '19990222995/2.wav', '19992012987/1.wav', '19991641234/2.wav', '19990581313/2.wav', '19986868686/1.wav', '19989167122/1.wav', '19990222995/1.wav', '19991227709/6.wav', '19990581313/1.wav', '19991227709/2.wav', '19991227709/11.wav', '19990581313/8.wav', '19990581313/3.wav'}
        pool = ThreadPool(10)
        try:
            pool.map(data_test_gray, add_wavs)
        except:
            print("灰库发生问题了")
        wavs_black_outdated.update(add_wavs)
        pool.close()
        pool.join()
        gray storeroom
        pool = ThreadPool(10)
        add_wavs = wavs_gray_new - wavs_gray_outdated
        try:
            pool.map(data_requests, add_wavs)
        except:
            print("黑库发生问题了")
        wavs_gray_outdated.update(add_wavs)
        pool.close()
        pool.join()
        # break # ------------------------------------ 记得关闭 -----------------


if __name__ == "__main__":
    # 自动注册第二部分
    run()
    # data_test_gray('19986868686/1.wav')

    # file_tets_requests("black/19986868686/1.wav")

    # wavs_black_data = access_file("black")
    # json_wav(wavs_black_data)
    # print(data_embedding("H_JSSR12898405_20220815353828_00000014_otalk_zhuanban.wav"))
    # pass

