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
    save_name = f"raw_{speech_number}_{pid}.webm"
    save_path = os.path.join(spk_dir, save_name)
    save_path_wav = os.path.join(spk_dir, f"raw_{speech_number}_{pid}.wav")
    file.save(save_path)
    # conver to wav
    # cmd = f"ffmpeg -i {save_path} -ac 1 -ar 16000 {save_path_wav}"
    # subprocess.call(cmd, shell=True)
    # cmd = f"rm {save_path}"
    # subprocess.call(cmd, shell=True)
    raw_file_path = upload_file(
        bucket_name="raw",
        filepath=save_path,
        filename=f"raw_{spk}_{speech_number}_{pid}.wav",
        save_days=cfg.MINIO["test_save_days"],
    )
    return save_path, raw_file_path


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
    save_name = f"raw_{speech_number}_{pid}.wav"

    if url.startswith("local://"):
        previous_path = url.replace("local://", "")
        save_path = os.path.join(spk_dir, save_name)
        shutil.copy(previous_path, save_path)
    else:
        save_path = os.path.join(spk_dir, save_name)
        wget.download(url, save_path)

    raw_file_path = upload_file(
        bucket_name="raw",
        filepath=save_path,
        filename=f"raw_{spk}_{speech_number}_{pid}.wav",
        save_days=cfg.MINIO["test_save_days"],
    )

    return save_path, raw_file_path
