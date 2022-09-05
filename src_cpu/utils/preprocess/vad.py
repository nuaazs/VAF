from speechbrain.pretrained import VAD
import torchaudio

VAD = VAD.from_hparams(source="pretrained_models/vad-crdnn-libriparty",
                            run_opts={"device":"cpu"})

def vad_and_upsample(file_path,pre_path):
    boundaries = VAD.get_speech_segments(audio_file=file_path,
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
    # boundaries=VAD.remove_short_segments(boundaries, len_th=0.250)
    # boundaries=VAD.merge_close_segments(boundaries, close_th=0.250)
    upsampled_boundaries = VAD.upsample_boundaries(boundaries, file_path) 
    output = wav[upsampled_boundaries[0]>0.9]
    save_audio(pre_path, output, sampling_rate=16000)
    return wav