# coding = utf-8
# @Time    : 2022-09-05  09:47:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Register and identify interfaces.

import os
import time
from flask import request
from datetime import datetime

import cfg
from utils.orm import check_spkid
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

def general(request_form,get_type="url",action_type="test"):
    """_summary_

    Args:
        request_form (form):   request.form:{'spkid': '1', 'wav_url': 'http://www.baidu.com/1.wav', 'wav_channel': 1}
        get_type (str, optional): url or file. Defaults to "url".
        action (str, optional): register or test. Defaults to "test".

    Returns:
        _type_: response: {'code':2000,'status':"success",'err_type': '1', 'err_msg': ''}
        * err_type 说明：
            # 1. 文件格式不对
            # 2. 文件解析错误
            # 3. 文件下载错误
            # 4. spkid重复
            # 5. 文件没有有效数据（质量极差）
            # 6. 文件有效时长不满足要求
            # 7. 文件质量检测不满足要求（环境噪声较大或有多个说话人干扰）
    """
    new_spkid = request_form["spkid"]
    if cfg.CHECK_DUPLICATE:
        if check_spkid(new_spkid):
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 4,
                "err_msg": f"ID: {new_spkid} already exists."
            }
            err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
            return response
    wav_channel = cfg.WAV_CHANNEL
    call_begintime = request_form.get("call_begintime","1999-02-18 10:10:10")
    call_endtime = request_form.get("call_endtime","1999-02-18 10:10:10")

    # STEP 1: Get wav file.
    if get_type == "file":
        new_file = request.files["wav_file"]
        filename = new_file.filename
        if (".wav" not in filename) and (".mp3" not in filename):
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 1,
                "err_msg": "Only support wav or mp3 files."
            }
            to_log(phone=new_spkid, action_type=action_type, err_type=response["err_type"], message=response["err_msg"],file_url="",preprocessed_file_path="")
            err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
            return response
        try:
            filepath,oss_path = save_file(file=new_file,spk=new_spkid)
        except Exception as e:
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 2,
                "err_msg": f"File save faild.",
            }
            to_log(phone=new_spkid, action_type=action_type, err_type=response["err_type"], message=response["err_msg"],file_url="",preprocessed_file_path="")
            err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
            return response
    elif get_type == "url":
        new_url =request.form.get("wav_url")
        try:
            filepath,oss_path = save_url(url=new_url,spk=new_spkid)
        except Exception as e:
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 3,
                "err_msg": f"File:{new_url} save faild.",
            }
            to_log(phone=new_spkid, action_type=action_type, err_type=response["err_type"], message=response["err_msg"],file_url="",preprocessed_file_path="")
            err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
            return response

    # STEP 2: VAD    
    try:
        wav = resample(filepath)
        vad_result = vad(wav,new_spkid)
        preprocessed_file_path = vad_result["preprocessed_file_path"]
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"VAD and upsample faild. No useful data in {filepath}.",
        }
        to_log(phone=new_spkid, action_type=action_type, err_type=5, message=f"vad error",file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
        err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        return response

    # STEP 3: Self Test
    try:
        print(type(vad_result["wav_torch"]))
        self_test_result = encode(wav_torch=vad_result["wav_torch"])

    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"Self Test faild. No useful data in {filepath}.",
        }
        to_log(phone=new_spkid, action_type=action_type, err_type=5, message=f"self test error",\
                file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
        err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        return response
    
    msg = self_test_result["msg"]
    if not self_test_result["pass"]:
        err_type = self_test_result["err_type"]
        response = {
            "code": 2000,
            "status": "error",
            "err_type": err_type,
            "err_msg": msg
            }
        to_log(phone=new_spkid, action_type=action_type, err_type=err_type, message=f"{msg}",file_url=oss_path,\
                preprocessed_file_path=preprocessed_file_path)
        err_logger.info(f"{new_spkid},{oss_path},{err_type},{msg}")
        return response

    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    if cfg.CLASSIFY:
        class_num = classify(embedding)
    else:
        class_num = 999
    
    # STEP 5: Test or Register
    if action_type == "test":
        return test(embedding,wav,new_spkid,class_num,oss_path,self_test_result,call_begintime,call_endtime,after_vad_length=vad_result["after_length"],preprocessed_file_path=preprocessed_file_path)

    elif action_type == "register":
        return register(embedding,wav,new_spkid,class_num,oss_path,self_test_result,
                call_begintime,call_endtime,after_vad_length=vad_result["after_length"],
                preprocessed_file_path=preprocessed_file_path)
