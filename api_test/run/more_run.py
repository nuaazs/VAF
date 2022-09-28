
from oss.oss_tool import OSS
import os
import datetime
import random
import json
import requests
import pandas as pd
import numpy as np
import yaml
from multiprocessing.dummy import Pool as ThreadPool
import time


# 读取配置文件
with open('config.yaml', 'r', encoding='utf-8') as f:
    args = yaml.safe_load(f) # 读取配置文件

def set_file(data_list, csv_file_name):
    # 注意：放到循环里面，每次都会打开，浪费时间
    with open(csv_file_name, 'a+') as brush:
        brush.writelines(",".join(data_list) + "\n")


def access_file():
    # 本地获取文件
    if pattern == "file":
        return os.listdir(args.get("WAV_PATH"))

    # url获取
    if pattern == "url":
        oss = OSS(args.get("BUCKETS_NAME"))
        return oss.get_object_name()


def info_neaten(resp, total_time, wav, file_size):
    # 时间数据整理
    resp_json = resp.json()
    print(json.dumps(resp_json, sort_keys=False, indent=4))

    total = total_time.total_seconds()
    status = resp_json.get("status")
    err_msg = resp_json.get("err_msg")
    inbase = resp_json.get("inbase")

    used_time = resp_json.get("used_time")
    download_time = used_time.get("download_used_time")
    vad_time = used_time.get("vad_used_time")
    self_test_time = used_time.get("self_test_used_time")
    classify_time = used_time.get("classify_used_time")

    DataBase_time = used_time.get("to_database_used_time",0)
    test_time = used_time.get("test_used_time",0)
    GetEmbedding_time = used_time.get("embedding_used_time",0)
    pd_list = [download_time, vad_time, self_test_time, classify_time, DataBase_time, test_time, GetEmbedding_time]
    Other_time = total - sum(pd_list)
    pd_list += [Other_time]
    pd_list = list(np.array(pd_list) * 1000)
    pd_list = [wav, status, err_msg, inbase, file_size, total] + pd_list

    pd_list_str = []
    for i in pd_list:
        pd_list_str.append(str(i))
    return pd_list_str


pattern = args.get("MODE")
def data_requests(wav):
    # 读取数据
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    is_storage = args.get("IS_STORAGE")
    print(wav)
    phone = random.randint(11111111111, 99999999999)
    values = {"spkid": str(phone),"show_phone": "15151832002","call_begintime":begintime,"call_endtime":endtime}

    wav_url = ""

    if  pattern == "file":
        wav = "raw_34086548105_1_1031627_____00010.wav"
        wav_url = "/mnt/panjiawei/test/downloadFild/raw_34086548105_1_1031627_____00010.wav"
        wav_url = os.path.join(args.get("WAV_PATH"), wav)
        file_size = os.path.getsize(wav_url) /1024 / 1024
        request_file = {'wav_file':open(wav_url, 'rb')}
        start = datetime.datetime.now()
        resp = requests.request("POST", url, files = request_file, data = values)
        time_used = datetime.datetime.now() - start

    if pattern == "url":
        wav_url = args.get("URL_PATH") + "/" + args.get("BUCKETS_NAME") + "/" + wav
        client = OSS(args.get("BUCKETS_NAME")).client
        client.stat_object(args.get("BUCKETS_NAME"), wav)
        file_size = client.stat_object(args.get("BUCKETS_NAME"), wav).size / 1024 / 1024
        values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
        start = datetime.datetime.now()
        resp = requests.request("POST", url, data = values)
        time_used = datetime.datetime.now() - start

    pd_list = info_neaten(resp, time_used, wav, file_size)
    print("===>pd_list ", pd_list)
    if is_storage:
        set_file(pd_list, args.get("FILE_NAME"))


if __name__ == "__main__":
    """
    功能：
        [1]. 测url  [2]. 测本地
    注意：
        运行前, 清先配置config.yaml文件
        单用例调试, 直接在data_requests函数中, 将if判断语句中的wav_url替换成固定路径即可。
    """
    url = r"http://{0}:{1}/{2}/{3}".format(args.get("IP"), args.get("PORT"), args.get("PATH"), args.get("MODE"))
    pb_index = ["file_name", "status", "err_msg", "inbase", "file_size(M)",  "all_time(s)", "download_time(ms)", 
                "vad_time(ms)", "self_test_time(ms)",  "classify_time(ms)", "DataBase_time(ms)", "test_time(ms)", 
                "GetEmbedding_time(ms)", "Other_time(ms)"]

    data_file = args.get("FILE_NAME")
    if args.get("IS_STORAGE") and not os.path.exists(data_file):
        set_file(pb_index, args.get("FILE_NAME"))

    strar = time.time()
    wavs = access_file()

    pool = ThreadPool(10)
    pool.map(data_requests, wavs)
    pool.close()
    pool.join()
    print("运行总时间 ===》 ", time.time() - strar)
