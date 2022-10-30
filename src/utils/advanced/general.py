# coding = utf-8
# @Time    : 2022-09-05  09:47:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Register and identify interfaces.

import torch
import datetime
from flask import request
from transformers import Wav2Vec2ConformerForAudioFrameClassification, Wav2Vec2ConformerForCTC

# utils
from utils.orm.database import get_embedding
from utils.orm import check_spkid
from utils.orm import get_spkinfo
from utils.orm import delete_spk
from utils.orm import to_log
from utils.orm.db_utils import mysql_handler
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
from utils.encoder import similarity
from utils.info import OutInfo

# cfg
import cfg

def general(request_form, file_mode="url", action_type="test"):
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
    outinfo = OutInfo(action_type)
    new_spkid = request_form["spkid"]
    call_begintime = request_form.get("call_begintime", "1999-02-18 10:10:10")
    call_endtime = request_form.get("call_endtime", "1999-02-18 10:10:10")
    show_phone = request_form.get("show_phone", new_spkid)
    outinfo.spkid=new_spkid
    outinfo.call_begintime = call_begintime
    outinfo.call_endtime = call_endtime
    outinfo.show_phone = show_phone

    logger.info(f"# {new_spkid}")
    if action_type == "register":
        action_num = 2
    if action_type == "test":
        action_num = 1

    # STEP 0: ID duplication detection
    # If the ID is repeated, first determine whether it has reached the specified time interval
    # if so, delete the original ID and re-register (update the voiceprint information)
    # If the specified time interval is not reached, an error message is returned directly
    do_update = False
    if check_spkid(new_spkid) and action_type == "register":
        old_info = get_spkinfo(new_spkid)
        last_days = int((datetime.datetime.now() - old_info["register_time"]).days)
        if last_days < cfg.UPDATE_DAYS:
            message = f"ID: {new_spkid} already exists, please change the ID or wait {cfg.UPDATE_DAYS - last_days} days to update."
            return outinfo.response_error(spkid=new_spkid, err_type=4, message=message)
        else:
            do_update = True
            logger.info(f"\tID:{new_spkid}, the audio has timed out and will be updated.")




    # STEP 1: Get wav file.
    if file_mode == "file":
        new_file = request.files["wav_file"]
        if (".wav" not in new_file.filename):
            message = f"File type error."
            return outinfo.response_error(spkid=new_spkid, err_type=1, message=message)
        try:
            filepath, outinfo.oss_path = save_file(file=new_file, spk=new_spkid)
        except Exception as e:
            return outinfo.response_error(spkid=new_spkid, err_type=2, message=e)
    elif file_mode == "url":
        new_url = request.form.get("wav_url")
        try:
            filepath, outinfo.oss_path = save_url(url=new_url, spk=new_spkid)
        except Exception as e:
            return outinfo.response_error(spkid=new_spkid, err_type=3, message=e)
    outinfo.log_time(name="download_used_time")




    # STEP 2: VAD
    try:
        wav = resample(wav_filepath=filepath, action_type=action_type)
        outinfo.wav = wav
        vad_result = vad(wav=wav, spkid=new_spkid, action_type=action_type)
        outinfo.after_length = vad_result["after_length"]
        outinfo.before_length = vad_result["before_length"]
        if cfg.SAVE_PREPROCESSED_OSS:
            outinfo.preprocessed_file_path = vad_result["preprocessed_file_path"]
        else:
            outinfo.preprocessed_file_path = ""
    except Exception as e:
        return outinfo.response_error(spkid=new_spkid, err_type=4, message=e)
    outinfo.log_time(name="vad_used_time")




    # STEP 3: Self Test
    try:
        self_test_result = encode(wav_torch_raw=vad_result["wav_torch"], action_type=action_type)
        outinfo.self_test_result = self_test_result
    except Exception as e:
        return outinfo.response_error(spkid=new_spkid, err_type=5, message=e)
    outinfo.log_time(name="self_test_used_time")
    msg = self_test_result["msg"]
    if not self_test_result["pass"]:
        return outinfo.response_error(spkid=new_spkid, err_type=self_test_result["err_type"], message=str(msg))




    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    if cfg.CLASSIFY:
        class_num = classify(embedding)
    else:
        class_num = 999
    outinfo.class_num = class_num
    outinfo.embedding = embedding
    outinfo.log_time(name="classify_used_time")




    # STEP 5: Updage encoding
    if do_update:
        old_class = old_info["class_number"]
        old_score = old_info["self_test_score_mean"]
        old_valid_length = old_info["valid_length"]
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
        else:
            return outinfo.response_error(spkid=new_spkid, err_type=8)



    # STEP 5: Test or Register
    if action_num == 1:
        return test(outinfo)

    elif action_num == 2:
        return register(outinfo)
