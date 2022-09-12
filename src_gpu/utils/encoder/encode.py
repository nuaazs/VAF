# coding = utf-8
# @Time    : 2022-09-05  15:02:51
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: self-test and encode.

from utils.encoder import spkreg
from utils.encoder import similarity
from utils.preprocess import denoise_wav
import torch
import cfg

def encode(wav_torch):
    similarity_limit = cfg.SELF_TEST_TH
    min_length = cfg.MIN_LENGTH
    sr = cfg.SR
    max_score = 0
    mean_score = 0
    min_score = 1

    if len(wav_torch)/sr <= min_length:
        result = {
            "pass":False,
            "msg":f"Insufficient duration, the current duration is {len(wav_torch)/sr}s.",
            "max_score":0,
            "mean_score":0,
            "min_score":0,
            "err_type": 6,
        }
        return result

    wav_length = int((len(wav_torch)-10)/2)
    wav_torch = wav_torch.unsqueeze(0)
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
        return do_denoise(wav_torch[0,:])
    result = {
            "pass":True,
            "msg":"Qualified.",
            "max_score":max_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "tensor":encoding_tensor,
            "err_type": 0
        }
    return result

def do_denoise(wav):
    print("do denoising ... ")
    similarity_limit = cfg.SELF_TEST_TH
    min_length = cfg.MIN_LENGTH
    sr = cfg.SR
    max_score = 0
    mean_score = 0
    min_score = 1
    wav_torch = denoise_wav(wav)
    wav_length = int((len(wav_torch)-10)/2)
    wav_torch = wav_torch.unsqueeze(0)
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
            "mean_score":mean_score,
            "min_score":min_score,
            "tensor":encoding_tensor,
            "err_type": 0
        }
    return result