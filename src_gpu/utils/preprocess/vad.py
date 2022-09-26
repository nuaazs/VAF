# coding = utf-8
# @Time    : 2022-09-05  15:34:32
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: VAD.

import torch
import os
from speechbrain.pretrained import VAD
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

USE_ONNX = True
model, utils = torch.hub.load(
    repo_or_dir="./snakers4_silero-vad_master",
    source="local",
    model="silero_vad",
    force_reload=False,
    onnx=USE_ONNX,
)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils


VAD = VAD.from_hparams(
    source="speechbrain/vad-crdnn-libriparty",
    savedir="./nn/vad",
    run_opts={"device": cfg.DEVICE},
)


def vad(wav, spkid, action_type, device=cfg.DEVICE):
    """Audio silence clip removal
    Args:
        wav (Numpy array (1D)): audio data
        spkid (string): speaker ID

    Returns:
        Numpy array (1D) : audio data
    """
    # if action_type=="register":
    #     min_length = cfg.MIN_LENGTH_REGISTER
    # elif action_type=="test":
    #     min_length = cfg.MIN_LENGTH_TEST
    # else:
    #     min_length = sys.maxsize

    before_vad_length = len(wav) / cfg.SR

    spk_dir = os.path.join("/tmp", str(spkid))
    os.makedirs(spk_dir, exist_ok=True)
    spk_filelist = os.listdir(spk_dir)
    speech_number = len(spk_filelist) + 1
    save_name = f"preprocessed_{spkid}_{speech_number}.wav"
    final_save_path = os.path.join(spk_dir, save_name)
    boundaries_save_path = os.path.join(spk_dir, f"{spkid}.txt")
    save_audio(final_save_path, wav, sampling_rate=16000)

    boundaries = VAD.get_speech_segments(
        audio_file=final_save_path,
        large_chunk_size=30,
        small_chunk_size=10,
        overlap_small_chunk=True,
        apply_energy_VAD=True,
        double_check=False,
        close_th=0.250,
        len_th=0.50,
        activation_th=0.5,
        deactivation_th=0.25,
        en_activation_th=0.5,
        en_deactivation_th=0.0,
        speech_th=0.50,
    )

    # VAD.save_boundaries(
    #     boundaries,
    #     save_path=boundaries_save_path,
    #     print_boundaries=False,
    #     audio_file=None,
    # )

    upsampled_boundaries = VAD.upsample_boundaries(boundaries, final_save_path)
    output_wav = wav[upsampled_boundaries[0] > 0.99]

    if cfg.SAVE_PREPROCESSED_OSS:
        save_audio(final_save_path, output_wav, sampling_rate=16000)
        preprocessed_file_path = upload_file(
            bucket_name="preprocessed",
            filepath=final_save_path,
            filename=save_name,
            save_days=cfg.MINIO["test_save_days"],
        )
    else:
        preprocessed_file_path = ""


    path = Path(final_save_path)
    # os.remove(final_save_path)
    if os.path.isfile(final_save_path):
        # Audio files are deleted, but the speaker directory remains
        cmd = f"rm -rf {path.parent.absolute()} & rm -rf ./pretrained_model_checkpoints/{path.name}"
        print(cmd)
        os.system(cmd)

    after_vad_length = len(output_wav) / 16000.0
    output_wav = torch.FloatTensor(output_wav)
    result = {
        "wav_torch": output_wav,
        "before_length": before_vad_length,
        "after_length": after_vad_length,
        "preprocessed_file_path": preprocessed_file_path,
    }
    return result
