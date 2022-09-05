from utils.orm import get_embeddings
from utils.log import logger
import cfg

def init_service():
    black_database = get_embeddings(blackbase=cfg.BLACK_BASE,class_index=-1)
    spks = list(black_database.keys())
    spks_num = len(spks)
    name = cfg["name"]
    logger.info(f"** Start! Total speaker num:{spks_num}")
    return {
        "spks":spks,
        "spks_num":spks_num,
        "name":name
    }