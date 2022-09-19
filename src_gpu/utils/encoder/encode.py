# coding = utf-8
# @Time    : 2022-09-05  15:02:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: self-test and encode.

from asyncio.log import logger
from utils.encoder import spkreg
from utils.encoder import similarity
from utils.preprocess.mydenoiser import denoise_wav
import torch
import cfg

def encode(wav_torch_raw):
    similarity_limit = cfg.SELF_TEST_TH
    min_length = cfg.MIN_LENGTH
    sr = cfg.SR
    max_score = 0
    mean_score = 0
    min_score = 1

    if len(wav_torch_raw)/sr <= min_length:
        result = {
            "pass":False,
            "msg":f"Insufficient duration, the current duration is {len(wav_torch_raw)/sr}s.",
            "max_score":0,
            "mean_score":0,
            "min_score":0,
            "err_type": 6,
            "before_score":None,
        }
        return result

    wav_length = int((len(wav_torch_raw)-10)/2)
    wav_torch = wav_torch_raw.unsqueeze(0)
    left = torch.cat((wav_torch[:,:wav_length],wav_torch[:,:wav_length]), dim=1)
    right = torch.cat((wav_torch[:,wav_length:wav_length*2],wav_torch[:,wav_length:wav_length*2]), dim=1)
    wav_torch = wav_torch[:,:left.shape[1]]
    batch = torch.cat((wav_torch,left,right), dim=0)
    encode_result = spkreg.encode_batch(batch)
    
    embedding = encode_result[0][0]
    similarity(encode_result[2][0], encode_result[1][0])
    embedding = spkreg.encode_batch(batch)
    encoding_tensor = embedding[0]
    encoding_tiny_1 = embedding[1][0]
    encoding_tiny_2 = embedding[2][0]
    score = similarity(encoding_tiny_1, encoding_tiny_2)
    max_score,mean_score,min_score = score,score,score

    if score < similarity_limit:
        # return do_denoise(wav_torch_raw,score)
        result = {
            "pass":False,
            "msg":f"Bad quality score:{min_score}.",
            "max_score":max_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "err_type": 7,

        }
        return result
    result = {
            "pass":True,
            "msg":"Qualified.",
            "max_score":max_score,
            "before_score":None,
            "mean_score":mean_score,
            "min_score":min_score,
            "tensor":encoding_tensor,
            "err_type": 0
        }
    return result

def do_denoise(wav,before_score):
    logger.info("Denoising ...")
    similarity_limit = cfg.SELF_TEST_TH
    min_length = cfg.MIN_LENGTH
    sr = cfg.SR
    max_score = 0
    mean_score = 0
    min_score = 1
    wav_torch = denoise_wav(wav.unsqueeze(0))

    wav_length = int((wav_torch.shape[1]-10)/2)
    left = torch.cat((wav_torch[:,:wav_length],wav_torch[:,:wav_length]), dim=1)
    right = torch.cat((wav_torch[:,wav_length:wav_length*2],wav_torch[:,wav_length:wav_length*2]), dim=1)
    wav_torch = wav_torch[:,:left.shape[1]]
    batch = torch.cat((wav_torch,left,right), dim=0)
    embedding = spkreg.encode_batch(batch)
    encoding_tensor = embedding[0]
    encoding_tiny_1 = embedding[1][0]
    encoding_tiny_2 = embedding[2][0]
    score = similarity(encoding_tiny_1, encoding_tiny_2)
    max_score,mean_score,min_score = score,score,score
    if score < similarity_limit:
        result = {
            "pass":False,
            "msg":f"Bad quality score:{min_score}.",
            "before_score":float(before_score.detach().cpu().numpy()),
            "max_score":max_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "err_type": 7,

        }
        return result
    result = {
            "pass":True,
            "msg":"Qualified.",
            "max_score":max_score,
            "before_score":before_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "tensor":encoding_tensor,
            "err_type": 0
        }
    return result