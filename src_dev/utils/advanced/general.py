# coding = utf-8
# @Time    : 2022-09-05  09:47:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Register and identify interfaces.

import datetime
from flask import request

# utils
from utils.preprocess import save_url
from utils.preprocess import save_file
from utils.preprocess import vad
from utils.preprocess import resample
from utils.encoder import encode
from utils.preprocess import classify
from utils.encoder import similarity

import torch

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
    used_time = {
        "download_used_time": 0,
        "vad_used_time": 0,
        "classify_used_time": 0,
        "embedding_used_time": 0,
        "self_test_used_time": 0,
        "to_database_used_time": 0,
        "test_used_time": 0,
    }

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
    if check_spkid(new_spkid):

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
            do_update = True
            print(f"start checking ... to update spk {new_spkid}")

    # STEP 1: Get wav file.
    if get_type == "file":
        new_file = request.files["wav_file"]
        filename = new_file.filename
        if (".wav" not in filename) and (".mp3" not in filename):
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 1,
                "err_msg": "File type error.\nOnly support wav or mp3 files.",
                "used_time": used_time,
            }
            to_log(
                phone=new_spkid,
                action_type=action_type,
                err_type=response["err_type"],
                message=response["err_msg"],
                file_url="",
                preprocessed_file_path="",
                show_phone=show_phone,
            )
            err_logger.info(
                f"{new_spkid},None,{response['err_type']},{response['err_msg']}"
            )
            return response
        try:
            filepath, oss_path = save_file(file=new_file, spk=new_spkid)
        except Exception as e:
            err_logger.info(e)
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 2,
                "err_msg": f"Form file save error.\nFile save faild.",
                "used_time": used_time,
            }
            to_log(
                phone=new_spkid,
                action_type=action_type,
                err_type=response["err_type"],
                message=response["err_msg"],
                file_url="",
                preprocessed_file_path="",
                show_phone=show_phone,
            )
            err_logger.info(
                f"{new_spkid},None,{response['err_type']},{response['err_msg']}"
            )
            return response

    elif get_type == "url":
        new_url = request.form.get("wav_url")
        try:
            filepath, oss_path = save_url(url=new_url, spk=new_spkid)
        except Exception as e:
            err_logger.info(e)
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 3,
                "err_msg": f"URL file save error.\nDownload {new_url} faild.",
                "used_time": used_time,
            }
            to_log(
                phone=new_spkid,
                action_type=action_type,
                err_type=response["err_type"],
                message=response["err_msg"],
                file_url="",
                preprocessed_file_path="",
                show_phone=show_phone,
            )
            err_logger.info(
                f"{new_spkid},None,{response['err_type']},{response['err_msg']}"
            )
            return response
    used_time["download_used_time"] = (datetime.datetime.now() - start).total_seconds()
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
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"VAD and upsample error.\nNo useful data in {filepath}.",
            "used_time": used_time,
        }
        to_log(
            phone=new_spkid,
            action_type=action_type,
            err_type=5,
            message=f"vad error",
            file_url=oss_path,
            preprocessed_file_path="",
            show_phone=show_phone,
        )
        err_logger.info(
            f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}"
        )
        return response

    used_time["vad_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()

    # STEP 3: Self Test
    try:
        self_test_result = encode(
            wav_torch_raw=vad_result["wav_torch"], action_type=action_type
        )

    except Exception as e:
        err_logger.info(e)
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"Self Test faild.\nNo useful data in {filepath}.",
            "used_time": used_time,
        }
        to_log(
            phone=new_spkid,
            action_type=action_type,
            show_phone=show_phone,
            err_type=5,
            message=f"self test error",
            file_url=oss_path,
            preprocessed_file_path=preprocessed_file_path,
        )
        err_logger.info(
            f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}"
        )
        return response

    used_time["self_test_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()

    msg = self_test_result["msg"]
    if not self_test_result["pass"]:
        err_type = self_test_result["err_type"]
        response = {
            "code": 2000,
            "status": "error",
            "err_type": err_type,
            "err_msg": msg,
            "used_time": used_time,
        }
        to_log(
            phone=new_spkid,
            action_type=action_type,
            show_phone=show_phone,
            err_type=err_type,
            message=f"{msg}",
            file_url=oss_path,
            preprocessed_file_path=preprocessed_file_path,
        )
        err_logger.info(f"{new_spkid},{oss_path},{err_type},{msg}")
        return response

    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    if cfg.CLASSIFY:
        class_num = classify(embedding)
    else:
        class_num = 999

    used_time["classify_used_time"] = (datetime.datetime.now() - start).total_seconds()
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
            used_time=used_time,
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
            used_time=used_time,
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
        if ((".wav" not in filename1) and (".mp3" not in filename1)) or (
            (".wav" not in filename2) and (".mp3" not in filename2)
        ):
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 1,
                "err_msg": "Only support wav or mp3 files.",
            }
            return response
        try:
            filepath1, oss_path1 = save_file(file=new_file1, spk=new_spkid1)
            filepath2, oss_path2 = save_file(file=new_file2, spk=new_spkid2)
        except Exception as e:
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 2,
                "err_msg": f"File save faild.",
            }
            return response
    elif get_type == "url":
        new_url1 = request.form.get("wav_url1")
        new_url2 = request.form.get("wav_url2")
        new_spkid1 = request.form.get("spkid1")
        new_spkid2 = request.form.get("spkid2")

        try:
            filepath1, oss_path1 = save_url(url=new_url1, spk=new_spkid1)
            filepath2, oss_path2 = save_url(url=new_url2, spk=new_spkid2)
        except Exception as e:
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 3,
                "err_msg": f"File:{new_url1} or {new_url2} save faild.",
            }
            return response

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

        preprocessed_file_path1 = vad_result1["preprocessed_file_path"]
        preprocessed_file_path2 = vad_result2["preprocessed_file_path"]
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"VAD and upsample faild. No useful data in {filepath1} or {filepath2}.",
        }
        return response

    # STEP 3: Self Test
    try:
        self_test_result1 = encode(wav_torch_raw=vad_result1["wav_torch"])
        self_test_result2 = encode(wav_torch_raw=vad_result2["wav_torch"])

    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"Self Test faild. No useful data in {filepath1} {filepath2}.",
        }
        return response

    msg = self_test_result1["msg"]
    if not self_test_result1["pass"]:
        err_type = self_test_result1["err_type"]
        response = {
            "code": 2000,
            "status": "error",
            "err_type": err_type,
            "err_msg": "wav1:" + msg,
        }
        return response

    msg = self_test_result2["msg"]
    if not self_test_result2["pass"]:
        err_type = self_test_result2["err_type"]
        response = {
            "code": 2000,
            "status": "error",
            "err_type": err_type,
            "err_msg": "wav2:" + msg,
        }
        return response

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


def update_embedding(request_form, get_type="url"):
    # TODO：删除旧的信息
    spkid = request.form.get("spkid")
    print(f"delete spk {spkid}")
    delete_spk(spkid)
    return general(request_form, get_type=get_type, action_type="register")
