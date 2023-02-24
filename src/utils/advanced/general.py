# coding = utf-8
# @Time    : 2022-09-05  09:47:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Register and identify interfaces.
from flask import request

# utils
from utils.orm import check_spkid
from utils.log import logger
from utils.preprocess import save_url
from utils.preprocess import save_file
from utils.preprocess import vad
from utils.preprocess import resample
from utils.encoder import encode
from utils.preprocess import classify
from utils.register import register
from utils.test import test
from utils.info import OutInfo
from utils.preprocess.mydenoiser import denoise_file, denoise_wav
from utils.preprocess import remove_fold_and_file

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

    new_spkid = request_form["spkid"]
    call_begintime = request_form.get("call_begintime", "1999-02-18 10:10:10")
    call_endtime = request_form.get("call_endtime", "1999-02-18 10:10:10")
    show_phone = request_form.get("show_phone", new_spkid)
    pool = request_form.get("pool", False)
    channel = int(request_form.get("wav_channel", cfg.WAV_CHANNEL))
    logger.info(f"# ID: {new_spkid} ShowPhone: {show_phone}. ")
    logger.info(f"# Pool: {pool} Channel: {channel}. ")

    if action_type == "register":
        action_num = 2
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
            return outinfo.response_error(spkid=new_spkid, err_type=4, message=message)

    # STEP 1: Get wav file.
    if file_mode == "file":
        logger.info(f"\t\t Downloading ...")
        new_file = request.files["wav_file"]
        if (new_file.filename.split('.')[-1] not in ["blob", "wav", "weba", "webm", "mp3", "flac", "m4a", "ogg", "opus",
                                                     "spx", "amr", "mp4", "aac", "wma", "m4r", "3gp", "3g2", "caf",
                                                     "aiff", "aif", "aifc", "au", "sd2", "bwf", "rf64"]):
            message = f"File type error."
            return outinfo.response_error(spkid=new_spkid, err_type=1, message=message)
        try:
            if "blob" in new_file.filename:
                new_file.filename = "test.webm"
            filepath, outinfo.oss_path = save_file(file=new_file, spk=new_spkid)
            logger.info(f"\t\t Download success. Filepath: {filepath}")
        except Exception as e:
            remove_fold_and_file(new_spkid)
            return outinfo.response_error(spkid=new_spkid, err_type=2, message=str(e))
    elif file_mode == "url":
        new_url = request_form.get("wav_url")
        logger.info(f"\t\t Downloading from URL:{new_url} ...")
        try:
            filepath, outinfo.oss_path = save_url(url=new_url, spk=new_spkid)
        except Exception as e:
            remove_fold_and_file(new_spkid)
            return outinfo.response_error(spkid=new_spkid, err_type=3, message=str(e))
    outinfo.log_time(name="download_used_time")
    logger.info(f"\t\t Download success. Filepath: {filepath}")

    # try:
    logger.info(f"\t\t Resampling wav data ... ")
    wav = resample(wav_filepath=filepath, action_type=action_type, channel=channel)
    # todo
    outinfo.wav = wav
    logger.info(f"\t\t Resampling Success! ")
    logger.info(f"\t\t Doing VAD ... ")
    vad_result = vad(wav=wav, spkid=new_spkid, action_type=action_type)
    outinfo.after_length = vad_result["after_length"]
    outinfo.before_length = vad_result["before_length"]
    logger.info(f"\t\t VAD Success! Before: {vad_result['before_length']}, After: {vad_result['after_length']}")
    if cfg.SAVE_PREPROCESSED_OSS:
        outinfo.preprocessed_file_path = vad_result["preprocessed_file_path"]
        logger.info(f"\t\t Preprocessed file saved to OSS: {outinfo.preprocessed_file_path}")
    else:
        outinfo.preprocessed_file_path = ""
    # except Exception as e:
    #     remove_fold_and_file(new_spkid)
    #     return outinfo.response_error(spkid=new_spkid, err_type=5, message=str(e))
    outinfo.log_time(name="vad_used_time")

    # STEP 3: Encoding
    embedding = encode(wav_torch_raw=vad_result["wav_torch"], action_type=action_type)["tensor"]
    if cfg.CLASSIFY:
        logger.info(f"\t\t Classifying ... ")
        class_num = classify(embedding)
        logger.info(f"\t\t Classify Success ! ")
    else:
        class_num = 999
    outinfo.class_num = class_num
    outinfo.embedding = embedding
    outinfo.log_time(name="classify_used_time")

    # STEP 4: Test or Register
    if action_num == 1:
        if pool:
            logger.info(f"\t\t Pooling ... ")
            test_info = test(outinfo, pool)
            register_info = register(outinfo, pool)
            logger.info(f"\t\t Pooling Success ")
            remove_fold_and_file(new_spkid)
            return test_info
        else:
            logger.info(f"\t\t Testing ... ")
            remove_fold_and_file(new_spkid)
            return test(outinfo)

    elif action_num == 2:
        logger.info(f"\t\t Registering ... ")
        remove_fold_and_file(new_spkid)
        return register(outinfo)
