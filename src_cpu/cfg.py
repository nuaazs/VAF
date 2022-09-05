# Workers
WORKERS = 2

# Threads
THREADS = 10

# Max Connections
WORKER_CONNECTIONS = 10

# Port
PORT = 8180

# Classify
CLASSIFY = True

# Log Phone Info Or Not
LOG_PHONE_INFO = False

# Clipping Detect
CLIP_DETECT = True

# Black Base Threshold
BLACK_TH = 0.82

# Clipping Detection Threshold(>0.99)
CLIP_TH = 0.03

# Min Length Of VAD-WAV
MIN_LENGTH = 10

# Self-Test Limit
SELF_TEST_TH = 0.75

# Max Length Of VAD-WAV
WAV_LENGTH = 90

# Use Which Channel
WAV_CHANNEL = 1

# Mysql
MYSQL = {
            "host": "zhaosheng.mysql.rds.aliyuncs.com",
            "port": 27546,
            "db": "si2",
            "username": "root",
            "passwd": "Nt3380518!zhaosheng123"
    }
# Redis
REDIS = {
    "host":'192.168.0.14',
    "port":6379,
    "register_db":1,
    "test_db":2,
    "password":""
}

# MinIO
MINIO = {
    "host": "192.168.0.14",
    "port": 9000,
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "test_save_days" : 30,
    "register_save_days": -1,
}

# Black Base File Path (='redis' use redis)
BLACK_BASE = "redis" # "/VAF-System/src/wavs/database/blackbase.pkl"

# Server Info
SERVER_INFO = {
    "name":"lyxx78"
}
