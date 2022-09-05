from encoder import spkreg
import torch

def self_test(wav_torch, spkreg,similarity, sr=16000, min_length=5, similarity_limit=0.60):
    max_score = 0
    min_score = 1

    wav_length = int((len(wav_torch)-10)/2)
    wav_torch = wav_torch.unsqueeze(0)
    left = torch.cat((wav_torch[:,:wav_length],wav_torch[:,:wav_length]), dim=1)
    right = torch.cat((wav_torch[:,wav_length:wav_length*2],wav_torch[:,wav_length:wav_length*2]), dim=1)
    wav_torch = wav_torch[:,:left.shape[1]]


    batch = torch.cat((wav_torch,left,right), dim=0)
    encode_result = spkreg.encode_batch(batch)
    embedding = encode_result[0][0]

    similarity(encode_result[2][0], encode_result[1][0])
    
    embedding = spkreg.encode_batch(batch)

    encoding_tensor = embedding[0]
    encoding_tiny_1 = embedding[1][0]
    encoding_tiny_2 = embedding[2][0]
    score = similarity(encoding_tiny_1, encoding_tiny_2)

    max_score,mean_score,min_score = score,score,score
    used_time = time.time() - local_time

    if score < similarity_limit:
        result = {
            "pass":False,
            "msg":f"Bad quality score:{min_score}.",
            "max_score":max_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "used_time":used_time,
        }
        return result
    result = {
            "pass":True,
            "msg":"Qualified.",
            "max_score":max_score,
            "mean_score":mean_score,
            "min_score":min_score,
            "used_time":used_time,
            "tensor":encoding_tensor
        }
    print(f"Encoder used time:{used_time}")
    return result
