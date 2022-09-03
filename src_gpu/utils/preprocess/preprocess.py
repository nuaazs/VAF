# @Time    : 2022-07-27  18:58:05
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/preprocess.py
# @Describe: Preprocess wav files.

import torch
import torchaudio.transforms as T
import os
import soundfile as sf
import time
from utils.oss import upload_file
import cfg
from speechbrain.pretrained import VAD
import torchaudio
import numpy as np
if cfg.DEVICE == "cuda":
    VAD = VAD.from_hparams(source="pretrained_models/vad-crdnn-libriparty",
                            run_opts={"device":cfg.DEVICE})
# else:
USE_ONNX = True
model, utils = torch.hub.load(repo_or_dir='./snakers4_silero-vad_master',
                            source='local',
                            model='silero_vad',
                            force_reload=False,
                            onnx=USE_ONNX)
(get_speech_timestamps,
save_audio,
read_audio,
VADIterator,
collect_chunks) = utils

def vad_and_upsample(wav_file,spkid,device="cuda",wav_length=90,savepath=None,channel=1,save_days=30):
    local_time = time.time()
    wav, sr = torchaudio.load(wav_file)
    if len(wav.shape)>1:
        if wav.shape[1]>sr*(wav_length):
            wav = wav[channel,:(wav_length)*sr]
        else:
            wav = wav[channel,:]
    else:
        if wav.shape[1]>sr*(wav_length):
            wav = wav[:(wav_length)*sr]
        else:
            wav = wav
    if sr != 16000:
        resampler = T.Resample(sr, 16000)
        wav = resampler(wav)
    before_vad_length = len(wav)/sr
    if not savepath:
            savepath = "/tmp"
    spk_dir = os.path.join(savepath, str(spkid))
    os.makedirs(spk_dir, exist_ok=True)
    spk_filelist = os.listdir(spk_dir)
    speech_number = len(spk_filelist) + 1
    # receive wav file and save it to  ->  <receive_path>/<spk_id>/raw_?.webm
    save_name = f"preprocessed_{spkid}_{speech_number}.wav"
    final_save_path = os.path.join(spk_dir, save_name)
    save_audio(final_save_path,wav, sampling_rate=16000)

    if device == "cuda":
        boundaries = VAD.get_speech_segments(audio_file=final_save_path,
                                        large_chunk_size=30,
                                        small_chunk_size=10,
                                        overlap_small_chunk=True,
                                        apply_energy_VAD=False,
                                        double_check=False,
                                        close_th=0.250,
                                        len_th=0.250,
                                        activation_th=0.5,
                                        deactivation_th=0.25,
                                        en_activation_th=0.5,
                                        en_deactivation_th=0.0,
                                        speech_th=0.50,
                                    )
        # boundaries=VAD.remove_short_segments(boundaries, len_th=0.250)
        # boundaries=VAD.merge_close_segments(boundaries, close_th=0.250)
        upsampled_boundaries = VAD.upsample_boundaries(boundaries, final_save_path) 
        output = wav[upsampled_boundaries[0]>0.9]
        save_audio(final_save_path,output, sampling_rate=16000)
        wav, sr = torchaudio.load(final_save_path)
        wav = wav[0,:]
        wait_time = 0
        wav = np.array(wav)
        wav = torch.FloatTensor(wav)
    else:
        wav = torch.FloatTensor(wav)
        speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000,window_size_samples=1536)
        if len(speech_timestamps)>1:
            wait_time = (speech_timestamps[1]["start"] - speech_timestamps[0]["end"])/16000
        else:
            wait_time = 0
        wav = collect_chunks(speech_timestamps, wav)
        
        save_audio(final_save_path,wav, sampling_rate=16000)

    preprocessed_file_path=upload_file(bucket_name='preprocessed',filepath=final_save_path,filename=save_name,save_days=save_days)
    
    after_vad_length = len(wav)/16000.
    used_time = time.time() - local_time

    print(f"VAD used time:{used_time}")
    result = {
        "wav_torch":wav,
        "before_length":before_vad_length,
        "after_length":after_vad_length,
        "save_path":final_save_path,
        "used_time":used_time,
        "preprocessed_file_path":preprocessed_file_path,
        "wait_time":wait_time,

    }
    return result

def self_test_and_encode(wav_torch, spkreg,similarity, sr=16000, min_length=5, similarity_limit=0.60):
    """Quality detection function, self-splitting into multiple fragments and then testing them in pairs.

    Args:
        wav_torch (torch.tensor): input wav
        spkreg (speechbarin.model): embedding model from speechbrain.
        similarity (function): similarity function
        sr (int, optional): sample rate. Defaults to 16000.
        split_num (int, optional): split wav to <num> fragments. Defaults to 3.
        min_length (int, optional): length(s) of each fragment. Defaults to 3.
        similarity_limit (float, optional): similarity limit for self-test. Defaults to 0.7.

    Returns:
        _type_: pass or not, message
    """
    local_time = time.time()
    max_score = 0
    min_score = 1

    if len(wav_torch)/sr <= min_length:
        used_time = time.time() - local_time
        result = {
            "pass":False,
            "msg":f"Insufficient duration, the current duration is {len(wav_torch)/sr}s.",
            "max_score":0,
            "mean_score":0,
            "min_score":0,
            "used_time":used_time,
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
    used_time = time.time() - local_time

    if score < similarity_limit:
        result = {
            "pass":False,
            "msg":f"Bad quality score:{min_score}.",
            "max_score":max_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "used_time":used_time,
        }
        return result
    result = {
            "pass":True,
            "msg":"Qualified.",
            "max_score":max_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "used_time":used_time,
            "tensor":encoding_tensor
        }
    print(f"Encoder used time:{used_time}")
    return result
