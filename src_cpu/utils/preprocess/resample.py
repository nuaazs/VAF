# coding = utf-8
# @Time    : 2022-09-05  15:32:55
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Resample.

import torchaudio.transforms as T
import torchaudio
import cfg
import os

wav_length = cfg.WAV_LENGTH
channel = cfg.WAV_CHANNEL
sr_dst = cfg.SR
def resample(wav_file):
    wav, sr = torchaudio.load(wav_file)
    if len(wav.shape)>1 and wav.shape[0]>1:
        if wav.shape[1]>sr*(wav_length):
            wav = wav[channel,:(wav_length)*sr]
        else:
            wav = wav[channel,:]
    elif len(wav.shape)>1:
        wav = wav[0]
        if wav.shape[0]>sr*(wav_length):
            wav = wav[:(wav_length)*sr]
        else:
            wav = wav
    else:
        if wav.shape[0]>sr*(wav_length):
            wav = wav[:(wav_length)*sr]
        else:
            wav = wav
    if sr != sr_dst:
        resampler = T.Resample(sr, sr_dst)
        wav = resampler(wav)
    
    
    # os.remove(wav_file)
    if os.path.isfile(wav_file):
        cmd = f"rm -rf {wav_file}"
        os.system(cmd)
        
    return wav
