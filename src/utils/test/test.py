# coding = utf-8
# @Time    : 2022-09-05  15:36:03
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: test.

import datetime
import time

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
from utils.asr import get_asr_content
import cfg

black_database = None


def test(outinfo, pool=False):
    """Audio reasoning, compare the audio features with the black library in full, and return the result.

    Args:
        embedding (tensor): audio features
        wav (tensor): audio data
        new_spkid (string): speaker ID
        max_class_index (int): pre-classify result
        oss_path (string): The file url on OSS
        self_test_result (dict): self-test results
        call_begintime (string): call start time
        call_endtime (string): call end time
        preprocessed_file_path (string): Preprocessed file address
        show_phone (string): Displayed phone number
        before_vad_length (float): Audio duration after VAD
        after_vad_length (float): Audio duration before VAD
        used_time (dict): Time spent on each module

    Returns:
        dict: inference result.
    """
    global black_database
    if black_database is None:
        black_database = get_embeddings(class_index=outinfo.class_num)
    outinfo.log_time("get_embeddings")
    is_inbase, check_result = test_wav(
        database=black_database,
        embedding=outinfo.embedding,
        spkid=outinfo.spkid,
        black_limit=cfg.BLACK_TH,
        similarity=similarity,
        top_num=10,
        pool=pool,
    )
    if pool:
        pool_info = check_result["pool_info"]
        print("pool_info", pool_info)
        return check_result

    hit_scores = check_result["best_score"]
    blackbase_phone = check_result["spk"]
    top_10 = check_result["top_10"]
    outinfo.log_time("test_used_time")

    add_success, phone_info = to_database(
        embedding=outinfo.embedding,
        spkid=outinfo.spkid,
        max_class_index=outinfo.class_num,
        log_phone_info=cfg.LOG_PHONE_INFO,
        mode="test",
    )
    if is_inbase:
        try:
            blackbase_id = get_blackid(blackbase_phone.split(",")[0])
        except Exception as e:
            print(e)
            blackbase_id = 0
        # todo
        # get asr content
        # asr_content,hit_keyword,keyword = get_asr_content(outinfo.preprocessed_file_path,outinfo.spkid)
        asr_content, hit_keyword, keyword = "", "", ""
        hit_info = {
            "name": "none",
            "show_phone": outinfo.show_phone,
            "phone": outinfo.spkid,
            "file_url": outinfo.oss_path,
            "hit_time": datetime.datetime.now(),
            "province": phone_info.get("province", ""),
            "city": phone_info.get("city", ""),
            "phone_type": phone_info.get("phone_type", ""),
            "area_code": phone_info.get("area_code", ""),
            "zip_code": phone_info.get("zip_code", ""),
            "call_begintime": outinfo.call_begintime,
            "call_endtime": outinfo.call_endtime,
            "class_number": outinfo.class_num,
            "preprocessed_file_path": outinfo.preprocessed_file_path,
            "blackbase_phone": blackbase_phone,
            "blackbase_id": blackbase_id,
            "hit_status": 1,
            "hit_scores": hit_scores,
            "top_10": top_10,
            "content_text": asr_content,
            "hit_keyword": hit_keyword,
            "keyword": keyword,

        }

        msg = f"{is_inbase}"
        # if cfg.CLIP_DETECT:
        #     clip = check_clip(wav=outinfo.wav, th=cfg.CLIP_TH)
        # else:
        clip = False
        outinfo.log_time("to_database_used_time")
        response = {
            "code": 2000,
            "status": "success",
            "inbase": is_inbase,
            "hit_scores": hit_scores,
            "blackbase_phone": blackbase_phone,
            "top_10": top_10,
            "err_msg": "null",
            "clip": clip,
            "before_vad_length": outinfo.before_length,
            "after_vad_length": outinfo.after_length,
            "self_test_before_score": 1,
            "used_time": outinfo.used_time,
        }
        if clip:
            to_log(
                phone=outinfo.spkid,
                action_type=1,
                err_type=10,
                message=f"{msg},clipped,{blackbase_phone},{hit_scores}",
                file_url=outinfo.oss_path,
                preprocessed_file_path=outinfo.preprocessed_file_path,
                valid_length=outinfo.after_length,
                show_phone=outinfo.show_phone,
                before_length=outinfo.before_length,
                after_length=outinfo.after_length
            )
            add_hit(hit_info, is_grey=True, after_vad_length=outinfo.after_length)
        else:
            to_log(
                phone=outinfo.spkid,
                action_type=1,
                err_type=0,
                message=f"{msg},{blackbase_phone},{hit_scores}",
                file_url=outinfo.oss_path,
                preprocessed_file_path=outinfo.preprocessed_file_path,
                valid_length=outinfo.after_length,
                show_phone=outinfo.show_phone,
                before_length=outinfo.before_length,
                after_length=outinfo.after_length
            )
            add_hit(hit_info, is_grey=False, after_vad_length=outinfo.after_length)
        add_hit_count(blackbase_phone)

        return response
    else:
        outinfo.log_time("to_database_used_time")

        response = {
            "code": 2000,
            "status": "success",
            "inbase": is_inbase,
            "err_msg": "null",
            "before_vad_length": outinfo.before_length,
            "after_vad_length": outinfo.after_length,
            "hit_scores": hit_scores,
            "blackbase_phone": blackbase_phone,
            "top_10": top_10,
            "used_time": outinfo.used_time,
        }
        to_log(
            phone=outinfo.spkid,
            action_type=1,
            err_type=99,
            message=f"False, Not in base, {blackbase_phone},{hit_scores}",
            file_url=outinfo.oss_path,
            preprocessed_file_path=outinfo.preprocessed_file_path,
            valid_length=outinfo.after_length,
            show_phone=outinfo.show_phone,
            before_length=outinfo.before_length,
            after_length=outinfo.after_length
        )
        return response
