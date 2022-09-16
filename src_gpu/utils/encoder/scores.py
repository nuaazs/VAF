# coding = utf-8
# @Time    : 2022-09-05  15:04:48
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: get scores.
import torch
import numpy as np

def get_scores(database,new_embedding,black_limit,similarity,top_num=10):
    return_results = {}
    results = []
    top_list = ""
    # Read embeddings in database
    for base_item in database:
        base_embedding = torch.tensor(database[base_item]["embedding_1"])
        results.append([similarity(base_embedding, new_embedding), base_item])
    results = sorted(results, key=lambda x:float(x[0])*(-1))
    return_results["best_score"] = float(np.array(results[0][0]))


    if results[0][0] <= black_limit:
        return_results["inbase"] = 0

        return return_results,top_list
    else:
        return_results["inbase"] = 1
        # top1-top10
        for index in range(top_num):
            return_results[f"top_{index+1}"] = f"{results[index][0].numpy():.5f}"
            return_results[f"top_{index+1}_id"] = str(results[index][1])
            top_list+=f"Top {index+1} 评分:{results[index][0].numpy():.2f} 说话人:{results[index][1]}<br/>"

    return return_results,top_list


def test_wav(database,embedding,spkid,black_limit,similarity,top_num=10):
    results = []
    return_results = {}
    for base_item in database.keys():
        base_embedding = torch.tensor(database[base_item]["embedding_1"])
        results.append([np.array(similarity(base_embedding, embedding)), base_item])
    results = sorted(results, key=lambda x:float(x[0])*(-1))
    top_10 = [f"{_score},{_spk_id}" for _score,_spk_id in results[:10]]
    best_score = float(np.array(results[0][0]))
    best_id = str(",".join(map(str,np.array(results)[:10,1])))
    top_10 = str("|".join(map(str,np.array(top_10))))
    return_results["best_score"] = best_score

    inbase = (best_score>= black_limit)
    return inbase,{"best_score":best_score,"spk":best_id,"top_10":top_10}
