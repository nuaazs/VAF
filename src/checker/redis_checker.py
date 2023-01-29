import redis
import cfg
from utils.log.log_wraper import logger

def check():
    # check is redis is connected
    logger.info("\t\t\t -> * Checking redis connection ... ")
    try:
        r = redis.Redis(
            host=cfg.REDIS["host"],
            port=cfg.REDIS["port"],
            db=cfg.REDIS["register_db"],
            password=cfg.REDIS["password"],
        )
        r.ping()
        logger.info("\t\t\t -> * Redis test: Pass ! ")
        return True,"connected"
    except Exception as e:
        print(e)
        logger.error("\t\t\t -> * Redis test: Error !!! ")
        logger.error(f"\t\t\t -> * Reids Error Message: {e}")
        return False,e