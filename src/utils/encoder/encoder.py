# coding = utf-8
# @Time    : 2022-09-05  15:04:36
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: models.

from speechbrain.pretrained import SpeakerRecognition
import torch

similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
spkreg = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="./nn/ecapa",
    run_opts={"device": "cuda:0"},
)
