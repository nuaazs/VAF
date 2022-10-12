import os
import requests
import datetime
import random
import json
from multiprocessing.dummy import Pool as ThreadPool
import logging
import pandas as pd

# from tomlkit import value


class Args:
    # ip   default:127.0.0.1
    ip = "127.0.0.1"
    # 端口号    default: 8187 ->gpu 和 8188 -> cpu
    port = 8187
    # 接口名称   default: test|register
    path = "test"
    # mode   default: url|file
    mode = "url"
    # 线程池| 数量
    poll_number = 10
    # 开启线程功能
    poll_switch = True
    # 黑库
    file_path_black = "/mnt/panjiawei/run_2/data/new/zhuanban.txt"
    # 桶名称
    bucket_name_black = "black"
    # 灰库
    file_path_gray = "/mnt/panjiawei/run_2/data/new/noblack.txt"
    bucket_name_gray = "gray"

    rclone = "rclone"

    # 验证功能部分

    # 日志级别   0 1 2 3 4 5 debug info warning error critical
    log_level = 1
    # 实时保存数据
    timely_save = True
    test_columns = [
        "code",
        "status",
        "inbase",
        "hit_scores",
        "blackbase_phone",
        "top_10",
        "err_msg",
        "clip",
        "before_vad_length",
        "after_vad_length",
        "self_test_score_mean",
        "self_test_score_min",
        "self_test_score_max",
        "self_test_before_score",
    ]
    used_time = [
        "download_used_time",
        "vad_used_time",
        "classify_used_time",
        "embedding_used_time",
        "self_test_used_time",
        "to_database_used_time",
        "test_used_time",
    ]

    register_columns = [
        "code",
        "status",
        "err_type",
        "err_msg",
        "name",
        "phone",
        "uuid",
        "hit",
        "register_time",
        "province",
        "city",
        "phone_type",
        "area_code",
        "zip_code",
        "self_test_score_mean",
        "self_test_score_min",
        "self_test_score_max",
        "self_test_before_score",
        "call_begintime",
        "call_endtime",
        "max_class_index",
        "preprocessed_file_path",
        "show_phone",
        "before_vad_length",
        "after_vad_length",
    ]

    # 日志保存路径
    log_path = "./plog/"


class Log:
    """
    logger.debug('This is a debug message!')
    logger.info('This is a info message!')
    logger.warning('This is a warning message!')
    logger.error('This is a error message!')
    logger.critical('This is a critical message!')
    """

    def __init__(self):
        self.file_name = Args.log_path + "info.log"
        # self.file_name = "info.log"
        self.check()
        self.log_format = "%(asctime)s[%(levelname)s]: %(message)s"
        self.log_grade = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]
        self.level = self.log_grade[Args.log_level]
        self.logger = self.run()

    def check(self):
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        with open(self.file_name, "w") as f1:
            f1.writelines("Logs start running!!!\n")

    def run(self):
        logging.basicConfig(
            filename=self.file_name, level=self.level, format=self.log_format
        )
        return logging.getLogger()


