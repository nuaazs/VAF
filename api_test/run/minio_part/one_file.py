
from oss.oss_tool import OSS
import os
import datetime
import random
import json
import requests
import yaml



with open('config.yaml', 'r', encoding='utf-8') as f:
    args = yaml.safe_load(f)

def access_file():
    if pattern == "file":
        return os.listdir(args.get("WAV_PATH"))

    if pattern == "url":
        oss = OSS(args.get("BUCKETS_NAME"))
        return oss.get_object_name()

pattern = args.get("MODE")
def data_requests(wav):
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    phone = random.randint(11111111111, 99999999999)
    values = {"spkid": str(phone),"show_phone": "15151832002","call_begintime":begintime,"call_endtime":endtime}

    wav_url = "http://192.168.3.202:9000/black/H_JSSR12565243_20220815374866_00000156_otalk_True_zhuanban.wav"
    print(wav_url)
    values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
    resp = requests.request("POST", url, data = values)

    resp_json = resp.json()
    print(json.dumps(resp_json, sort_keys=False, indent=4))


if __name__ == "__main__":
    url = r"http://{0}:{1}/{2}/{3}".format(args.get("IP"), args.get("PORT"), args.get("PATH"), args.get("MODE"))
    pb_index = ["file_name", "status", "err_msg", "inbase", "file_size(M)",  "all_time(s)", "download_time(ms)", 
                "vad_time(ms)", "self_test_time(ms)",  "classify_time(ms)", "DataBase_time(ms)", "test_time(ms)", 
                "GetEmbedding_time(ms)", "Other_time(ms)"]
    client = OSS(args.get("BUCKETS_NAME")).client
    data_file = args.get("FILE_NAME")
    wavs = access_file()

    data_requests("1_8_name_000000000000125.wav")


