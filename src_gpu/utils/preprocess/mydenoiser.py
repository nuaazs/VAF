import torch
from denoiser import pretrained
from denoiser.dsp import convert_audio

model = pretrained.dns64().cuda()

def denoise_wav(wav_data):
    wav_data = convert_audio(wav_data.cuda(), 16000, model.sample_rate, model.chin)
    with torch.no_grad():
        denoised = model(wav_data[None])[0]
    return denoised