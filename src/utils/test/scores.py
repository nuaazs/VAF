# coding = utf-8
# @Time    : 2022-09-05  15:35:17
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Scores.
import os

import torch
import numpy as np
from utils.orm.query import get_wav_url
import cfg


def get_scores(database, new_embedding, black_limit, similarity, top_num=10):
    return_results = {}
    results = []
    top_list = ""
    # Read embeddings in database
    for base_item in database:
        base_embedding = torch.tensor(database[base_item]["embedding_1"])
        results.append([similarity(base_embedding, new_embedding), base_item])
    results = sorted(results, key=lambda x: float(x[0]) * (-1))
    return_results["best_score"] = float(np.array(results[0][0]))

    if results[0][0] <= black_limit:
        return_results["inbase"] = 0
        return return_results, top_list
    else:
        return_results["inbase"] = 1
        # top1-top10
        for index in range(top_num):
            return_results[f"top_{index + 1}"] = f"{results[index][0].numpy():.5f}"
            return_results[f"top_{index + 1}_id"] = str(results[index][1])
            top_list += f"Top {index + 1} 评分:{results[index][0].numpy():.2f} 说话人:{results[index][1]}<br/>"
    return return_results, top_list


def self_check(database, embedding, spkid, black_limit, similarity, top_num=10):
    results = []
    return_results = {}
    for base_item in database.keys():
        base_embedding = torch.tensor(database[base_item]["embedding_1"])
        results.append([similarity(base_embedding, embedding), base_item])
    results = sorted(results, key=lambda x: float(x[0]) * (-1))
    best_score = float(np.array(results[0][0]))
    best_id = str(np.array(results[0][1]))
    return_results["best_score"] = best_score

    inbase = False

    for key in database.keys():
        if spkid[-11:] == key[-11:]:
            inbase = True
            break

    if inbase:
        if best_score > black_limit:
            return_results["inbase"] = 1
            # top1-top10
            for index in range(top_num):
                if results[index][1][-11:] == spkid[-11:]:
                    msg = f"在黑库中,正确,第{index + 1}个命中了。得分:{results[index][0]},now_spk:{spkid},best score:{best_score},spk:{best_id}"
                    return True, 1, msg, {"best_score": best_score, "spk": best_id}
            msg = f"在黑库中,错误,但未命中,now_spk:{spkid},best score:{best_score},spk:{best_id}"
            return False, 2, msg, {"best_score": best_score, "spk": best_id}
        else:
            return (
                True,
                3,
                f"在黑库中,错误,不满足阈值,now_spk:{spkid},best score:{best_score},spk:{best_id}",
                {"best_score": best_score, "spk": best_id},
            )
    else:

        if best_score < black_limit:
            msg = f"不在黑库中,正确,now_spk:{spkid},best score:{best_score},spk:{best_id}"
            return True, 4, msg, {"best_score": best_score, "spk": best_id}
        else:
            msg = f"不在黑库中,错误,now_spk:{spkid},best score:{best_score},spk:{best_id}"
            return False, 5, msg, {"best_score": best_score, "spk": best_id}


def test_wav(database, embedding, spkid, black_limit, similarity, top_num=10):
    results = []
    return_results = {}
    for base_item in database.keys():
        base_embedding = torch.tensor(database[base_item]["embedding_1"])
        results.append([np.array(similarity(base_embedding, embedding)), base_item])
    results = sorted(results, key=lambda x: float(x[0]) * (-1))
    top_10 = [f"{_score},{_spk_id}" for _score, _spk_id in results[:10]]
    best_score = float(np.array(results[0][0]))
    best_id = str(",".join(map(str, np.array(results)[:10, 1])))
    top_10 = str("|".join(map(str, np.array(top_10))))
    return_results["best_score"] = best_score
    inbase = best_score >= black_limit
    return inbase, {"best_score": best_score, "spk": best_id, "top_10": top_10}


def find_similar_wav(database, spk_id_a, embedding_a, similarity, pool_info):
    results = []
    for base_item in database.keys():
        base_embedding = torch.tensor(database[base_item]["embedding_1"]).to(cfg.DEVICE)
        score = similarity(base_embedding, embedding_a).detach().cpu().numpy()
        if score < 1:
            results.append(
                [score, base_item, base_embedding]
            )
    results = sorted(results, key=lambda x: float(x[0]) * (-1))
    for _score, _spk_id, embedding_b in results:
        if _score < cfg.BLACK_TH:
            break
        wav_url = get_wav_url(_spk_id)
        pool_info.append({"score": str(_score), "spk_id_a": spk_id_a, "spk_id_b": _spk_id, "wav_url": wav_url})
        pool_info = find_similar_wav(database, _spk_id, embedding_b, similarity, pool_info)
    return pool_info


