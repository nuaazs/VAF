# coding = utf-8
# @Time    : 2022-09-05  09:47:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Register and identify interfaces.

import datetime
from flask import request

# utils
from utils.orm.database import to_database
from utils.orm.database import get_embedding

from utils.orm import check_spkid
from utils.orm import get_spkinfo
from utils.orm import delete_spk


from utils.orm import to_log
from utils.log import err_logger
from utils.log import logger
from utils.preprocess import save_url
from utils.preprocess import save_file
from utils.preprocess import vad
from utils.preprocess import resample
from utils.encoder import encode
from utils.preprocess import classify
from utils.register import register
from utils.test import test
from utils.encoder import similarity
from utils.orm.db_utils import mysql_handler

import torch

# cfg
import cfg


class OutInfo:
    """
    out dict info
    """
    used_time = {
            "download_used_time": 0,
            "vad_used_time": 0,
            "classify_used_time": 0,
            "embedding_used_time": 0,
            "self_test_used_time": 0,
            "to_database_used_time": 0,
            "test_used_time": 0,
        }
    def __init__(self):
        self.response = {"code": 2000, "status": "error"}
        self.response_check_new = {
            "code": 2000,
            "status": "error",
            "err_type": "None",
            "err_msg": "None",
            "inbase": True,
            "code": 2000,
            "replace": False
        }

    def response_error(self, spkid, err_type, err_msg, used_time=None, oss_path="None"):
        err_logger.info("%s, %s, %s, %s"%(spkid, oss_path, err_type, err_msg))
        self.response["err_type"] = err_type
        self.response["err_msg"] = err_msg
        if used_time != None:
            self.response["used_time"] = used_time
        return self.response

    def response_vad(self, err_type, err_msg, used_time=None):
        self.response["err_type"] = err_type
        self.response["err_msg"] = err_msg
        if used_time != None:
            self.response["used_time"] = used_time
        return self.response

    def response_check(self, err_type, err_msg):
        self.response_check_new["err_type"] = err_type
        self.response_check_new["err_msg"] = err_msg
        return self.response


