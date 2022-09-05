import time
from flask import request
import os
from datetime import datetime
import os
import cfg

from utils.orm import check_url
from utils.orm import check_spkid
from utils.orm import to_log
from utils.log import err_logger
from utils.preprocess import save_url
from utils.preprocess import save_file
from utils.preprocess import vad
from utils.preprocess import resample
from utils.preprocess import encode
from utils.preprocess import classify


def general(request_form,cfg,get_type="url",action_type="test"):
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

    new_spkid = request_form["spkid"]
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
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"VAD and upsample faild. No useful data in {filepath}.",
        }
        to_log(phone=new_spkid, action_type=action_type, err_type=5, message=f"vad error",file_url=oss_path,preprocessed_file_path="")
        err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        return response

    # STEP 3: Self Test
    try:
        self_test_result = encode(wav_torch=vad_result["torch"])
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"Self Test faild. No useful data in {filepath}.",
        }
        to_log(phone=new_spkid, action_type=action_type, err_type=5, message=f"self test error",file_url=oss_path,preprocessed_file_path="")
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
            to_log(phone=new_spkid, action_type=action_type, err_type=2, message=f"{msg}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
            err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        else:
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 7,
                "err_msg": msg
                }
            to_log(phone=new_spkid, action_type=action_type, err_type=1, message=f"{msg}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path)
            err_logger.info(f"{new_spkid},{oss_path},{response['err_type']},{response['err_msg']}")
        return response

    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    class_num = classify(embedding)
    

    # STEP 5: Test or Register
    if action_type == "test":
        
            return response
        else:
            response = {
                "code": 2000,
                "status": "success",
                "inbase":False,
                "top_10":top_10,
                "err_msg": "null",

            }
            to_log(phone=new_spkid, action_type=1, err_type=0, message=f"Not in base,{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
            end_time = time.time()
            time_used = end_time - start_time
            logger.info(f"Test,{new_spkid},{oss_path},{response['inbase']},{time_used:.2f}")
            return response

    elif action_type == "register":
        
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
