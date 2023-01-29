# coding = utf-8
# @Time    : 2022-09-05  15:33:45
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Save file.

import os
import wget
import subprocess
import shutil
from utils.oss import upload_file
import cfg


def save_file(file, spk):
    """save wav file from post request.

    Args:
        file (request.file): wav file.
        spk (string): speack id
        receive_path (string): save path

    Returns:
        string: file path
    """
    receive_path = "/tmp/"
    spk_dir = os.path.join(receive_path, str(spk))
    os.makedirs(spk_dir, exist_ok=True)
    spk_filelist = os.listdir(spk_dir)
    speech_number = len(spk_filelist) + 1
    # receive wav file and save it to  ->  <receive_path>/<spk_id>/raw_?.webm
    pid = os.getpid()
    ext = file.filename.split('.')[-1]
    print("save file type:", ext)
    save_name = f"raw_{speech_number}_{pid}.{ext}"
    save_path = os.path.join(spk_dir, save_name)
    save_path_wav = os.path.join(spk_dir, f"raw_{speech_number}_{pid}.wav")
    file.save(save_path)
    print(f"save to {save_path}")
    # conver to wav
    if ext!="wav":
        # cmd = f"ffmpeg -i {save_path} -ar 16000 -ac 1 -vn -map_channel 0.0.{cfg.WAV_CHANNEL} {save_path_wav}" #   
        cmd = f"ffmpeg -i {save_path} -ac 1 -ar 16000 {save_path_wav}"
        subprocess.call(cmd, shell=True)
        # print(save_path)
        cmd = f"rm {save_path}"
        subprocess.call(cmd, shell=True)
    else:
        save_path_wav = save_path
    raw_file_path = upload_file(
        bucket_name="raw",
        filepath=save_path_wav,
        filename=f"raw_{spk}_{speech_number}_{pid}.wav",
        save_days=cfg.MINIO["test_save_days"],
    )
    return save_path_wav, raw_file_path


def save_url(url, spk):
    """save wav file from post request.

    Args:
        file (request.file): wav file.
        spk (string): speack id
        receive_path (string): save path

    Returns:
        string: file path
    """
    receive_path = "/tmp/"
    spk_dir = os.path.join(receive_path, str(spk))
    os.makedirs(spk_dir, exist_ok=True)
    spk_filelist = os.listdir(spk_dir)
    speech_number = len(spk_filelist) + 1
    # receive wav file and save it to  ->  <receive_path>/<spk_id>/raw_?.webm

    pid = os.getpid()
    ext = url.split('.')[-1]
    save_name = f"raw_{speech_number}_{pid}.{ext}"

    if url.startswith("local://"):
        previous_path = url.replace("local://", "")
        save_path = os.path.join(spk_dir, save_name)
        shutil.copy(previous_path, save_path)
    else:
        save_path = os.path.join(spk_dir, save_name)
        wget.download(url, save_path)

    if ext!="wav":
        save_path_wav = os.path.join(spk_dir, f"raw_{speech_number}_{pid}.wav")
        # conver to wav
        # cmd = f"ffmpeg -i {save_path} -ac 1 -ar 16000 -vn -map_channel 0.0.{cfg.WAV_CHANNEL} {save_path_wav}"
        cmd = f"ffmpeg -i {save_path} -ac 1 -ar 16000 {save_path_wav}"
        subprocess.call(cmd, shell=True)
        cmd = f"rm {save_path}"
        subprocess.call(cmd, shell=True)
    else:
        save_path_wav = save_path
    raw_file_path = upload_file(
        bucket_name="raw",
        filepath=save_path_wav,
        filename=f"raw_{spk}_{speech_number}_{pid}.wav",
        save_days=cfg.MINIO["test_save_days"],
    )

    return save_path_wav, raw_file_path