def general(request_form, get_type="url", action_type="test"):
    """_summary_

    Args:
        request_form (form):{'spkid': '1', 'wav_url': 'http://xxxxx/1.wav', 'wav_channel': 1}
        get_type (str, optional): url or file. Defaults to "url".
        action (str, optional): register or test. Defaults to "test".

    Returns:
        _type_: response: {'code':2000,'status':"success",'err_type': '1', 'err_msg': ''}
        * err_type:
            # 1. The file format is incorrect       
            # 2. File parsing error 
            # 3. File download error
            # 4. spkid repeat
            # 5. The file has no valid data (very poor quality)  
            # 6. The valid duration of the file does not meet the requirements
            # 7. The file quality detection does not meet the requirements 
            #    (the environment is noisy or there are multiple speakers)
    """

    start = datetime.datetime.now()

    new_spkid = request_form["spkid"]
    call_begintime = request_form.get("call_begintime", "1999-02-18 10:10:10")
    call_endtime = request_form.get("call_endtime", "1999-02-18 10:10:10")
    show_phone = request_form.get("show_phone", new_spkid)

    if action_type == "register":
        action_num = 2
    if action_type == "test":
        action_num = 1

    # ID duplication detection.
    # TODO:判断更新的逻辑
    do_update = False
    if check_spkid(new_spkid) and action_type == "register":
        do_update = True
        old_info = get_spkinfo(new_spkid)
        last_days = int((datetime.datetime.now() - old_info["register_time"]).days)
        if last_days < cfg.UPDATE_DAYS:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 4,
                "err_msg": f"ID error.\nID: {new_spkid} already exists.",
            }
            err_logger.info(
                f"{new_spkid},None,{response['err_type']},{response['err_msg']}"
            )
            return response
        else:
            query_sql = f"delete from speaker where phone='{new_spkid}'"
            _ = mysql_handler.delete(query_sql)
            print(f"phone:{new_spkid}, The user audio has timed out and will be updated.")

    # STEP 1: Get wav file.
    if get_type == "file":
        new_file = request.files["wav_file"]
        filename = new_file.filename
        if (".wav" not in filename) and (".mp3" not in filename):
            err_msg = "File type error.\nOnly support wav or mp3 files."
            to_log(
                phone = new_spkid,
                action_type = action_type,
                err_type = 1,
                message = err_msg,
                file_url = "",
                preprocessed_file_path = "",
                show_phone = show_phone,
            )
            return OutInfo().response_error(new_spkid, 1, err_msg, OutInfo.used_time)
        try:
            filepath, oss_path = save_file(file=new_file, spk=new_spkid)
        except Exception as e:
            err_logger.info(e)
            print(e)
            err_msg = "Form file save error. File save faild."
            to_log(
                phone=new_spkid,
                action_type=action_type,
                err_type=2,
                message=err_msg,
                file_url="",
                preprocessed_file_path="",
                show_phone=show_phone,
            )
            return OutInfo().response_error(new_spkid, 2, err_msg, OutInfo.used_time)

    elif get_type == "url":
        new_url = request.form.get("wav_url")
        try:
            filepath, oss_path = save_url(url=new_url, spk=new_spkid)
        except Exception as e:
            err_logger.info(e)
            print(e)
            err_msg = f"URL file save error. Download {new_url} faild."
            to_log(
                phone=new_spkid,
                action_type=action_type,
                err_type=3,
                message=err_msg,
                file_url="",
                preprocessed_file_path="",
                show_phone=show_phone,
            )
            return OutInfo().response_error(new_spkid, 3, err_msg, OutInfo.used_time)

    OutInfo.used_time["download_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()

    # STEP 2: VAD
    try:
        wav = resample(wav_filepath=filepath, action_type=action_type)
        vad_result = vad(wav=wav, spkid=new_spkid, action_type=action_type)
        if cfg.SAVE_PREPROCESSED_OSS:
            preprocessed_file_path = vad_result["preprocessed_file_path"]
        else:
            preprocessed_file_path = ""
    except Exception as e:
        err_logger.info(e)
        err_msg = "VAD and upsample error. No useful data in {filepath}."
        to_log(
            phone=new_spkid,
            action_type=action_type,
            err_type=5,
            message=f"vad error",
            file_url=oss_path,
            preprocessed_file_path="",
            show_phone=show_phone,
        )
        return OutInfo().response_error(new_spkid, 5, err_msg, OutInfo.used_time, oss_path)

    OutInfo.used_time["vad_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()

    # STEP 3: Self Test
    try:
        self_test_result = encode(wav_torch_raw=vad_result["wav_torch"], action_type=action_type)
    except Exception as e:
        err_logger.info(e)
        print(e)
        err_msg = f"Self Test faild. No useful data in {filepath}."
        to_log(
            phone=new_spkid,
            action_type=action_type,
            show_phone=show_phone,
            err_type=5,
            message=f"self test error",
            file_url=oss_path,
            preprocessed_file_path=preprocessed_file_path,
        )
        return OutInfo().response_error(new_spkid, 5, err_msg, OutInfo.used_time, oss_path)

    OutInfo.used_time["self_test_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()

    msg = self_test_result["msg"]
    if not self_test_result["pass"]:
        err_type = self_test_result["err_type"]
        to_log(
            phone=new_spkid,
            action_type=action_type,
            show_phone=show_phone,
            err_type=err_type,
            message=str(msg),
            file_url=oss_path,
            preprocessed_file_path=preprocessed_file_path,
        )
        return OutInfo().response_error(new_spkid, err_type, msg, OutInfo.used_time, oss_path)

    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    if cfg.CLASSIFY:
        class_num = classify(embedding)
    else:
        class_num = 999

    OutInfo.used_time["classify_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()

    # TODO:执行更新声纹特征
    if do_update:
        
        if old_info == None:
            return {
                "inbase": False,
                "code": 2000,
                "status": "success",
                "replace": False,
                "err_msg": "activate ID not exist.",
                "err_type": 0,
            }
        old_class = old_info["class_number"]
        old_score = old_info["self_test_score_mean"]
        old_valid_length = old_info["valid_length"]
        print(f"now get embedding from :{new_spkid}")
        old_embedding = get_embedding(new_spkid)

        embedding_similarity = (
            similarity(embedding, torch.FloatTensor(old_embedding).cuda())
            .detach()
            .cpu()
            .numpy()
        )
        score = float(self_test_result["mean_score"])
        if embedding_similarity >= cfg.UPDATE_TH and score >= old_score - 0.05:
            delete_spk(new_spkid)
            return general(request_form, get_type=get_type, action_type="register")

    # STEP 5: Test or Register
    if action_num == 1:
        return test(
            embedding,
            wav,
            new_spkid,
            class_num,
            oss_path,
            self_test_result,
            call_begintime,
            call_endtime,
            before_vad_length=vad_result["before_length"],
            after_vad_length=vad_result["after_length"],
            preprocessed_file_path=preprocessed_file_path,
            show_phone=show_phone,
            used_time=OutInfo.used_time,
        )

    elif action_num == 2:
        return register(
            embedding,
            wav,
            new_spkid,
            class_num,
            oss_path,
            self_test_result,
            call_begintime,
            call_endtime,
            preprocessed_file_path=preprocessed_file_path,
            show_phone=show_phone,
            before_vad_length=vad_result["before_length"],
            after_vad_length=vad_result["after_length"],
            used_time=OutInfo.used_time,
        )


def get_score(request_form, get_type="url"):
    # STEP 1: Get wav file.
    if get_type == "file":
        new_spkid1 = request.form.get("spkid1")
        new_spkid2 = request.form.get("spkid2")
        new_file1 = request.files["wav_file1"]
        new_file2 = request.files["wav_file2"]
        filename1 = new_file1.filename
        filename2 = new_file2.filename
        if ((".wav" not in filename1) and (".mp3" not in filename1)) or \
           ((".wav" not in filename2) and (".mp3" not in filename2)):
            return OutInfo().response_vad(1, "Only support wav or mp3 files.")
        try:
            filepath1, _oss_path1 = save_file(file=new_file1, spk=new_spkid1)
            filepath2, _oss_path2 = save_file(file=new_file2, spk=new_spkid2)
        except Exception as e:
            print(e)
            return OutInfo().response_vad(2, "File save faild.")

    elif get_type == "url":
        new_url1 = request.form.get("wav_url1")
        new_url2 = request.form.get("wav_url2")
        new_spkid1 = request.form.get("spkid1")
        new_spkid2 = request.form.get("spkid2")

        try:
            filepath1, _oss_path1 = save_url(url=new_url1, spk=new_spkid1)
            filepath2, _oss_path2 = save_url(url=new_url2, spk=new_spkid2)
        except Exception as e:
            print(e)
            return OutInfo().response_vad(3, "File:%s or %s save faild."%(new_url1, new_url2))

    # STEP 2: VAD
    try:
        wav1 = resample(filepath1, action_type="register")
        wav2 = resample(filepath2, action_type="register")
        vad_result1 = vad(wav1, new_spkid1)
        vad_result2 = vad(wav2, new_spkid2)
        before_vad_length1 = vad_result1["before_length"]
        before_vad_length2 = vad_result2["before_length"]
        after_vad_length1 = vad_result1["after_length"]
        after_vad_length2 = vad_result1["after_length"]
    except Exception as e:
        print(e)
        err_msg = "VAD and upsample faild. No useful data in %s or %s."%(filepath1, filepath2)
        return OutInfo().response_vad(5, err_msg)

    # STEP 3: Self Test
    try:
        self_test_result1 = encode(wav_torch_raw=vad_result1["wav_torch"])
        self_test_result2 = encode(wav_torch_raw=vad_result2["wav_torch"])

    except Exception as e:
        print(e)
        err_msg = "Self Test faild. No useful data in %s %s."%(filepath1, filepath2)
        return OutInfo().response_vad(5, err_msg)

    msg = self_test_result1["msg"]
    if not self_test_result1["pass"]:
        err_type = self_test_result1["err_type"]
        return OutInfo().response_vad(err_type, "wav1:" + msg)

    msg = self_test_result2["msg"]
    if not self_test_result2["pass"]:
        err_type = self_test_result2["err_type"]
        return OutInfo().response_vad(err_type, "wav2:" + msg)

    # STEP 4: Encoding
    embedding1 = self_test_result1["tensor"]
    embedding2 = self_test_result2["tensor"]
    result = similarity(embedding1, embedding2).detach().cpu().numpy()
    response = {
        "code": 2000,
        "status": "success",
        "err_type": 0,
        "err_msg": f"",
        "socre": float(result[0]),
        "before_vad_length1": before_vad_length1,
        "before_vad_length2": before_vad_length2,
        "after_vad_length1": after_vad_length1,
        "after_vad_length2": after_vad_length2,
    }
    return response


def check_new(request_form, get_type="url"):
    # STEP 1: Check old data
    new_spkid = request.form.get("spkid")
    print(new_spkid)
    has_spkid = check_spkid(new_spkid)
    print("has_spkid:", has_spkid)
    if has_spkid:
        # TODO:获取历史文件信息
        old_info = get_spkinfo(new_spkid)
        if old_info == None:
            return {
                "inbase": False,
                "code": 2000,
                "status": "success",
                "replace": False,
                "err_msg": "activate ID not exist.",
                "err_type": 0,
            }
        old_score = old_info["self_test_score_mean"]
        print(f"now get embedding from :{new_spkid}")
        old_embedding = get_embedding(new_spkid)
        # STEP 2: Get wav file.
        if get_type == "file":
            new_file = request.files["wav_file"]
            filename = new_file.filename
            if (".wav" not in filename) and (".mp3" not in filename):
                return OutInfo().response_check(1, "Only support wav or mp3 files.")
            try:
                filepath, oss_path = save_file(file=new_file, spk=new_spkid)
            except Exception as e:
                print(e)
                return OutInfo().response_check(2, "File save faild.")

        elif get_type == "url":
            new_url = request.form.get("wav_url")
            try:
                filepath, oss_path = save_url(url=new_url, spk=new_spkid)
            except Exception as e:
                print(e)
                return OutInfo().response_check(3, "File:%s save faild."%new_url)

        # STEP 3: VAD
        try:
            wav1 = resample(filepath, action_type="register")
            vad_result = vad(wav1, new_spkid, action_type="register")
            before_vad_length = vad_result["before_length"]
            after_vad_length = vad_result["after_length"]
        except Exception as e:
            print(e)
            return OutInfo().response_check(5, "VAD and upsample faild. No useful data in %s."%filepath)

        # STEP 3: Self Test
        try:
            self_test_result = encode(
                wav_torch_raw=vad_result["wav_torch"], action_type="register"
            )
        except Exception as e:
            print(e)
            return OutInfo().response_check(5, "Self Test faild. No useful data in %s."%filepath)

        msg = self_test_result["msg"]
        if not self_test_result["pass"]:
            err_type = self_test_result["err_type"]
            return OutInfo().response_check(err_type, "wav1:" + msg)

        # STEP 4: Encoding
        embedding = self_test_result["tensor"]

        embedding_similarity = (
            similarity(embedding, torch.FloatTensor(old_embedding).cuda())
            .detach()
            .cpu()
            .numpy()
        )
        score = float(self_test_result["mean_score"])
        if embedding_similarity >= cfg.UPDATE_TH and score >= old_score - 0.05:
            response = {
                "code": 2000,
                "status": "success",
                "err_type": 0,
                "err_msg": f"",
                "similarity": float(embedding_similarity[0]),
                "before_vad_length": before_vad_length,
                "after_vad_length": after_vad_length,
                "old_score": old_score,
                "score": score,
                "inbase": True,
                "code": 2000,
                "replace": True,
                "err_msg": "None",
            }
            return response
        else:
            if embedding_similarity > cfg.UPDATE_TH:
                response = {
                    "code": 2000,
                    "status": "success",
                    "err_type": 0,
                    "err_msg": f"",
                    "similarity": float(embedding_similarity[0]),
                    "before_vad_length": before_vad_length,
                    "after_vad_length": after_vad_length,
                    "old_score": old_score,
                    "score": score,
                    "inbase": True,
                    "code": 2000,
                    "replace": False,
                    "err_msg": "相似度过低",
                }
                return response
            else:
                response = {
                    "code": 2000,
                    "status": "success",
                    "err_type": 0,
                    "err_msg": f"",
                    "similarity": float(embedding_similarity[0]),
                    "before_vad_length": before_vad_length,
                    "after_vad_length": after_vad_length,
                    "old_score": old_score,
                    "score": score,
                    "inbase": True,
                    "code": 2000,
                    "replace": False,
                    "err_msg": "音频质量没有提升",
                }
                return response

    else:
        return {
            "inbase": False,
            "code": 2000,
            "status": "success",
            "replace": False,
            "err_msg": "None",
            "err_type": 0,
        }


def update_embedding(request_form, get_type="url"):
    # TODO：删除旧的信息
    spkid = request.form.get("spkid")
    print(f"delete spk {spkid}")
    delete_spk(spkid)
    return general(request_form, get_type=get_type, action_type="register")
