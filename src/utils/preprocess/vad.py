# coding = utf-8
# @Time    : 2022-09-05  15:34:32
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: VAD.

import torch
import os
# from speechbrain.pretrained import VAD
from utils.preprocess.new_vad import lyxx_VAD
import torchaudio
import numpy as np
import pandas as pd
import re
import sys
from pathlib import Path


# cfg
import cfg

# utils
from utils.oss import upload_file
from utils.cmd import run_cmd
from utils.preprocess.energy_vad import energy_VAD

# log
from utils.log import logger
# save_audio
def save_audio(path: str,
               tensor: torch.Tensor,
               sampling_rate: int = 16000):
    torchaudio.save(path, tensor.unsqueeze(0), sampling_rate, bits_per_sample=16)

random_seed = torch.randint(1000, 9999, (1,)).item()
VAD = lyxx_VAD.from_hparams(
    source=f"./nn/{cfg.VAD_MODEL}",
    savedir=f"./pretrained_models/{cfg.VAD_MODEL}_{random_seed}",
    run_opts={"device": cfg.DEVICE},
)


def get_vad_result(wav):
    # print(wav.shape)
    assert wav.shape[0] == 1
    assert len(wav.shape) == 2
    boundaries = VAD.get_speech_segments(
        wav_data=wav,
        large_chunk_size=cfg.large_chunk_size,
        small_chunk_size=cfg.small_chunk_size,
        overlap_small_chunk=cfg.overlap_small_chunk,
        apply_energy_VAD=cfg.apply_energy_VAD,
        double_check=cfg.double_check,
        close_th=cfg.close_th,
        len_th=cfg.len_th,
        activation_th=cfg.activation_th,
        deactivation_th=cfg.deactivation_th,
        en_activation_th=cfg.en_activation_th,
        en_deactivation_th=cfg.en_deactivation_th,
        speech_th=cfg.speech_th,
    )
    upsampled_boundaries = VAD.upsample_boundaries(boundaries, wav)
    output_wav = wav[upsampled_boundaries > 0.5]
    # torchaudio.save("test.wav",output_wav.reshape(1,-1),cfg.SR)
    return output_wav


def vad(wav, spkid, action_type=None, device=cfg.DEVICE):
    before_vad_length = len(wav[0]) / cfg.SR

    spk_dir = os.path.join(cfg.TEMP_PATH, str(spkid))
    os.makedirs(spk_dir, exist_ok=True)
    spk_filelist = os.listdir(spk_dir)

    speech_number = len(spk_filelist) + 1
    save_name = f"preprocessed_{spkid}_{speech_number}.wav"
    final_save_path = os.path.join(spk_dir, save_name)

    # after vad wav (tensor)
    output_wav = get_vad_result(wav)

    # save
    if cfg.SAVE_PREPROCESSED_OSS:
        save_audio(final_save_path, output_wav, sampling_rate=cfg.SR)
        preprocessed_file_path = upload_file(
            bucket_name="preprocessed",
            filepath=final_save_path,
            filename=save_name,
            save_days=cfg.MINIO["test_save_days"],
        )
    else:
        preprocessed_file_path = ""

    after_vad_length = len(output_wav) / cfg.SR
    output_wav = torch.FloatTensor(output_wav)
    result = {
        "wav_torch": output_wav,
        "before_length": before_vad_length,
        "after_length": after_vad_length,
        "preprocessed_file_path": preprocessed_file_path,
    }
    return result
