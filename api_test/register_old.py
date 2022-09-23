# @Time    : 2022-07-26  01:52:59
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/auto_register/register_old.py
# @Describe:

# from copyreg import pickle
import pickle
from datetime import datetime, timedelta
import requests
import os
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm
import random
import time
import argparse
import numpy as np

parser = argparse.ArgumentParser(description="")
parser.add_argument("--ip", type=str, default="http://192.168.3.202", help="")
parser.add_argument("--port", type=int, default=8187, help="")
parser.add_argument("--path", type=str, default="/test/file", help="")
parser.add_argument(
    "--file_path", type=str, default="/mnt/cti_record_data_with_phone_num", help=""
)
args = parser.parse_args()

result = []

spkid_paths = [
    os.path.join(args.file_path, _file) for _file in os.listdir(args.file_path)
]

for spkid_path in tqdm(spkid_paths):
    patient_len = 0
    spkid = spkid_path.split("/")[-1]
    session_paths = [
        os.path.join(spkid_path, _path)
        for _path in os.listdir(spkid_path)
        if "wav" not in _path
    ]
    for session_path in session_paths:
        wav_files = [
            os.path.join(session_path, _path) for _path in os.listdir(session_path)
        ]
        for wav_file in wav_files:
            result.append(
                {
                    "url": f"{args.ip}:{args.port}{args.path}",
                    "record_file_name": "",
                    "spkid": spkid + str(int(time.time())),
                    "begintime": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                    "endtime": (
                        datetime.now() + timedelta(seconds=random.randint(60, 300))
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "wav_url": f"local://{wav_file}",
                    # "request_file":{'wav_file':open(wav_file, 'rb')}
                }
            )
            break
        break

print(len(result))
# with open('register_old.pkl', 'wb') as f:
#      pickle.dump(result, f)


def register(item):
    record_file_name = item["record_file_name"]
    url = item["url"]
    spkid = item["spkid"]
    begintime = item["begintime"]
    endtime = item["endtime"]
    wav_url = item["wav_url"]
    filename = record_file_name.split("/")[-1]

    values = {
        "spkid": spkid,
        "wav_url": wav_url,
        "call_begintime": begintime,
        "call_endtime": endtime,
    }
    wav_file = wav_url.replace("local://", "")
    wav_request_file = {"wav_file": open(wav_file, "rb")}
    try:
        resp = requests.request("POST", url=url, data=values, files=wav_request_file)
        print(resp.json())
        print(f"Registering:\n\t-> URL {url}\n\t-> SPKID {spkid}")
    except Exception as e:
        print(e)
        return
    print(f"success {spkid}")


result = result[::-1]
# register(result)
pool = ThreadPool(2)
pool.map(register, result)
pool.close()
pool.join()
