from query import Query
from datetime import datetime
import requests
import time

query = Query(-24 * 20)
print("* 开始自动注册")
query.now_timestamp = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
result = query.check_new_record()
query.pre_timestamp = query.now_timestamp

print(len(result))
# result = [
#     {
#         "record_file_name":"",
#         "caller_num":"15151832012",
#         "begintime":(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
#         "endtime":(datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
#     }
# ]
for item in result:
    print(item)
    record_file_name = item["record_file_name"]
    caller_num = item["caller_num"]
    begintime = item["begintime"]
    endtime = item["endtime"]
    if len(caller_num) != 11:
        continue
    wav_url = f"http://116.62.120.233/mpccApi/common/downloadFile.json?type=0&addr={record_file_name}"
    # wav_url = f"local:/home/zhaosheng/VAF-System/demo_flask/wavs/raw/13654182662/raw_1.wav"
    filename = record_file_name.split("/")[-1]
    save_path = f"root/{caller_num}/{filename}"

    url = "http://192.168.0.14:8180/register/url"
    values = {
        "spkid": caller_num,
        "wav_url": wav_url,
        "call_begintime": begintime,
        "call_endtime": endtime,
    }
    print(values)
    try:
        resp = requests.request("POST", url=url, data=values)
        print(resp.json())
        print(
            f"Registering:\n\t-> URL {url}\n\t-> SPKID {caller_num}\n\t-> Save Path {save_path}"
        )
    except Exception as e:
        print(e)
        time.sleep(10)
        continue
