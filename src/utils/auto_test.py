# @Time    : 2022-07-27  19:04:10
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/download_and_preprocess.py
# @Describe: Main function.

import time
from flask import request
import torch
import numpy as np
import os
from datetime import datetime
import os

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


def auto_test(new_spkid,embedding,black_database,oss_path,preprocessed_file_path,self_test_result,call_begintime,call_endtime,max_class_index,cfg):
    predict_right,status,pre_test_msg,check_result= self_check(database=black_database,
                                            embedding=embedding,
                                            spkid=new_spkid,
                                            black_limit=cfg.BLACK_TH,
                                            similarity=similarity,
                                            top_num=10)
    hit_scores=check_result["best_score"]
    blackbase_phone=check_result["spk"]
    # blackbase_id=check_result["blackbase_id"]
    blackbase_id=0
                
    add_to_log(phone=new_spkid, action_type=3, err_type=status, message=f"{pre_test_msg}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
    if 1<=status<=3:
        add_speaker_hit(new_spkid)
        add_to_log(phone=new_spkid, action_type=4, err_type=0, message=f"",file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
        # TODO hit log
        phone_info ={}
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
            "top_10":"",
        }

        add_hit_log(hit_info,hit_db,Hit,preprocessed_file_path=preprocessed_file_path)
    if predict_right:
        logger.info(f"\t# Pre-test pass √")
        logger.info(f"\t# Pre-test msg:{pre_test_msg}")

    else:
        logger.info(f"\t# Pre-test error !")
        logger.info(f"\t# Pre-test msg:{pre_test_msg}")