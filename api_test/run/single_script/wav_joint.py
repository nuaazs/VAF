import wave
from pydub import AudioSegment
import os
import json
import random
import datetime
import requests
import torch
from oss.oss_tool import OSS
import time

class Args:
    # 合格音频长度(s)
    wav_time = 60
    # 拼接方法   0: 无智能顺序拼接 1: 循环顺序拼接
    json_flag = 0
    # url网址本地路径
    url_path = "http://192.168.3.202:9000"
    # ip   default:127.0.0.1
    ip = "127.0.0.1"

    # 端口号    default: 8187 ->gpu 和 8188 -> cpu
    port = "8186"

    # 接口名称   default: test|register
    start = "test"

    # mode   default: url|file
    mode = "url"
    # 桶名称
    buckets_name = "1wfile15msize"
    wav_path = "/mnt/panjiawei/run_2/data/black"
    file_name = "data.csv"
    black_buckets_name = "black"
    

def access_file():
    # 本地获取文件
    pattern = Args.mode
    if pattern == "file":
        return os.listdir(Args.wav_path)

    # url获取
    if pattern == "url":
        oss = OSS(Args.buckets_name)
        return oss.get_object_name()


def data_embedding(wav, state):
    """
    get data
    """
    # if state == "black":
    #     url = r"http://{0}:{1}/{2}/{3}".format(IP, PORT, PATH, MODE)
    # if state == "gray":

    url = "http://127.0.0.1:8185/embedding/url"
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    phone = int(time.time() * 1000000)
    values = {"spkid": str(phone),"show_phone": "15151832002","call_begintime":begintime,"call_endtime":endtime}

    wav_url = Args.url_path + "/" + state + "/" + wav
    print(wav_url)
    values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
    resp = requests.request("POST", url, data = values)

    resp_json = resp.json()
    # return resp_json
    return resp_json.get("embedding")


def read_wav_time(file_path):
    """
        return s
    """
    try:
        with wave.open(file_path, 'rb') as f:
            wav_length = f.getnframes() / f.getframerate()
    except:
        print("[warning] read error. ", file_path)
        return 99999999
    return wav_length


def wav_join(out_name, *args):
    playlist = AudioSegment.empty()
    for wav in args[0]:
        playlist += AudioSegment.from_wav(wav)
    playlist.export(out_name, format = "wav")


def similarity(embedding_0, embedding_1):
    # 相似度对比
    similarity_wav = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
    embedding1 = torch.Tensor(embedding_0)
    embedding2 = torch.Tensor(embedding_1)
    result = similarity_wav(embedding1,embedding2)
    return result

def join_v1(_path, _time, pwd_path, state):
    embedding_list = []
    time_list = []
    path_list = []
    for i, value in enumerate(_path):
        embedding = data_embedding(value, state)
        if embedding != None:
            embedding_list.append(embedding)
            time_list.append(_time[i])
            path_list.append(value)

    wav_len = len(embedding_list)
    if wav_len == 1:
        return []

    if sum(time_list) < Args.wav_time or wav_len < 2:
        return []
    # 加个相似度判断  data_embedding  假设用的是url
    print("1")
    if wav_len == 2 and similarity(embedding_list[0], embedding_list[1]) > 0.8 and sum(time_list) > Args.wav_time:
        out = [os.path.join(pwd_path, "wav_join_two.wav")]
        print(sum(time_list), path_list, "1")
        # wav_join(out[0], path_list)
        return out
    elif wav_len == 2:
        return []

    # a, join_time, join_list = 0, 0, []
    # 加个相似度判断  data_embedding

    join_list = []
    time_list_falg = []
    res = []
    first = embedding_list[0]
    for i, value in enumerate(embedding_list[1:]):
        print("2")
        print(path_list[0])
        if similarity(first, value) > 0.8:
            join_list.append(path_list[i+1])
            time_list_falg.append(time_list[i+1])
        
        if sum(time_list_falg) > Args.wav_time:
            new_name = os.path.join(pwd_path, "wav_join_two_%d.wav"%(i))
            print(sum(time_list_falg), join_list, ":2")
            # wav_join(new_name, join_list)
            res.append(join_list)
            first = embedding_list[i+1]
            join_list = [path_list[i+1]]
            time_list_falg = [time_list[i+1]]
    return res


def file_dispose(file_path, state):
    # file_path: 相对路径
    join_path = []
    join_time = []
    for i in os.listdir(file_path):
        path = os.path.join(file_path, i)
        wav_time = read_wav_time(path)  # 获取时间
        # print(i, wav_time)
        if wav_time < Args.wav_time:
            join_path.append(path.split("/")[-1])
            join_time.append(wav_time)
    print(join_time)
    if Args.json_flag == 0:
        return join_v1(join_path, join_time, file_path, state)



if __name__ == "__main__":
    file_dispose("./temporary/19991227709", "black")
    # state = "black"
    # print(data_embedding("H_JSSR77667835_20220815950216_00000036_otalk_zhuanban.wav", state))
    pass