class CallingInterface:
    def __init__(self, state):
        # url
        self.url_path = "http://192.168.3.202:9000"
        self.inbase_out = []
        self.url = ""
        self.bucket_name = ""
        self.state = state
        self.ip = Args.ip
        self.port = Args.port
        self.mode = Args.mode
        self.poll_switch = Args.poll_switch
        self.poll_number = Args.poll_number
        self.port_type = ""
        self.columns = ""
        self.file_path = ""
        if self.state == "test":
            self.columns = Args.test_columns
            self.file_path = Args.file_path_gray
        elif self.state == "register":
            self.columns = Args.register_columns
            self.file_path = Args.file_path_black
        self.used_time = Args.used_time
        self.txt_file_info = self.get_txt_file()

    def info_neaten(self, resp, wav):
        wav = wav.split("/")[-1]
        resp_json = resp.json()
        print(json.dumps(resp_json, sort_keys=False, indent=4))
        print(wav)
        try:
            file_name, phone = self.txt_file_info.get(wav)
        except TypeError:
            if self.state == "test":
                logger.warning(self.state + ": " + wav + "not in noblack.txt")
            elif self.state == "register":
                logger.warning(self.state + ": " + wav + "not in zhuanban.txt")
            file_name, phone = wav, "nan"

        temporary_data = [file_name, phone]

        for i in self.columns:
            value = str(resp_json.get(i))
            if i == "blackbase_phone" or i == "top_10":
                value = value.replace(",", "_")
            if i == "err_msg":
                value = value.replace("\n", " ")
            temporary_data.append(value)
        used_time = resp_json.get("used_time")
        for i in self.used_time:
            temporary_data.append(str(used_time.get(i)))

        self.inbase_out.append(temporary_data)
        if Args.timely_save:
            with open(
                Args.log_path + self.port_type + "_timely_save_file.csv", "a+"
            ) as f1:
                f1.writelines(",".join(temporary_data) + "\n")

    def test_port(self, wav):
        wav_url = self.url_path + "/" + self.bucket_name + "/" + wav
        endtime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        begintime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        phone = random.randint(11111111111, 99999999999)
        values = {
            "spkid": str(phone),
            "show_phone": "15151832002",
            "wav_url": wav_url,
            "call_begintime": begintime,
            "call_endtime": endtime,
        }
        resp = requests.request("POST", self.url, data=values)

        self.info_neaten(resp, wav)
        logger.debug("(%s)  file %s run success." % (self.port_type, wav))

    def run_port(self, port_type, bucket_name):
        # test|register
        self.url = r"http://{0}:{1}/{2}/{3}".format(
            self.ip, self.port, port_type, self.mode
        )
        self.port_type = port_type
        wavs_gray_object = self.access_file(bucket_name)

        logger.info(
            "[label] There are %d pieces of data in the %s database"
            % (len(wavs_gray_object), self.state)
        )
        self.bucket_name = bucket_name
        if self.poll_switch:
            pool = ThreadPool(self.poll_number)
            try:
                pool.map(self.test_port, wavs_gray_object)
            except:
                logger.error("Multithreading failure!")
                raise RuntimeError("Multithreading failure!")
            pool.close()
            pool.join()
        else:
            for wav in wavs_gray_object:
                self.test_port(wav)

    def access_file(self, bucket_name):
        # read bucket object
        if Args.rclone == "rclone":
            str = r"rclone lsl minio:/%s | awk '{print $4}'" % (bucket_name)
            with os.popen(str) as f1:
                return f1.read().strip().split("\n")

    def get_txt(self, path):
        # read txt
        with open(path, "r") as f1:
            data = f1.readlines()

        check_out = []
        dict_file = {}
        for _, line in enumerate(data):
            line = line.strip().split("                ")
            if len(line) == 1:
                line = line[0].split("       ")
            if len(line) == 1:
                line = line[0].split("       ")
            if len(line) == 1:
                line = line[0].split("      ")
            if len(line) == 1:
                line = line[0].split("     ")
            if len(line) == 1:
                line = line[0].split(" ")
            check_out.append(line)
            whole, incomplete = line

            phones_ = whole.split("_")[3]

            dict_file[incomplete] = [whole, phones_]
        logger.debug("get %s file success." % (self.file_path))
        return check_out, dict_file

    def check(self, file_name, data):
        # check data
        error_log = []
        for i, value in enumerate(data):
            if len(value) != 2:
                error_log.append(
                    "The data in line %d fails, please check it ! ! !" % (i)
                )
                continue
            if not value[0].endswith("wav"):
                error_log.append(
                    "The data in line %d fails, please check it ! ! !" % (i)
                )
            if not value[1].endswith("wav"):
                error_log.append(
                    "The data in line %d fails, please check it ! ! !" % (i)
                )
        if len(error_log) != 0:
            raise TypeError(file_name + str(error_log))
        logger.debug("check %s file success." % (file_name))

    def get_txt_file(self):
        check_data, txt_file_info = self.get_txt(self.file_path)
        self.check(self.file_path, check_data)
        logger.debug("read txt file success.")
        return txt_file_info


def acquire_data(state):
    port = CallingInterface(state)
    columns = ""
    if state == "test":
        columns = ["wav", "Zphone"] + Args.test_columns + Args.used_time
    elif state == "register":
        columns = ["wav", "Zphone"] + Args.register_columns + Args.used_time

    if Args.timely_save:
        with open(Args.log_path + state + "_timely_save_file.csv", "a+") as f1:
            f1.writelines(",".join(columns) + "\n")
    if state == "register":
        port.run_port(state, Args.bucket_name_black)
    elif state == "test":
        port.run_port(state, Args.bucket_name_gray)
    data = pd.DataFrame(port.inbase_out, columns=columns)
    return data


