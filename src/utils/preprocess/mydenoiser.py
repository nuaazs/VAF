import torch
from denoiser import pretrained
from denoiser.dsp import convert_audio

model = pretrained.dns64().cuda()


def denoise_wav(wav_data, denoise_type=1):
    with torch.no_grad():
        denoised = model(wav_data)[0]
    wav_data2 = convert_audio(wav_data.cuda(), 16000, model.sample_rate, model.chin)
    if denoise_type == 1:
        wav_data2 = model(wav_data2)
    diff = torch.abs(wav_data2 - wav_data.cuda())
    wav_data[diff>0.2] = 0
    
    return wav_data
