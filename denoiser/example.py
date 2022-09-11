from IPython import display as disp
import torch
import torchaudio
from denoiser import pretrained
from denoiser.dsp import convert_audio
from speechbrain.pretrained import SpeakerRecognition
import torch

similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
spkreg = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb",
    run_opts={"device":"cuda"})


black = "/mnt/zhaosheng/Voiceprint-Recognition-System-bak/test/voiceprint-recognition-system/api_test/loupan/loupan/17751156796/black_8157.wav"
grey = "/mnt/zhaosheng/Voiceprint-Recognition-System-bak/test/voiceprint-recognition-system/api_test/loupan/loupan/17751156796/grey_3012293.wav"
def save_audio(path: str,
               tensor: torch.Tensor,
               sampling_rate: int = 16000):
    torchaudio.save(path, tensor.data.cpu(), sampling_rate)


model = pretrained.dns64().cuda()
wav_black, sr_wav = torchaudio.load(black)
wav_grey, sr_grey = torchaudio.load(grey)
wav_black = convert_audio(wav_black.cuda(), sr_wav, model.sample_rate, model.chin)
wav_grey = convert_audio(wav_grey.cuda(), sr_grey, model.sample_rate, model.chin)
with torch.no_grad():
    denoised_black = model(wav_black[None])[0]
    denoised_grey = model(wav_grey[None])[0]

save_audio("./raw_black.wav",wav_black,sampling_rate=model.sample_rate)
save_audio("./denoised_black.wav",denoised_black,sampling_rate=model.sample_rate)
save_audio("./raw_grey.wav",wav_grey,sampling_rate=model.sample_rate)
save_audio("./denoised_grey.wav",denoised_grey,sampling_rate=model.sample_rate)




from speechbrain.pretrained import VAD
import torchaudio

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

VAD = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty",
                            run_opts={"device":"cuda"})


def vad(final_save_path):
    boundaries = VAD.get_speech_segments(audio_file=final_save_path,
                                        large_chunk_size=30,
                                        small_chunk_size=10,
                                        overlap_small_chunk=True,
                                        apply_energy_VAD=False,
                                        double_check=False,
                                        close_th=0.250,
                                        len_th=0.250,
                                        activation_th=0.5,
                                        deactivation_th=0.25,
                                        en_activation_th=0.5,
                                        en_deactivation_th=0.0,
                                        speech_th=0.50,
                                    )
  
    upsampled_boundaries = VAD.upsample_boundaries(boundaries, final_save_path) 
    output = wav[upsampled_boundaries[0]>0.9]
    save_audio(final_save_path,output, sampling_rate=16000)
    wav, sr = torchaudio.load(final_save_path)
    wav = wav[0,:]
    wav = torch.FloatTensor(wav)
    return wav


wav1=vad("./denoised_grey.wav")
wav2=vad("./denoised_black.wav")
print(wav1.shape)
print(similarity(wav1,wav2))