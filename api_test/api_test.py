# coding = utf-8
# @Time    : 2022-09-11  18:41:22
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: API test script, test the running speed of CPU and GPU version and the proportion of each part.

import requests
import argparse
import datetime
import os
import random
import numpy as np
import json


parser = argparse.ArgumentParser(description='')
parser.add_argument('--ip', type=str, default="127.0.0.1",help='server ip')
parser.add_argument('--port', type=int, default=8187,help='port number')
parser.add_argument('--path', type=str, default="test",help='test|register')
parser.add_argument('--wav_path', type=str, default="/VAF-System/test/test_wavs",help='The directory address of the wav file for testing.')
parser.add_argument('--mode', type=str, default="url",help='url|file')
parser.add_argument('--test_num', type=int, default=1000,help='The total number of files you want to test, if not enough to test the same files repeatedly.')
args = parser.parse_args()

url=f"http://{args.ip}:{args.port}/{args.path}/{args.mode}"
headers = {
    'Content-Type': 'multipart/form-data'
}
endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
wavs = sorted([os.path.join(args.wav_path,_file) for _file in os.listdir(args.wav_path) if ".wav" in _file])
print(f"* Start testing:\n\t total {len(wavs)} files in fold.")
start_time = datetime.datetime.now()

item_number = 0

download_total = 0
vad_total = 0
self_test_total = 0
classify_total = 0
other_total = 0
total_total = 0
to_database_total = 0
test_total = 0
test_embedding_total = 0

for wav in wavs:
    for i in range(1):
        if item_number>=args.test_num:
            break
        item_number += 1
        if args.mode == 'file':
            request_file = {'wav_file':open(wav, 'rb')}
            phone = random.randint(11111111111, 99999999999)
            values = {"spkid": str(phone),"show_phone": "15151832002","call_begintime":begintime,"call_endtime":endtime}
            start = datetime.datetime.now()
            resp = requests.request("POST",url, files=request_file, data=values)
            #print(f"\n\n#{item_number}")
            #print(json.dumps(resp.json(), sort_keys=False, indent=4))
            time_used =datetime.datetime.now() - start
            total = time_used.total_seconds()
            total_total += total
            download_total += resp.json()["download_used_time"]
            vad_total += resp.json()["vad_used_time"]
            self_test_total += resp.json()["self_test_used_time"]

            to_database_total += resp.json().get("to_database_used_time",0)
            test_total += resp.json().get("test_used_time",0)
            test_embedding_total += resp.json().get("embedding_used_time",0)
            
            other_total += total - resp.json().get("to_database_used_time",0) - resp.json().get("test_used_time",0) - resp.json().get("embedding_used_time",0) - resp.json()["download_used_time"] - resp.json()["vad_used_time"] - resp.json()["self_test_used_time"] - resp.json()["classify_used_time"]

        else:
            
            wav_url = f"local://{wav}"
            phone = random.randint(11111111111, 99999999999)
            values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
            start = datetime.datetime.now()
            resp = requests.request("POST",url, data=values)
            #print(f"\n\n#{item_number}")
            #print(json.dumps(resp.json(), sort_keys=False, indent=4))
            time_used =datetime.datetime.now() - start
            total = time_used.total_seconds()
            total_total += total
            download_total += resp.json()["download_used_time"]
            vad_total += resp.json()["vad_used_time"]
            self_test_total += resp.json()["self_test_used_time"]
            classify_total += resp.json()["classify_used_time"]

            to_database_total += resp.json().get("to_database_used_time",0)
            test_total += resp.json().get("test_used_time",0)
            test_embedding_total += resp.json().get("embedding_used_time",0)
            
            other_total += total - resp.json().get("to_database_used_time",0) - resp.json().get("test_used_time",0) - resp.json().get("embedding_used_time",0) - resp.json()["download_used_time"] - resp.json()["vad_used_time"] - resp.json()["self_test_used_time"] - resp.json()["classify_used_time"]


mean_time = total_total/item_number
print(f"\n\n\t-> Mean Used Time:{mean_time}")
print(f"\t\t-> Download Used Time:{download_total*100/total_total:.2f}%")
print(f"\t\t-> Vad Used Time:{vad_total*100/total_total:.2f}%")
print(f"\t\t-> Self test Used Time:{self_test_total*100/total_total:.2f}%")
print(f"\t\t-> Classify Used Time:{classify_total*100/total_total:.2f}%")
print(f"\t\t-> To DataBase Used Time:{to_database_total*100/total_total:.2f}%")
print(f"\t\t-> Test Used Time:{test_total*100/total_total:.2f}%")
print(f"\t\t-> GetEmbedding Used Time:{test_embedding_total*100/total_total:.2f}%")
print(f"\t\t-> Other Used Time:{other_total*100/total_total:.2f}%")

# 2022-09-11 4000条测试结果 -> Mean Used Time:0:00:00.667702