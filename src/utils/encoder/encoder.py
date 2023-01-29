# coding = utf-8
# @Time    : 2022-09-05  15:04:36
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: models.

from speechbrain.pretrained import SpeakerRecognition
import torch
import cfg

similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
spkreg = SpeakerRecognition.from_hparams(
    source="./nn/ecapa",
    savedir="./pretrained_models/ecapa",
    run_opts={"device": cfg.DEVICE},
)
