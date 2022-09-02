# @Time    : 2022-07-27  19:04:10
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/download_and_preprocess.py
# @Describe: Main function.

import time
from flask import request
import os
from datetime import datetime
import os
import cfg


# utils
from utils.database import add_to_database,get_all_embedding
from utils.save import save_wav_from_url,save_wav_from_file
from utils.preprocess import self_test_and_encode,vad_and_upsample
from utils.scores import test_wav,self_check
from utils.orm import add_speaker,add_hit_log
from utils.query import add_speaker_hit, add_to_log,check_spkid_already_exists
from utils.log_wraper import logger,err_logger
from encoder.encoder import *
from models.speaker import db as speaker_db,Speaker
from models.hit import db as hit_db,Hit
from utils.auto_test import auto_test
from utils.check_clip import check_clip

def get_slience_form_data(request_form,cfg,get_type="url"):
   
    wav_channel = request_form.get("wav_channel",cfg.WAV_CHANNEL)
    spkid = request_form["spkid"]

    if get_type == "file":
        new_file = request.files["wav_file"]
        filename = new_file.filename
        if (".wav" not in filename) and (".mp3" not in filename):
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 1,
                "err_msg": "Only support wav or mp3 file."
            }
            return response
        try:
            filepath,oss_path = save_wav_from_file(file=new_file,spk=spkid,receive_path=cfg.RAW_FILE_PATH,save_days=cfg.MINIO[f'test_save_days'])
        except Exception as e:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 2,
                "err_msg": f"File open faild.",
            }
            return response
    elif get_type == "url":
        new_url =request.form.get("wav_url")
        try:
            filepath,oss_path = save_wav_from_url(url=new_url,spk=spkid,receive_path=cfg.RAW_FILE_PATH,save_days=cfg.MINIO[f'test_save_days'])

        except Exception as e:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 3,
                "err_msg": f"File:{new_url} download faild.",
            }
            return response

    try:
        vad_result = vad_and_upsample(wav_file=filepath,spkid=spkid,wav_length=cfg.WAV_LENGTH,device="cpu",savepath=cfg.VAD_FILE_PATH,channel=wav_channel,save_days=cfg.MINIO[f'test_save_days'])
        wait_time = vad_result["wait_time"]
        if wait_time>3:
            wait_time_gt3 = True
        else:
            wait_time_gt3 = False
        if not cfg.VAD_FILE_PATH:
            os.remove(vad_result["save_path"])
        if not cfg.RAW_FILE_PATH:
            os.remove(filepath)
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"VAD and upsample faild. No useful data in {filepath}.",
        }

    response = {
        "code": 2000,
        "status": "success",
        "err_msg": "null",
        "wait_time_gt3":wait_time_gt3
    }
    
    return response

