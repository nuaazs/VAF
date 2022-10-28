# -*- coding:utf-8 -*-
# Author: 𝕫𝕙𝕒𝕠𝕤𝕙𝕖𝕟𝕘
# Email: zhaosheng@nuaa.edu.cn
# Time  : 2022-05-06  20:05:37.000-05:00
# Desc  : API test.

import requests
import argparse
import datetime
import os
import random

parser = argparse.ArgumentParser(description="")
parser.add_argument("--ip", type=str, default="127.0.0.1", help="")
parser.add_argument("--port", type=int, default=8185, help="")
parser.add_argument("--path", type=str, default="score", help="")
parser.add_argument(
    "--wav_path", type=str, default="/VAF-System/test/test_wavs", help=""
)
parser.add_argument("--mode", type=str, default="file", help="url or file")

args = parser.parse_args()

url = f"http://{args.ip}:{args.port}/{args.path}/{args.mode}"
headers = {"Content-Type": "multipart/form-data"}
endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
wavs = sorted(
    [
        os.path.join(args.wav_path, _file)
        for _file in os.listdir(args.wav_path)
        if ".wav" in _file
    ]
)
print(wavs)
start_time = datetime.datetime.now()
wav1 = wavs[0]
wav2 = wavs[1]

if args.mode == "file":
    request_file = {"wav_file1": open(wav1, "rb"), "wav_file2": open(wav2, "rb")}
    phone1 = random.randint(11111111111, 99999999999)
    phone2 = random.randint(11111111111, 99999999999)
    values = {
        "spkid1": str(phone1),
        "spkid2": str(phone2),
        "show_phone": "15151832002",
        "call_begintime": begintime,
        "call_endtime": endtime,
    }
    print(values)
    # !不能指定header
    resp = requests.request("POST", url, files=request_file, data=values)
    print(resp.json())

else:
    wav_url1 = f"local://{wav1}"
    wav_url2 = f"local://{wav2}"
    phone1 = random.randint(11111111111, 99999999999)
    phone2 = random.randint(11111111111, 99999999999)
    values = {
        "spkid1": str(phone1),
        "spkid2": str(phone2),
        "show_phone": "15151832002",
        "wav_url1": wav_url1,
        "wav_url2": wav_url2,
    }
    print(values)
    resp = requests.request("POST", url=url, data=values)
    print(resp.json())

time_used = end = datetime.datetime.now() - start_time
print(time_used)
