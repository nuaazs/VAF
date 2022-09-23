# coding = utf-8
# @Time    : 2022-09-05  15:34:32
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: VAD.

import torch
import os
from utils.oss import upload_file
import cfg
from speechbrain.pretrained import VAD
import torchaudio
import numpy as np
import pandas as pd
import re

# else:
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
    run_opts={"device": "cuda"},
)


def vad(wav, spkid):
    before_vad_length = len(wav) / 16000.0

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

    # boundaries=VAD.remove_short_segments(boundaries, len_th=0.250)
    # boundaries=VAD.merge_close_segments(boundaries, close_th=0.250)

    VAD.save_boundaries(
        boundaries,
        save_path=boundaries_save_path,
        print_boundaries=True,
        audio_file=None,
    )

    # print(f"Type : {type(boundaries)}")
    # regex=re.compile('\s+')
    # df =  pd.read_csv(boundaries_save_path,names=['seg','start','end','description'],sep=regex, engine="python")
    # print(df)
    upsampled_boundaries = VAD.upsample_boundaries(boundaries, final_save_path)

    output = wav[upsampled_boundaries[0] > 0.9]
    save_audio(final_save_path, output, sampling_rate=16000)
    wav, sr = torchaudio.load(final_save_path)
    wav = wav[0, :]
    wav = torch.FloatTensor(wav)

    # wav = torch.FloatTensor(wav)
    # speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000,window_size_samples=1536)
    # wav = collect_chunks(speech_timestamps, wav)
    # save_audio(final_save_path,wav, sampling_rate=16000)

    preprocessed_file_path = upload_file(
        bucket_name="preprocessed",
        filepath=final_save_path,
        filename=save_name,
        save_days=cfg.MINIO["test_save_days"],
    )

    os.remove(final_save_path)
    after_vad_length = len(wav) / 16000.0
    wav = torch.FloatTensor(wav)
    result = {
        "wav_torch": wav,
        "before_length": before_vad_length,
        "after_length": after_vad_length,
        "preprocessed_file_path": preprocessed_file_path,
    }
    return result