def test_wav(database, embedding, spkid, black_limit, similarity, pool, top_num=10):
    if pool:

        results = []
        embedding = torch.tensor(embedding).to('cpu')
        for base_item in database.keys():
            base_embedding = torch.tensor(database[base_item]["embedding_1"]).to('cpu')
            score = similarity(base_embedding, embedding).detach().cpu().numpy()[0]
            results.append(
                [score, base_item, base_embedding]
            )
        results = sorted(results, key=lambda x: float(x[0]) * (-1))
        pool_info = []
        if cfg.POOL_TYPE == "quick":
            for _score, _spk_id, embedding_b in results[:500]:
                if _score < cfg.BLACK_TH:
                    break
                wav_url = get_wav_url(_spk_id)
                pool_info.append({"score": str(_score), "spk_id_a": spkid, "spk_id_b": _spk_id, "wav_url": wav_url})
            # 去重
            out_info = []
            id_list = []
            for _data in pool_info:
                if (_data["spk_id_a"] == _data["spk_id_b"]):
                    continue
                elif (_data["spk_id_a"] > _data["spk_id_b"]):
                    if _data["spk_id_a"] + _data["spk_id_b"] not in id_list:
                        out_info.append(
                            {"score": _data["score"], "spk_id_a": _data["spk_id_a"], "spk_id_b": _data["spk_id_b"],
                             "wav_url": _data["wav_url"]})
                        id_list.append(_data["spk_id_a"] + _data["spk_id_b"])
                else:
                    if _data["spk_id_b"] + _data["spk_id_a"] not in id_list:
                        out_info.append(
                            {"score": _data["score"], "spk_id_a": _data["spk_id_b"], "spk_id_b": _data["spk_id_a"],
                             "wav_url": _data["wav_url"]})
                        id_list.append(_data["spk_id_b"] + _data["spk_id_a"])

            if len(out_info) >= cfg.POOL_LIMIT:
                in_pool = True
            else:
                in_pool = False

        if cfg.POOL_TYPE == "recursion":
            for _score, _spk_id, embedding_b in results[:500]:
                if _score < cfg.BLACK_TH:
                    break
                wav_url = get_wav_url(_spk_id)
                pool_info.append({"score": str(_score), "spk_id_a": spkid, "spk_id_b": _spk_id, "wav_url": wav_url})
                # 递归
                pool_info = find_similar_wav(database, _spk_id, embedding_b, similarity, pool_info)
            # 去重
            out_info = []
            id_list = []
            for _data in pool_info:
                if (_data["spk_id_a"] == _data["spk_id_b"]):
                    continue
                elif (_data["spk_id_a"] > _data["spk_id_b"]):
                    if _data["spk_id_a"] + _data["spk_id_b"] not in id_list:
                        out_info.append(
                            {"score": _data["score"], "spk_id_a": _data["spk_id_a"], "spk_id_b": _data["spk_id_b"],
                             "wav_url": _data["wav_url"]})
                        id_list.append(_data["spk_id_a"] + _data["spk_id_b"])
                else:
                    if _data["spk_id_b"] + _data["spk_id_a"] not in id_list:
                        out_info.append(
                            {"score": _data["score"], "spk_id_a": _data["spk_id_b"], "spk_id_b": _data["spk_id_a"],
                             "wav_url": _data["wav_url"]})
                        id_list.append(_data["spk_id_b"] + _data["spk_id_a"])

            if len(out_info) >= cfg.POOL_LIMIT:
                in_pool = True
            else:
                in_pool = False

        return in_pool, {"pool_info": out_info}
    else:
        results = []
        return_results = {}
        embedding = torch.tensor(embedding).to('cpu')
        for base_item in database.keys():
            base_embedding = torch.tensor(database[base_item]["embedding_1"]).to('cpu')
            results.append(
                [similarity(base_embedding, embedding).detach().cpu().numpy(), base_item]
            )
        results = sorted(results, key=lambda x: float(x[0]) * (-1))
        top_10 = [f"{_score},{_spk_id}" for _score, _spk_id in results[:10]]
        best_score = float(np.array(results[0][0]))
        best_id = str(",".join(map(str, np.array(results)[:10, 1])))
        top_10 = str("|".join(map(str, np.array(top_10))))
        return_results["best_score"] = best_score
        inbase = best_score >= black_limit
        return inbase, {"best_score": best_score, "spk": best_id, "top_10": top_10}
