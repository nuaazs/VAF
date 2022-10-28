# coding = utf-8
# @Time    : 2022-09-05  09:47:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Register and identify interfaces.

import torch
import datetime
from flask import request

# utils
from utils.orm.database import get_embedding
from utils.orm import check_spkid
from utils.orm import get_spkinfo
from utils.orm import delete_spk
from utils.orm import to_log
from utils.orm.db_utils import mysql_handler
from utils.log import err_logger
from utils.preprocess import save_url
from utils.preprocess import save_file
from utils.preprocess import vad
from utils.preprocess import resample
from utils.encoder import encode
from utils.preprocess import classify
from utils.register import register
from utils.test import test
from utils.encoder import similarity
from utils.info import OutInfo

# cfg
import cfg

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

    # STEP 0: ID duplication detection
    do_update = False
    if check_spkid(new_spkid) and action_type == "register":
        
        old_info = get_spkinfo(new_spkid)
        last_days = int((datetime.datetime.now() - old_info["register_time"]).days)
        if last_days < cfg.UPDATE_DAYS:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 4,
                "err_msg": f"ID error. ID: {new_spkid} already exists and it's not time to update it yet",
            }
            err_logger.info(
                f"{new_spkid},None,{response['err_type']},{response['err_msg']}"
            )
            return response
        else:
            do_update = True
            # TODO: 删除旧的信息？ 这一步先不删除，等到更新成功了再删除
            # delete_spk(new_spkid)
            print(
                f"ID:{new_spkid}, the audio has timed out and will be updated."
            )

    # STEP 1: Get wav file.
    if get_type == "file":
        new_file = request.files["wav_file"]
        filename = new_file.filename
        if (".wav" not in filename) and (".mp3" not in filename):
            err_msg = f"File type error. Only support wav or mp3 files. not {filename.split('.')[-1]}"
            to_log(
                phone=new_spkid,
                action_type=action_type,
                err_type=1,
                message=err_msg,
                file_url="",
                preprocessed_file_path="",
                show_phone=show_phone,
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

    OutInfo.used_time["download_used_time"] = (
        datetime.datetime.now() - start
    ).total_seconds()
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
        err_msg = f"VAD and upsample error. No useful data in {filepath}."
        to_log(
            phone=new_spkid,
            action_type=action_type,
            err_type=5,
            message=f"vad error",
            file_url=oss_path,
            preprocessed_file_path="",
            show_phone=show_phone,
        )
        return OutInfo().response_error(
            new_spkid, 5, err_msg, OutInfo.used_time, oss_path
        )

    OutInfo.used_time["vad_used_time"] = (
        datetime.datetime.now() - start
    ).total_seconds()
    start = datetime.datetime.now()

    # STEP 3: Self Test
    try:
        self_test_result = encode(
            wav_torch_raw=vad_result["wav_torch"], action_type=action_type
        )
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
        return OutInfo().response_error(
            new_spkid, 5, err_msg, OutInfo.used_time, oss_path
        )

    OutInfo.used_time["self_test_used_time"] = (
        datetime.datetime.now() - start
    ).total_seconds()
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
        return OutInfo().response_error(
            new_spkid, err_type, msg, OutInfo.used_time, oss_path
        )

    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    if cfg.CLASSIFY:
        class_num = classify(embedding)
    else:
        class_num = 999

    OutInfo.used_time["classify_used_time"] = (
        datetime.datetime.now() - start
    ).total_seconds()
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
        # TODO:加LOG
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
            # return general(request_form, get_type=get_type, action_type="register")

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