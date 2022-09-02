# @Time    : 2022-07-27  19:05:52
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/encoder/encoder.py
# @Describe: Models.

from speechbrain.pretrained import SpeakerRecognition
import torch
import cfg

similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
spkreg = SpeakerRecognition.from_hparams(
    source="/VAF-System/src/pretrained_ecapa", savedir="/VAF-System/src/pretrained_ecapa"
    ,run_opts={"device":cfg.DEVICE})
