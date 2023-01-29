import torch
from utils.log.log_wraper import logger

def check():
    # check if cuda is available
    logger.info("\t\t\t -> * Checking CUDA ... ")
    if torch.cuda.is_available():
        logger.info("\t\t\t -> * CUDA test: Pass ! ")
        return True,"cuda is available"
    else:
        logger.info("\t\t\t -> * CUDA test: Error !!! ")
        return False,"cuda is not available"