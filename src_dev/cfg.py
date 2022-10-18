# coding = utf-8
# @Time    : 2022-09-05  09:43:48
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: service configuration file.

# Workers
WORKERS = 2

SR = 16000

CUDA_NUM = 0

# Device
DEVICE = "cuda:0"  # "cuda:id" or "cpu"

# Threads
THREADS = 20

# UPDATE
UPDATE = False

# UPDATE_DAYS
UPDATE_DAYS = 90

# start second
WAV_START = 0

# Max Connections
WORKER_CONNECTIONS = 20

# Port
PORT = 8180

# Classify
CLASSIFY = True

# Check duplicate
CHECK_DUPLICATE = False

# Log Phone Info Or Not
LOG_PHONE_INFO = False

# Clipping Detect
CLIP_DETECT = True

# Black Base Threshold
BLACK_TH = 0.795

# Clipping Detection Threshold(>0.99)
CLIP_TH = 0.03

# Similarity threshold for audio updates of the same ID
UPDATE_TH = 0.8

UPDATE_DAYS = 90

# Min Length Of VAD-WAV
MIN_LENGTH_REGISTER = 10
MIN_LENGTH_TEST = 5

# Self-Test Limit
SELF_TEST_TH = 0.6

# Self-Test segment length
SELF_TEST_SL = 3

# Self-Test segment stride
SELF_TEST_SS = 2

# Max Length Of VAD-WAV
WAV_LENGTH = 90

# Use Which Channel
WAV_CHANNEL = 1

# Whether to save the preprocessed file
SAVE_PREPROCESSED_OSS = True

# Mysql
MYSQL = {
    "host": "zhaosheng.mysql.rds.aliyuncs.com",
    "port": 27546,
    "db": "si2",
    "username": "root",
    "passwd": "Nt3380518!zhaosheng123",
}
# Redis
REDIS = {
    "host": "192.168.3.202",
    "port": 6379,
    "register_db": 1,
    "test_db": 2,
    "password": "",
}

# MinIO
MINIO = {
    "host": "192.168.3.202",
    "port": 9000,
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "test_save_days": 30,
    "register_save_days": -1,
}

# Server Info
SERVER_INFO = {"name": "lyxx-192.168.3.202"}
