import torchaudio
from speechbrain.pretrained import EncoderClassifier
import torch
# Model is downloaded from the speechbrain HuggingFace repo
classifier = EncoderClassifier.from_hparams(
    source="/ssd2/voiceprint-recognition-system/src/nn/ECAPATDNN-16k-phone_1",
    savedir="./pretrained_models/spkrec-ecapa-voxceleb",
)
# Compute embeddings
# signal, fs = torchaudio.load("samples/audio_samples/example1.wav")
# embeddings =  classifier.encode_batch(signal)
# print Module.modules sub module names
# print(type(classifier.mods.embedding_model))
# for name, module in classifier.named_modules():
#     # if name == "embedding_model":
#     print(name)
#     # print(type(module))

# change speechbrain.lobes.models.ECAPA_TDNN.ECAPA_TDNN to torch.nn.Module
compute_features_nn_module = classifier.mods.compute_features
# add_wav_lens = torch.
mean_var_norm_nn_module = classifier.mods.mean_var_norm
embedding_model_nn_module = classifier.mods.embedding_model

import torch
# import onnx
import onnxruntime

class AudioEmbeddingModel(torch.nn.Module):
    def __init__(self):
        super(AudioEmbeddingModel, self).__init__()
        self.compute_features = compute_features_nn_module
        self.mean_var_norm = mean_var_norm_nn_module
        self.embedding_model = embedding_model_nn_module
    
    def forward(self, wavs, wav_lens):
        feats = self.compute_features(wavs)
        feats = self.mean_var_norm(feats, wav_lens)
        embeddings = self.embedding_model(feats, wav_lens)
        return embeddings

model = AudioEmbeddingModel()
dummy_input = (torch.zeros([1, 16000]), torch.ones([1,]))

# 导出 ONNX 模型
# onnx opset version 12
# torch.onnx.export(model, dummy_input, "audio_embedding_model.onnx", verbose=True, opset_version=12)
torch.onnx.export(model, dummy_input, "audio_embedding_model.onnx", input_names=["wavs", "wav_lens"], output_names=["embeddings"], dynamic_axes={"wavs": {0: "batch_size", 1: "num_audio_frames"}, "wav_lens": {0: "batch_size"}})

# 验证导出结果
# onnx_model = onnx.load("audio_embedding_model.onnx")
# ort_session = onnxruntime.InferenceSession("audio_embedding_model.onnx")

# # merge nn.Module
# nn_module = torch.nn.Sequential(compute_features_nn_module, mean_var_norm_nn_module, embedding_model_nn_module)
# print(type(nn_module))
# # change to onnx
# torch.onnx.export(nn_module, torch.randn(1, 1,16000), "ecapa_tdnn.onnx", verbose=True, opset_version=11)