import torchaudio.transforms as T
import torchaudio
import cfg

wav_length = cfg.WAV_LENGTH
channel = cfg.WAV_CHANNEL

def resample(wav_file):
    wav, sr = torchaudio.load(wav_file)

    if len(wav.shape)>1 and wav.shape[0]>1:
        if wav.shape[1]>sr*(wav_length):
            wav = wav[channel,:(wav_length)*sr]
        else:
            wav = wav[channel,:]
    elif len(wav.shape)>1:
        wav = wav[0]
        if wav.shape[0]>sr*(wav_length):
            wav = wav[:(wav_length)*sr]
        else:
            wav = wav
    else:
        if wav.shape[0]>sr*(wav_length):
            wav = wav[:(wav_length)*sr]
        else:
            wav = wav
    if sr != 16000:
        resampler = T.Resample(sr, 16000)
        wav = resampler(wav)
    return wav
