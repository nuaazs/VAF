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


def encode(wav_torch_raw, action_type):
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
        min_length = sys.maxsize
    similarity_limit = cfg.SELF_TEST_TH
    sr = cfg.SR
    max_score = 0
    mean_score = 0
    min_score = 1
    raw_wav_length = len(wav_torch_raw) / sr

    if raw_wav_length <= min_length:
        result = {
            "pass": False,
            "msg": f"Insufficient duration, the current duration is {len(wav_torch_raw)/sr}s.",
            "max_score": 0,
            "mean_score": 0,
            "min_score": 0,
            "err_type": 6,
            "before_score": None,
        }
        return result
    segments_number = int(raw_wav_length)
    wav_torch = wav_torch_raw.unsqueeze(0)

    # full_wavs = []  # wav_torch
    # segments = []
    # start = 0
    # while start + cfg.SELF_TEST_SL * cfg.SR < len(wav_torch_raw):
    #     full_wavs.append(remove(wav_torch, start, start + cfg.SELF_TEST_SL * cfg.SR))
    #     segments.append(wav_torch[:, start : start + cfg.SELF_TEST_SL * cfg.SR])
    #     start = start + cfg.SELF_TEST_SS * cfg.SR

    # batch = torch.cat(full_wavs, dim=0)
    # segs_batch = torch.cat(segments, dim=0)
    # encode_result = spkreg.encode_batch(batch)
    # segs_encode_result = spkreg.encode_batch(segs_batch)

    # result_len = len(segs_batch)

    # # seg_scores = []
    # # for x_index in range(result_len):
    # #     socres = []
    # #     for y_index in range(result_len):
    # #         if y_index == x_index:
    # #             continue
    # #         socres.append(similarity(segs_batch[x_index][0], segs_batch[y_index][0]))
    # #     max_score, mean_score, min_score = (
    # #         np.max(socres),
    # #         np.mean(socres),
    # #         np.min(socres),
    # #     )
    # #     seg_scores.append([max_score, mean_score, min_score, x_index])
    # # seg_scores = sorted(seg_scores, key=lambda x: x[2])  # sort by min_score
    # # del_index = seg_scores[0][3]

    # # wav_torch = full_wavs[del_index]
    # wav_torch = wav_torch.unsqueeze(0)

    # socres = []
    # for y_index in range(result_len):
    #     if y_index == del_index:
    #         continue
    #     socres.append(similarity(batch[del_index][0], batch[y_index][0]))

    wav_length = int((wav_torch.shape[1] - 10) / 2)
    left = torch.cat((wav_torch[:, :wav_length], wav_torch[:, :wav_length]), dim=1)
    right = torch.cat(
        (
            wav_torch[:, wav_length : wav_length * 2],
            wav_torch[:, wav_length : wav_length * 2],
        ),
        dim=1,
    )
    wav_torch = wav_torch[:, : left.shape[1]]
    batch = torch.cat((wav_torch, left, right), dim=0)
    embedding = spkreg.encode_batch(batch)
    encoding_tensor = embedding[0]
    encoding_tiny_1 = embedding[1][0]
    encoding_tiny_2 = embedding[2][0]
    score = similarity(encoding_tiny_1, encoding_tiny_2)
    max_score, mean_score, min_score = score, score, score

    # max_score, mean_score, min_score = np.max(socres), np.mean(socres), np.min(socres)

    if mean_score > similarity_limit:
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
    else:
        result = do_denoise(wav_torch_raw, mean_score)
        result = {
            "pass": False,
            "msg": f"Bad quality score:{min_score}.",
            "max_score": max_score,
            "mean_score": mean_score,
            "min_score": min_score,
            "err_type": 7,
        }
    return result


def do_denoise(wav, before_score):
    """ Noise reduction for audio

    Args:
        wav (tensor): Audio data
        before_score (tensor): score brefore denoise

    Returns:
        dict: encode result
    """
    similarity_limit = cfg.SELF_TEST_TH
    max_score = 0
    mean_score = 0
    min_score = 1
    wav_torch = denoise_wav(wav.unsqueeze(0))
    wav_length = int((wav_torch.shape[1] - 10) / 2)
    left = torch.cat((wav_torch[:, :wav_length], wav_torch[:, :wav_length]), dim=1)
    right = torch.cat(
        (
            wav_torch[:, wav_length : wav_length * 2],
            wav_torch[:, wav_length : wav_length * 2],
        ),
        dim=1,
    )
    wav_torch = wav_torch[:, : left.shape[1]]
    batch = torch.cat((wav_torch, left, right), dim=0)
    embedding = spkreg.encode_batch(batch)
    encoding_tensor = embedding[0]
    encoding_tiny_1 = embedding[1][0]
    encoding_tiny_2 = embedding[2][0]
    score = similarity(encoding_tiny_1, encoding_tiny_2)
    max_score, mean_score, min_score = score, score, score
    if score < similarity_limit:
        result = {
            "pass": False,
            "msg": f"Bad quality score:{min_score}.",
            "before_score": float(before_score.detach().cpu().numpy()),
            "max_score": max_score,
            "mean_score": mean_score,
            "min_score": min_score,
            "err_type": 7,
        }
        return result
    result = {
        "pass": True,
        "msg": "Qualified.",
        "max_score": max_score,
        "before_score": before_score,
        "mean_score": mean_score,
        "min_score": min_score,
        "tensor": encoding_tensor,
        "err_type": 0,
    }
    return result
