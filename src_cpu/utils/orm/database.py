# @Time    : 2022-07-27  18:55:16
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : ./src/utils/database.py
# @Describe: load database from reids or pickle file.

import pickle
from utils.phone_util import getPhoneInfo
import struct
import redis
import numpy as np
import cfg

def toRedis(r,a,n):
    """Store given Numpy array 'a' in Redis under key 'n'"""
    shape = struct.pack('>II',192,1)
    encoded = shape + a.tobytes()
    r.set(n,encoded)
    return

def fromRedis(r,n):
    """Retrieve Numpy array from Redis key 'n'"""
    encoded = r.get(n)
    a = np.frombuffer(encoded, dtype=np.float32, offset=8)
    return a

def deletRedis(r,n):
    if (r.keys(f"*{n}*")):
        r.delete(*r.keys(f"*{n}*"))
    return

def get_all_embedding(blackbase="redis",class_index=-1):
    class_index = -1
    if blackbase  != 'redis':
        with open(cfg.BLACK_BASE, 'rb') as f:
            all_spker_embedding = pickle.load(f)
        all_embedding = {}
        for key in all_spker_embedding.keys():
            if "_" not in key:
                continue
            class_index_now = int(key.split("_")[0])
            if class_index_now == class_index or class_index == -1:
                spkid = key.split("_")[1]
                embedding_1 = all_spker_embedding[key]["embedding_1"]
                all_embedding[spkid] = {"embedding_1":embedding_1}
            else:
                continue
        return all_embedding

    else:
        r = redis.Redis(host=cfg.REDIS["host"], port=cfg.REDIS["port"], db=cfg.REDIS["register_db"],password=cfg.REDIS["password"])
        all_embedding = {}
        for key in r.keys():
            key = key.decode('utf-8')
            if "_" not in key:
                continue
            class_index_now = int(key.split("_")[0])
            if class_index_now == class_index or class_index == -1:
                spkid = key.split("_")[1]
                embedding_1 = fromRedis(r,key)
                all_embedding[spkid] = {"embedding_1":embedding_1}
            else:
                continue
        return all_embedding

def add_to_database(blackbase,embedding,spkid,max_class_index,log_phone_info,mode="register"):
    if log_phone_info:
        phone_info = getPhoneInfo(spkid[-11:])
    else:
        phone_info = {}
    embedding_npy = embedding.detach().cpu().numpy()

    if blackbase == 'redis':
        if mode=="register":
            db = cfg.REDIS["register_db"]
        else:
            db = cfg.REDIS["test_db"]
        r = redis.Redis(host=cfg.REDIS["host"], port=cfg.REDIS["port"], db=db,password=cfg.REDIS["password"])
        toRedis(r,embedding_npy,f'{max_class_index}_{spkid}')
    else:
        return False,"only allow redis database."
    return True,phone_info

def delete_by_key(blackbase,spkid):
    r = redis.Redis(host=cfg.REDIS["host"], port=cfg.REDIS["port"], db=cfg.REDIS["register_db"],password=cfg.REDIS["password"])
    deletRedis(r,spkid)
    return

def save_redis_to_pkl():
    r = redis.Redis(host=cfg.REDIS["host"], port=cfg.REDIS["port"], db=cfg.REDIS["register_db"],password=cfg.REDIS["password"])
    all_embedding = {}
    for key in r.keys():
        key = key.decode('utf-8')
        spkid = key
        embedding_1 = fromRedis(r,key)
        all_embedding[spkid] = {"embedding_1":embedding_1}
    with open(cfg.BLACK_BASE, 'wb') as f:
        pickle.dump(all_embedding, f, pickle.HIGHEST_PROTOCOL)