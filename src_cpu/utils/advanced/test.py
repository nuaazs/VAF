from utils.orm import get_embeddings
from utils.orm import to_database
from utils.orm import add_hit
from utils.orm import to_log
from utils.orm import add_hit
from utils.encoder import similarity
from utils.preprocess import check_clip


import cfg

def test(embedding,wav,new_spkid,max_class_index):
    black_database = get_embeddings(blackbase=cfg.BLACK_BASE,class_index=-1)
    is_inbase,check_result= test_wav(database=black_database,
                                embedding=embedding,
                                spkid=new_spkid,
                                black_limit=cfg.BLACK_TH,
                                similarity=similarity,
                                top_num=10)
    hit_scores=check_result["best_score"]
    blackbase_phone=check_result["spk"]
    top_10=check_result["top_10"]

    add_success,phone_info = to_database(
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
            "clip":clip,
        }
        if clip:
            # 10
            to_log(phone=new_spkid, action_type=1, err_type=10, message=f"{msg},clipped,{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
            add_hit(hit_info,hit_db,Hit,preprocessed_file_path=preprocessed_file_path,is_grey=True)
        else:
            to_log(phone=new_spkid, action_type=1, err_type=0, message=f"{msg},{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
            to_log(phone=new_spkid, action_type=1, err_type=0, message=f"{msg},{blackbase_phone},{hit_scores}",file_url=oss_path,preprocessed_file_path=preprocessed_file_path,valid_length=after_vad_length)
            add_hit(hit_info,hit_db,Hit,preprocessed_file_path=preprocessed_file_path,is_grey=False)
        add_hit(new_spkid)

        logger.info(f"Test,{new_spkid},{oss_path},{response['inbase']},{time_used:.2f}")