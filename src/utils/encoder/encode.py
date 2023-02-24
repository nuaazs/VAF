# coding = utf-8
# @Time    : 2022-09-05  15:02:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: self-test and encode.

import sys
import torch
import numpy as np

# utils
from utils.log import logger
from utils.encoder import spkreg
from utils.encoder import similarity
from utils.preprocess.mydenoiser import denoise_wav
from utils.preprocess.remove_segments import remove


# cfg
import cfg


def encode(wav_torch_raw, action_type="test"):
    # TODO:降噪模块更新
    """Audio quality detection and encoding.

    Args:
        wav_torch_raw (torch 1D): wav data
        action_type (sting): Action type (register or test)

    Returns:
        Dict: Quality inspection results and audio characteristics
    """
    if action_type == "register":
        min_length = cfg.MIN_LENGTH_REGISTER
    elif action_type == "test":
        min_length = cfg.MIN_LENGTH_TEST
    else:
        min_length = cfg.MIN_LENGTH_TEST# sys.maxsize
    sr = cfg.SR
    max_score = 0
    mean_score = 0
    min_score = 1
    raw_wav_length = len(wav_torch_raw) / sr
    if raw_wav_length <= min_length:
        result = {
            "pass": False,
            "msg": f" encode Insufficient duration, the current duration is {len(wav_torch_raw)/sr}s. %d <= %d"%(raw_wav_length, min_length),
            "max_score": 0,
            "mean_score": 0,
            "min_score": 0,
            "err_type": 6,
            "before_score": None,
        }
        return result
    wav_torch = wav_torch_raw.unsqueeze(0)
    embedding = spkreg.encode_batch(wav_torch)
    result = {
        "pass": True,
        "msg": "Qualified.",
        "max_score": max_score,
        "before_score": None,
        "mean_score": mean_score,
        "min_score": min_score,
        "tensor": embedding[0],  # encode_result[x_index][0],
        "err_type": 0,
    }
    return result


def preprocess_denoise(wav):
    return denoise_wav(wav.unsqueeze(0))[0]