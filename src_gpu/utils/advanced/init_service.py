# coding = utf-8
# @Time    : 2022-09-05  09:48:38
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Init service.

from utils.orm import get_embeddings
from utils.log import logger
import cfg


def init_service():
    black_database = get_embeddings(class_index=-1)
    spks = list(black_database.keys())
    spks_num = len(spks)
    name = cfg.SERVER_INFO["name"]
    logger.info(f"** Start! Total speaker num:{spks_num}")
    return {"spks": spks, "spks_num": spks_num, "name": name}
