# @Time    : 2022-07-27  18:56:04
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/log_wraper.py
# @Describe: logger wraper.

from logging.handlers import RotatingFileHandler
import logging

# common log
logger = logging.getLogger("si_log")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "[%(asctime)s]  %(levelname)s  [%(filename)s]  #%(lineno)d <%(process)d:%(thread)d>  %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
)
handler = RotatingFileHandler(
    "./log/si.log", maxBytes=20 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
handler.setFormatter(formatter)
handler.namer = lambda x: "si." + x.split(".")[-1]
logger.addHandler(handler)


# error log
err_logger = logging.getLogger("err_log")
err_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "[%(asctime)s]  %(levelname)s  [%(filename)s]  #%(lineno)d <%(process)d:%(thread)d>  %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
)
err_handler = RotatingFileHandler(
    "./log/err.log", maxBytes=20 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
err_handler.setFormatter(formatter)
err_handler.namer = lambda x: "err." + x.split(".")[-1]
err_logger.addHandler(err_handler)

