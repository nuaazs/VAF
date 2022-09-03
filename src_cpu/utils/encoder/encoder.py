from speechbrain.pretrained import SpeakerRecognition
import torch

similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6)
spkreg = SpeakerRecognition.from_hparams(
    source="./nn/pretrained_ecapa",
    savedir="./nn/pretrained_ecapa"
    ,run_opts={"device":"cpu"})