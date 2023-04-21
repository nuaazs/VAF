# coding = utf-8
# @Time    : 2022-09-05  09:47:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Register and identify interfaces.
import os
import torchaudio
from flask import request

# utils
from utils.orm import check_spkid
from utils.log import logger
from utils.preprocess import save_url
from utils.preprocess import save_file
from utils.preprocess import vad
from utils.preprocess import read_wav_data,resample
from utils.encoder import encode
from utils.register import register
from utils.test import test
from utils.info import OutInfo
from utils.preprocess import remove_fold_and_file
from utils.cmd import run_cmd
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
            # 1. spkid repeat
            # 2. The file format is incorrect       
            # 3. File parsing error 
            # 4. File download error
            # 5. The file has no valid data (very poor quality)  
            # 6. The valid duration of the file does not meet the requirements
            # 7. The file quality detection does not meet the requirements 
            #    (the environment is noisy or there are multiple speakers)
    """

    new_spkid = request_form["spkid"]
    call_begintime = request_form.get("call_begintime", "1999-02-18 10:10:10")
    call_endtime = request_form.get("call_endtime", "1999-02-18 10:10:10")
    show_phone = request_form.get("show_phone", new_spkid)
    channel = int(request_form.get("wav_channel", cfg.WAV_CHANNEL))
    logger.info(f"# ID: {new_spkid} ShowPhone: {show_phone}. ")

    if action_type == "register":
        action_num = 2
        register_date = request_form.get("register_date", '20200101')
    if action_type == "test":
        action_num = 1

    outinfo = OutInfo(action_num)
    outinfo.spkid = new_spkid
    outinfo.call_begintime = call_begintime
    outinfo.call_endtime = call_endtime
    outinfo.show_phone = show_phone

    if cfg.CHECK_DUPLICATE:
        if check_spkid(new_spkid) and action_type == "register":
            message = f"ID: {new_spkid} already exists. Deny registration."
            return outinfo.response_error(spkid=new_spkid, err_type=1, message=message)

    # STEP 1: Get wav file.
    if file_mode == "file":
        logger.info(f"\t\t Downloading ...")
        new_file = request.files["wav_file"]
        if (new_file.filename.split('.')[-1] not in ["blob", "wav", "weba", "webm", "mp3", "flac", "m4a", "ogg", "opus",
                                                     "spx", "amr", "mp4", "aac", "wma", "m4r", "3gp", "3g2", "caf",
                                                     "aiff", "aif", "aifc", "au", "sd2", "bwf", "rf64"]):
            message = f"File type error. Only support wav, weba, webm, mp3, flac, m4a, ogg, opus, spx, amr, \
                mp4, aac, wma, m4r, 3gp, 3g2, caf, aiff, aif, aifc, au, sd2, bwf, rf64."
            return outinfo.response_error(spkid=new_spkid, err_type=2, message=message)
        try:
            if "blob" in new_file.filename:
                new_file.filename = "test.webm"
            filepath, outinfo.oss_path = save_file(file=new_file, spk=new_spkid,channel=channel)
            logger.info(f"\t\t Download success. Filepath: {filepath}")
        except Exception as e:
            remove_fold_and_file(new_spkid)
            return outinfo.response_error(spkid=new_spkid, err_type=3, message=str(e))
    elif file_mode == "url":
        new_url = request_form.get("wav_url")
        logger.info(f"\t\t Downloading from URL:{new_url} ...")
        try:
            filepath, outinfo.oss_path = save_url(url=new_url, spk=new_spkid,channel=channel)
        except Exception as e:
            remove_fold_and_file(new_spkid)
            return outinfo.response_error(spkid=new_spkid, err_type=4, message=str(e))
    #=========================LOG TIME=========================
    outinfo.log_time(name="download_used_time")
    logger.info(f"\t\t Download success. Filepath: {filepath}")
    outinfo.wav = read_wav_data(wav_filepath=filepath)
    # STEP 2: VAD
    logger.info(f"\t\t Doing VAD ... ")
    vad_result = vad(wav=outinfo.wav, spkid=new_spkid, action_type=action_type)
    outinfo.after_length = vad_result["after_length"]
    outinfo.before_length = vad_result["before_length"]
    outinfo.wav_vad = vad_result["wav_torch"]
    outinfo.preprocessed_file_path = vad_result["preprocessed_file_path"]
    logger.info(f"\t\t VAD Success! Before: {vad_result['before_length']}, After: {vad_result['after_length']}")
    #=========================LOG TIME=========================
    outinfo.log_time(name="vad_used_time")
    vad_result["wav_torch"] = resample(vad_result["wav_torch"],cfg.SR,cfg.ECAPA_SR)
    #=========================LOG TIME=========================
    outinfo.log_time(name="resample_16k")
    # STEP 3: Encoding
    encode_result = encode(wav_torch_raw=vad_result["wav_torch"], action_type=action_type)
    #=========================LOG TIME=========================
    outinfo.log_time(name="encode_time")
    if encode_result["pass"]:
        embedding = encode_result["tensor"]
    else:
        remove_fold_and_file(new_spkid)
        return outinfo.response_error(spkid=new_spkid, err_type=encode_result["err_type"],
                                      message=encode_result["msg"])
    
    outinfo.embedding = embedding

    # STEP 4: Test or Register
    
    if action_num == 1:
        logger.info(f"\t\t Testing ... ")
        outinfo.class_num = 999
        return test(outinfo)
    elif action_num == 2:
        logger.info(f"\t\t Registering ... ")
        outinfo.class_num = register_date
        remove_fold_and_file(new_spkid)
        return register(outinfo)