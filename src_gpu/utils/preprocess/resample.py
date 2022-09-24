# coding = utf-8
# @Time    : 2022-09-05  15:32:55
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Resample.

from calendar import c
import torchaudio.transforms as T
import torchaudio
import os
import sys

# cfg
import cfg


def resample(
    wav_filepath,
    action_type,
    sr_dst=cfg.SR,
    channel=cfg.WAV_CHANNEL,
    wav_length=cfg.WAV_LENGTH,
):
    """Read the file to check the file size and duration validity
         and upsample it to the specified sample rate.

    Args:
        wav_filepath (string): wav file path.

    Returns:
        Numpy Array (2D [channel,data]) : wav data.
    """

    # if action_type=="register":
    #     min_length = cfg.MIN_LENGTH_REGISTER
    # elif action_type=="test":
    #     min_length = cfg.MIN_LENGTH_TEST
    # else:
    #     min_length = sys.maxsize

    wav, sr = torchaudio.load(wav_filepath)
    if len(wav.shape) > 1 and wav.shape[0] > 1:
        # Multi-channel audio, and the number of channels is greater than 1
        if wav.shape[1] > sr * (wav_length):
            wav = wav[channel, : (wav_length) * sr]
        else:
            wav = wav[channel, :]
    elif len(wav.shape) > 1:
        # Multi-channel audio, and the number of channels is equal to 1
        wav = wav[0]
        if wav.shape[0] > sr * (wav_length):
            wav = wav[: (wav_length) * sr]
        else:
            wav = wav
    else:
        # single channel audio
        if wav.shape[0] > sr * (wav_length):
            wav = wav[: (wav_length) * sr]
        else:
            wav = wav

    if sr != sr_dst:
        resampler = T.Resample(sr, sr_dst)
        wav = resampler(wav)

    # os.remove(wav_file)
    if os.path.isfile(wav_filepath):
        # Audio files are deleted, but the speaker directory remains
        cmd = f"rm -rf {wav_filepath}"
        os.system(cmd)

    return wav