def matrix_prin(real, label):

    TP = real.count("1_true") + real.count("1_True")
    FN = real.count("1_false") + real.count("1_False")

    FP = real.count("0_true") + real.count("0_True")
    TN = real.count("0_false") + real.count("0_False")
    try:
        logger.info("==========》 【" + label + "】")
        logger.info("              ------------------------------------|")
        logger.info("              |           prediction              |")
        logger.info("              ------------------------------------|")
        logger.info("              |       1         |        0        |")
        logger.info("--------------------------------------------------|")
        logger.info("|         | 1 |   TP: %-8d  |  TN: %-8d   |" % (TP, TN))
        logger.info("| correct |---------------------------------------|")
        logger.info("|         | 0 |   FP: %-8d  |  FN: %-8d   |" % (FP, FN))
        logger.info("--------------------------------------------------|")

        logger.info(label + "[label] ACC: " + str((TP + TN) / (TP + TN + FP + FN)))
        logger.info(label + "[label] PPV: " + str((TP) / (TP + FP)))
        logger.info(label + "[label] TPR: " + str(TP / (TP + FN)))
        logger.info(label + "[label] FNR: " + str(FN / (TP + FN)))
        logger.info(label + "[label] FPR: " + str(FP / (TN + FP)))
        logger.info(label + "[label] TNR: " + str(TN / (TN + FP)))
    except ZeroDivisionError:
        logger.error("division by zero." + real)


def run():
    # balck
    balck_data = acquire_data("register")
    # TODO: id,wav,status,msg,valid_length,score
    balck_success = balck_data[balck_data["status"] == "success"]
    balck_error = balck_data[balck_data["status"] == "error"]
    balck_error.to_csv(Args.log_path + "balck_error_data.csv")

    logger.info("balck test valid data: %d" % (len(balck_success["status"])))
    logger.info(
        "balck test invalid data: %d.  please findv %sbalck_error_data.csv "
        % (len(balck_error["status"]), Args.log_path)
    )
    balck_phone = set(balck_success["Zphone"])
    logger.info("balck_phone : " + str(balck_phone))
    # gray
    gray_data = acquire_data("test")
    gray_success = gray_data[gray_data["status"] == "success"]
    gray_error = gray_data[gray_data["status"] == "error"]
    gray_error.to_csv(Args.log_path + "gray_error_data.csv")
    logger.info("gray test valid data: %d" % (len(gray_success["status"])))
    logger.info(
        "gray test invalid data: %d.  please findv %sgray_error_data.csv "
        % (len(gray_error["status"]), Args.log_path)
    )

    real = []
    dict_phone = {}
    for name, inbase, phone in zip(gray_success["wav"], gray_success["inbase"], gray_success["Zphone"]):
        if dict_phone.get("Zphone") == None:
            dict_phone[phone] = [inbase, name]
        else:
            inbase_ = inbase or dict_phone[phone][0]
            dict_phone[phone] = [inbase_, name]

        if phone in balck_phone:
            # TODO：
            if inbase:
                real.append("1_true")
            else:
                real.append("1_false")

            # real.append("1_" + str(inbase)) # 1_
            
        else:
            if inbase:
                real.append("0_false")
            else:
                real.append("0_true")
            # real.append("0_" + str(inbase))

    matrix_prin(real, "file")

    real_ = []
    for _phone in dict_phone.keys():
        inbase, name = dict_phone.get(_phone)
        if _phone in balck_phone:
            real_.append("1_" + str(inbase))
        else:
            real_.append("0_" + str(inbase))
    matrix_prin(real, "individual")

    # top
    top = []
    for Zphone, Bphone in zip(gray_success["Zphone"], gray_success["blackbase_phone"]):
        Bphone = Bphone.split(",")
        if Zphone == Bphone[0]:
            top.append("top1")
            continue
        if Zphone in Bphone[:5]:
            top.append("top5")
            continue
        if Zphone in Bphone:
            top.append("top10")
            continue


if __name__ == "__main__":
    if not os.path.exists(Args.log_path):
        os.mkdir(Args.log_path)
    logger = Log().logger
    run()
