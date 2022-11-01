import pandas as pd
import os
import random
import json
import datetime
import requests

class Args:
    pwd = os.getcwd()
    # 数据集路径
    data_warehouse = "/mnt/dataset/cjsd"
    # 数据保存路径
    scv = os.path.join(pwd, "new/")
    # csv文件路径
    csv_path = os.path.join(pwd, "new/cjsd.csv")

    # 黑库数量
    black_number = 40
    # 黑库路径
    balck_path = os.path.join(pwd, "data/black/")
    # 灰库路径
    gray_path = os.path.join(pwd, "data/gray/")

    # 灰库其他样例
    gray_nubmer = 100



def test_test(self, wav):
    wav_url = self.url_path + "/" + self.bucket_name + "/" + wav
    print("wav_url", wav_url)
    # wav_url = r"http://192.168.3.202:9000/gray/H_JSSR10942663_20220815641817_00000070_otalk_noblack.wav"
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    try:
        file_name, phone = self.txt_file_info.get(wav)
    except TypeError:
        if self.state == "test":
            phone = random.randint(11111111111, 99999999999)
        file_name, phone = wav, random.randint(11111111111, 99999999999)

    print(phone)
    values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
    resp = requests.request("POST", self.url, data = values)


def test_register(self, wav):
    wav_url = self.url_path + "/" + self.bucket_name + "/" + wav
    print("wav_url", wav_url)
    # wav_url = r"http://192.168.3.202:9000/gray/H_JSSR10942663_20220815641817_00000070_otalk_noblack.wav"
    endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    try:
        file_name, phone = self.txt_file_info.get(wav)
    except TypeError:
        if self.state == "test":
            phone = random.randint(11111111111, 99999999999)
        file_name, phone = wav, random.randint(11111111111, 99999999999)

    print(phone)
    values = {"spkid": str(phone),"show_phone": "15151832002","wav_url":wav_url,"call_begintime":begintime,"call_endtime":endtime}
    resp = requests.request("POST", self.url, data = values)


if __name__ == "__main__":
    data = pd.read_csv(Args.csv_path)
    info = {}
    # 对
    not_one_file_data = data[data["wav_number"] == 2]
    zhuanban = []
    noblack = []
    speech_duration = list(not_one_file_data["speech_duration"])
    for i, phone in enumerate(not_one_file_data["speaker_id"]):
        phone_falg = data[data["speaker_id"] == phone]
        phone = str(phone)
        new_path = os.path.join(Args.data_warehouse, phone)
        if not os.path.exists(new_path):
            continue
        source_path_1 = os.path.join(new_path, "1.wav")

        try:
            index = list(phone_falg["wav_number"]).index(1)
        except ValueError:
            continue
        size = data.loc[index][2] / 1000

        if i < Args.black_number:
            try:
                index = list(phone_falg["wav_number"]).index(2)
            except ValueError:
                continue
            source_path_2 = os.path.join(new_path, "2.wav")
            jssr = str(random.randint(10000000, 99999999))
            date = "20220815" + str(random.randint(100000, 999999))
            file_name_zhuanban_previous = "H_JSSR%s_%s_%s_otalk_zhuanban.wav" % (jssr, date, phone)
            file_name_zhuanban_new = "H_JSSR%s_%s_%s_otalk_zhuanban.wav" % (jssr, date, "%08d"%i)
            info[file_name_zhuanban_new] = size

            zhuanban.append([file_name_zhuanban_previous, file_name_zhuanban_new])
            print("cp " + source_path_1 + " " + os.path.join(Args.balck_path, file_name_zhuanban_new))

            file_name_noblack_previous = "H_JSSR%s_%s_%s_otalk_noblack.wav" % (jssr, date, phone)
            file_name_noblack_new = "H_JSSR%s_%s_%s_otalk_noblack.wav" % (jssr, date, "%08d"%i)
            noblack.append([file_name_noblack_previous, file_name_noblack_new])

            size = data.loc[index][2] / 1000
            info[file_name_noblack_new] = size

            print("cp " + source_path_2 + " " + os.path.join(Args.gray_path, file_name_noblack_new))
        elif i < Args.black_number + Args.gray_nubmer:
            jssr = str(random.randint(10000000, 99999999))
            date = "20220815" + str(random.randint(100000, 999999))
            file_name_noblack_previous = "H_JSSR%s_%s_%s_otalk_noblack.wav" % (jssr, date, phone)
            file_name_noblack_new = "H_JSSR%s_%s_%s_otalk_noblack.wav" % (jssr, date, "%08d" % i)
            info[file_name_noblack_new] = size
            noblack.append([file_name_noblack_previous, file_name_noblack_new])
            print("cp " + source_path_1 + " " + os.path.join(Args.gray_path, file_name_noblack_new))

    with open(Args.scv + "zhuanban.txt", "w") as z1:
        for i, j in zhuanban:
            z1.writelines(i + " " + j + "\n")
    with open(Args.scv + "noblack.txt", "w") as n1:
        for i, j in noblack:
            n1.writelines(i + " " + j + "\n")
    with open(Args.scv + "json.json", "w") as json_1:
        json.dump(info, json_1)
