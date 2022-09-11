# coding = utf-8
# @Time    : 2022-09-05  15:34:55
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: register.

from datetime import datetime

from utils.orm import to_database
from utils.orm import add_speaker
from utils.orm import to_database
from utils.orm import to_log
from utils.orm import get_embeddings
from utils.orm import to_database

import cfg


def register(embedding,wav,new_spkid,max_class_index,oss_path,self_test_result,
                call_begintime,call_endtime,
                preprocessed_file_path,show_phone,before_vad_length,after_vad_length,
                download_used_time,vad_used_time,
                self_test_used_time,classify_used_time):

    add_success,phone_info = to_database(
                                    embedding=embedding,
                                    spkid=new_spkid,
                                    max_class_index=max_class_index,
                                    log_phone_info = cfg.LOG_PHONE_INFO
                                    )
    if add_success:
        skp_info = {
            "name":"none",
            "phone":new_spkid,
            "uuid":oss_path,
            "hit":0,
            "register_time":(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "province":phone_info.get("province",""),
            "city":phone_info.get("city",""),
            "phone_type":phone_info.get("phone_type",""),
            "area_code":phone_info.get("area_code",""),
            "zip_code":phone_info.get("zip_code",""),
            "self_test_score_mean":float(self_test_result["mean_score"].numpy()),
            "self_test_score_min":float(self_test_result["min_score"].numpy()),
            "self_test_score_max":float(self_test_result["max_score"].numpy()),
            "call_begintime":call_begintime,
            "call_endtime":call_endtime,
            "max_class_index":max_class_index,
            "preprocessed_file_path":preprocessed_file_path,
            "show_phone":show_phone
        }
        add_speaker(skp_info,after_vad_length=after_vad_length)
        to_log(phone=new_spkid, action_type=2, err_type=0, message=f"Register success.",file_url=oss_path,\
                preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length,show_phone=show_phone)
        
        response = {
            "code": 2000,
            "status": "success",
            "err_type":0,
            "err_msg": "Register success.",
            "name":"none",
            "phone":new_spkid,
            "uuid":oss_path,
            "hit":0,
            "register_time":(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "province":phone_info.get("province",""),
            "city":phone_info.get("city",""),
            "phone_type":phone_info.get("phone_type",""),
            "area_code":phone_info.get("area_code",""),
            "zip_code":phone_info.get("zip_code",""),
            "self_test_score_mean":float(self_test_result["mean_score"].numpy()),
            "self_test_score_min":float(self_test_result["min_score"].numpy()),
            "self_test_score_max":float(self_test_result["max_score"].numpy()),
            "call_begintime":call_begintime,
            "call_endtime":call_endtime,
            "max_class_index":max_class_index,
            "preprocessed_file_path":preprocessed_file_path,
            "show_phone":show_phone,
            "before_vad_length":before_vad_length,
            "after_vad_length":after_vad_length,
            "download_used_time" : download_used_time,
            "vad_used_time" :vad_used_time,
            "self_test_used_time":self_test_used_time,
            "classify_used_time":classify_used_time

        }
        print(response)
        return response
