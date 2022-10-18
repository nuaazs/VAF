
import datetime
from flask import request

# utils

from utils.preprocess import save_url
from utils.preprocess import save_file
from utils.preprocess import vad
from utils.preprocess import resample
from utils.encoder import encode
from utils.preprocess import classify

import torch

# cfg
import cfg


def preprocess(request_form,get_type="url",action_type="register"):
    new_spkid = request_form["spkid"]
    # STEP 1: Get wav file.
    if get_type == "file":
        new_file = request.files["wav_file"]
        filename = new_file.filename
        try:
            filepath, oss_path = save_file(file=new_file, spk=new_spkid)
        except Exception as e:
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 2,
                "err_msg": f"Form file save error.\nFile save faild.",
            }
            return response

    elif get_type == "url":
        new_url = request.form.get("wav_url")
        try:
            filepath, oss_path = save_url(url=new_url, spk=new_spkid)
        except Exception as e:
            print(e)
            response = {
                "code": 2000,
                "status": "error",
                "err_type": 3,
                "err_msg": f"URL file save error.\nDownload {new_url} faild.",
            }
            return response
    

    # VAD
    try:
        wav = resample(wav_filepath=filepath, action_type=action_type)
        vad_result = vad(wav=wav, spkid=new_spkid, action_type=action_type)
        if cfg.SAVE_PREPROCESSED_OSS:
            preprocessed_file_path = vad_result["preprocessed_file_path"]
        else:
            preprocessed_file_path = ""
    except Exception as e:
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"VAD and upsample error.\nNo useful data in {filepath}.",
        }
        return response

    # STEP 3: Self Test
    try:
        self_test_result = encode(
            wav_torch_raw=vad_result["wav_torch"], action_type=action_type
        )
    except Exception as e:
        print(e)
        response = {
            "code": 2000,
            "status": "error",
            "err_type": 5,
            "err_msg": f"Self Test faild.\nNo useful data in {filepath}.",
        }
        return response



    msg = self_test_result["msg"]
    if not self_test_result["pass"]:
        err_type = self_test_result["err_type"]
        response = {
            "code": 2000,
            "status": "error",
            "err_type": err_type,
            "err_msg": msg,
        }
        return response

    # STEP 4: Encoding
    embedding = self_test_result["tensor"]
    if cfg.CLASSIFY:
        class_num = classify(embedding)
    else:
        class_num = 999


    result  = {
        "code": 2000,
        "status": "success",
         # "wav_torch":vad_result["wav_torch"].detach().cpu().numpy().tolist(),
        "embedding": embedding.detach().cpu().numpy().tolist(),
        "class_num": class_num,
    }
    return result