def get_form_data(request_form,cfg,get_type="url",action="test"):
    """_summary_

    Args:
        request_form (form):   request.form:{'spkid': '1', 'wav_url': 'http://www.baidu.com/1.wav', 'wav_channel': 1}
        cfg (_type_): config settings
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
    if action == "test":
        action_type = 1
    elif action == "register":
        action_type = 2
    new_spkid = request_form["spkid"]
    if check_spkid_already_exists(new_spkid):
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 4,
            "err_msg": f"spkid:{new_spkid} already exists"
        }
        err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
        return response
    wav_channel = request_form.get("wav_channel",cfg.WAV_CHANNEL)
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
                "err_msg": "Only support wav or mp3 file."
            }
            add_to_log(phone=new_spkid, action_type=action_type, err_type=response["err_type"], message=response["err_msg"],file_url="",preprocessed_file_path="")
            err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
            return response
        try:
            filepath,oss_path = save_wav_from_file(file=new_file,spk=new_spkid,receive_path=cfg.RAW_FILE_PATH,save_days=cfg.MINIO[f'{action}_save_days'])
        except Exception as e:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 2,
                "err_msg": f"File open faild.",
            }
            add_to_log(phone=new_spkid, action_type=action_type, err_type=response["err_type"], message=response["err_msg"],file_url="",preprocessed_file_path="")
            err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
            return response
    elif get_type == "url":
        new_url =request.form.get("wav_url")
        try:
            filepath,oss_path = save_wav_from_url(url=new_url,spk=new_spkid,receive_path=cfg.RAW_FILE_PATH,save_days=cfg.MINIO[f'{action}_save_days'])
        except Exception as e:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 3,
                "err_msg": f"File:{new_url} download faild.",
            }
            add_to_log(phone=new_spkid, action_type=action_type, err_type=response["err_type"], message=response["err_msg"],file_url="",preprocessed_file_path="")
            err_logger.info(f"{new_spkid},None,{response['err_type']},{response['err_msg']}")
            return response


    # STEP 2: VAD
    start_time = time.time()
    try:
        vad_result = vad_and_upsample(wav_file=filepath,spkid=new_spkid,device=cfg.DEVICE,wav_length=cfg.WAV_LENGTH,savepath=cfg.VAD_FILE_PATH,channel=wav_channel,save_days=cfg.MINIO[f'{action}_save_days'])
        wav = vad_result["wav_torch"]
        after_vad_length = vad_result["after_length"]
        preprocessed_file_path = vad_result["preprocessed_file_path"]
        wait_time = vad_result["wait_time"]
        if wait_time>3:
            wait_time_gt3 = True
        else:
            wait_time_gt3 = False
        if not cfg.VAD_FILE_PATH:
            os.remove(vad_result["save_path"])
        if not cfg.RAW_FILE_PATH:
            os.remove(filepath)
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"VAD and upsample faild. No useful data in {filepath}.",
        }
        add_to_log(phone=new_spkid, action_type=action_type, err_type=5, message=f"vad error",file_url=oss_path,preprocessed_file_path="")
        err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        return response

    # STEP 3: Self Test
    try:
        self_test_result = self_test_and_encode(wav_torch=wav, spkreg = spkreg,similarity=similarity, sr=16000, min_length=cfg.MIN_LENGTH,similarity_limit=cfg.SELF_TEST_TH)
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"Self Test faild. No useful data in {filepath}.",
        }
        add_to_log(phone=new_spkid, action_type=action_type, err_type=5, message=f"self test error",file_url=oss_path,preprocessed_file_path="")
        err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        return response
    msg = self_test_result["msg"]
    if not self_test_result["pass"]:
        
        if "duration" in msg:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 6,
                "err_msg": msg
                }
            add_to_log(phone=new_spkid, action_type=action_type, err_type=2, message=f"{msg}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
            err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        else:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 7,
                "err_msg": msg
                }
            add_to_log(phone=new_spkid, action_type=action_type, err_type=1, message=f"{msg}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
            err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        return response

    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    max_class_score = 0
    max_class_index = 0
    if cfg.pre_classify:
        for index,i in enumerate(torch.eye(192)):
            if cfg.DEVICE == "cuda":
                i = torch.FloatTensor(i).cuda()
            now_class_score = similarity(embedding,i)
            if now_class_score>max_class_score:
                max_class_score=now_class_score
                max_class_index = index
    

    # STEP 5: Test or Register
    if action == "test":
        black_database = get_all_embedding(blackbase=cfg.BLACK_BASE,class_index=-1)
        is_inbase,check_result= test_wav(database=black_database,
                                    embedding=embedding,
                                    spkid=new_spkid,
                                    black_limit=cfg.BLACK_TH,
                                    similarity=similarity,
                                    top_num=10)
        hit_scores=check_result["best_score"]
        blackbase_phone=check_result["spk"]
        top_10=check_result["top_10"]

        add_success,phone_info = add_to_database(
                                        blackbase = cfg.BLACK_BASE,
                                        embedding=embedding,
                                        spkid=new_spkid,
                                        max_class_index=max_class_index,
                                        log_phone_info = cfg.LOG_PHONE_INFO,
                                        mode = "test"
                                        )

        blackbase_id=0                
        if is_inbase:
            hit_info = {
                "name":"none",
                "phone":new_spkid,
                "file_url":oss_path,
                "hit_time":datetime.now(),
                "province":phone_info.get("province",""),
                "city":phone_info.get("city",""),
                "phone_type":phone_info.get("phone_type",""),
                "area_code":phone_info.get("area_code",""),
                "zip_code":phone_info.get("zip_code",""),
                "self_test_score_mean":self_test_result["mean_score"],
                "self_test_score_min":self_test_result["min_score"],
                "self_test_score_max":self_test_result["max_score"],
                "call_begintime":call_begintime,
                "call_endtime":call_endtime,
                "class_number":max_class_index,
                "blackbase_phone":blackbase_phone,
                "blackbase_id":blackbase_id,
                "hit_status":1,
                "hit_scores":hit_scores,
                "top_10":top_10
            }

            
            msg = f"{is_inbase}"
            clip = check_clip(wav=wav,th=cfg.CLIP_TH)
            
            response = {
                "code": 2000,
                "status": "success",
                "inbase":is_inbase,
                "hit_scores":hit_scores,
                "blackbase_phone":blackbase_phone,
                "top_10":top_10,
                "err_msg": "null",
                "wait_time_gt3":wait_time_gt3,
                "clip":clip,
            }
            if clip:
                # 10
                add_to_log(phone=new_spkid, action_type=1, err_type=10, message=f"{msg},clipped,{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
                add_hit_log(hit_info,hit_db,Hit,preprocessed_file_path=preprocessed_file_path,is_grey=True)
            else:
                add_to_log(phone=new_spkid, action_type=1, err_type=0, message=f"{msg},{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
                add_hit_log(hit_info,hit_db,Hit,preprocessed_file_path=preprocessed_file_path,is_grey=False)
            add_speaker_hit(new_spkid)
            end_time = time.time()
            time_used = end_time - start_time
            logger.info(f"Test,{new_spkid},{oss_path},{response['inbase']},{time_used:.2f}")
            return response
        else:
            response = {
                "code": 2000,
                "status": "success",
                "inbase":False,
                "top_10":top_10,
                "err_msg": "null",
                "wait_time_gt3":wait_time_gt3
            }
            add_to_log(phone=new_spkid, action_type=1, err_type=0, message=f"Not in base,{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
            end_time = time.time()
            time_used = end_time - start_time
            logger.info(f"Test,{new_spkid},{oss_path},{response['inbase']},{time_used:.2f}")
            return response

    elif action == "register":
        
        if cfg.AUTO_TEST:
            black_database = get_all_embedding(blackbase=cfg.BLACK_BASE,class_index=-1)
            if len(black_database.keys()) > 1:
                auto_test(new_spkid,embedding,black_database,oss_path,preprocessed_file_path,self_test_result,call_begintime,call_endtime,max_class_index,cfg)
        max_class_index =1

        add_success,phone_info = add_to_database(
                                        blackbase = cfg.BLACK_BASE,
                                        embedding=embedding,
                                        spkid=new_spkid,
                                        max_class_index=1,
                                        log_phone_info = cfg.LOG_PHONE_INFO
                                        )
        if add_success:
            skp_info = {
                "name":"none",
                "phone":new_spkid,
                "uuid":oss_path,
                "hit":0,
                "register_time":datetime.now(),
                "province":phone_info.get("province",""),
                "city":phone_info.get("city",""),
                "phone_type":phone_info.get("phone_type",""),
                "area_code":phone_info.get("area_code",""),
                "zip_code":phone_info.get("zip_code",""),
                "self_test_score_mean":self_test_result["mean_score"],
                "self_test_score_min":self_test_result["min_score"],
                "self_test_score_max":self_test_result["max_score"],
                "call_begintime":call_begintime,
                "call_endtime":call_endtime,
                "max_class_index":max_class_index
            }
            add_speaker(skp_info,speaker_db,Speaker,preprocessed_file_path=preprocessed_file_path)
            add_to_log(phone=new_spkid, action_type=2, err_type=0, message=f"Register success.",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
            
            response = {
                "code": 2000,
                "status": "success",
                "err_type":0,
                "err_msg": "Register success.",
                "wait_time_gt3":wait_time_gt3
            }
            end_time = time.time()
            time_used = end_time - start_time
            logger.info(f"Register,{new_spkid},{oss_path},Success,{time_used:.2f}")
            return response
