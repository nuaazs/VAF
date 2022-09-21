# coding = utf-8
# @Time    : 2022-09-05  15:36:03
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: test.

import datetime
from utils.orm.query import add_hit_count

from utils.orm import to_database
from utils.orm import to_log
from utils.orm import add_hit
from utils.orm import get_embeddings
from utils.test import test_wav
from utils.encoder import similarity
from utils.orm import to_database
from utils.preprocess import check_clip
from utils.orm import get_blackid

import cfg

def test(embedding,wav,new_spkid,max_class_index,oss_path,self_test_result,
            call_begintime,call_endtime,preprocessed_file_path,
            show_phone,before_vad_length,after_vad_length,used_time):
    start = datetime.datetime.now()

    black_database = get_embeddings(class_index=max_class_index)
    used_time["embedding_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()

    is_inbase,check_result= test_wav(database=black_database,
                                embedding=embedding,
                                spkid=new_spkid,
                                black_limit=cfg.BLACK_TH,
                                similarity=similarity,
                                top_num=10)

    hit_scores=check_result["best_score"]
    blackbase_phone=check_result["spk"]
    top_10=check_result["top_10"]
    used_time["test_used_time"] = (datetime.datetime.now() - start).total_seconds()
    start = datetime.datetime.now()
    add_success,phone_info = to_database(
                                    embedding=embedding,
                                    spkid=new_spkid,
                                    max_class_index=max_class_index,
                                    log_phone_info = cfg.LOG_PHONE_INFO,
                                    mode = "test"
                                    )
    
    try:
        blackbase_id=get_blackid(blackbase_phone.split(",")[0])
    except Exception as e:
        print(e)
        blackbase_id = 0
    if is_inbase:
        hit_info = {
            "name":"none",
            "show_phone":show_phone,
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
            "preprocessed_file_path":preprocessed_file_path,
            "blackbase_phone":blackbase_phone,
            "blackbase_id":blackbase_id,
            "hit_status":1,
            "hit_scores":hit_scores,
            "top_10":top_10
        }
        
        
        msg = f"{is_inbase}"
        if cfg.CLIP_DETECT:
            clip = check_clip(wav=wav,th=cfg.CLIP_TH)
        else:
            clip = False
        used_time["to_database_used_time"] = (datetime.datetime.now() - start).total_seconds()
        start = datetime.datetime.now()
        response = {
            "code": 2000,
            "status": "success",
            "inbase":is_inbase,
            "hit_scores":hit_scores,
            "blackbase_phone":blackbase_phone,
            "top_10":top_10,
            "err_msg": "null",
            "clip":clip,
            "before_vad_length":before_vad_length,
            "after_vad_length":after_vad_length,
            "self_test_score_mean":float(self_test_result["mean_score"].numpy()),
            "self_test_score_min":float(self_test_result["min_score"].numpy()),
            "self_test_score_max":float(self_test_result["max_score"].numpy()),
            "self_test_before_score":self_test_result["before_score"],
            "used_time":used_time
        }
        if clip:
            to_log(phone=new_spkid, action_type=1, err_type=10, message=f"{msg},clipped,{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length,show_phone=show_phone)
            add_hit(hit_info,is_grey=True,after_vad_length=after_vad_length)
        else:
            to_log(phone=new_spkid, action_type=1, err_type=0, message=f"{msg},{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length,show_phone=show_phone)
            add_hit(hit_info,is_grey=False,after_vad_length=after_vad_length)
        add_hit_count(new_spkid)

        

        return response
    else:
        used_time["to_database_used_time"] = (datetime.datetime.now() - start).total_seconds()
        start = datetime.datetime.now()
        response = {
            "code": 2000,
            "status": "success",
            "inbase":is_inbase,
            "err_msg": "null",
            "before_vad_length":before_vad_length,
            "after_vad_length":after_vad_length,
            "hit_scores":hit_scores,
            "blackbase_phone":blackbase_phone,
            "top_10":top_10,
            "self_test_score_mean":float(self_test_result["mean_score"].detach().cpu().numpy()),
            "self_test_score_min":float(self_test_result["min_score"].detach().cpu().numpy()),
            "self_test_score_max":float(self_test_result["max_score"].detach().cpu().numpy()),
            "self_test_before_score":self_test_result["before_score"],
            "used_time":used_time
        }

        
        return response