# coding = utf-8
# @Time    : 2022-09-05  15:34:32
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: VAD.

import torch
import os
from utils.oss import upload_file
import cfg

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

def vad(wav,spkid):
    before_vad_length = len(wav)/16000.

    spk_dir = os.path.join("/tmp", str(spkid))
    os.makedirs(spk_dir, exist_ok=True)
    spk_filelist = os.listdir(spk_dir)
    speech_number = len(spk_filelist) + 1
    save_name = f"preprocessed_{spkid}_{speech_number}.wav"
    
    final_save_path = os.path.join(spk_dir, save_name)
    wav = torch.FloatTensor(wav)
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000,window_size_samples=1536)
    print(speech_timestamps)
    wav = collect_chunks(speech_timestamps, wav)
    save_audio(final_save_path,wav, sampling_rate=16000)
    preprocessed_file_path=upload_file(bucket_name='preprocessed',filepath=final_save_path,filename=save_name,save_days=cfg.MINIO["test_save_days"])
    
    after_vad_length = len(wav)/16000.
    wav = torch.FloatTensor(wav)
    result = {
        "wav_torch":wav,
        "before_length":before_vad_length,
        "after_length":after_vad_length,
        "preprocessed_file_path":preprocessed_file_path,
    }
    os.remove(final_save_path)
    return result
