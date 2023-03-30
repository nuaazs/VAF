<<<<<<< HEAD
# coding = utf-8
# @Time    : 2022-09-05  09:43:48
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: vaf service configuration file.

#######################################################
############## 1. System Configuration ################
#######################################################
"""
WORKERS
    value    : int
    defaule  : 1
    describe : 启动的进程数量
"""
WORKERS = 1

"""
SR
    value    : 16000 or 8000
    defaule  : 16000
    describe : 声纹识别模型需要的采样率
"""
SR = 16000

"""
Device
    value    : "cuda:cuda_num" or "cpu"
    defaule  : "cuda:0"
    describe : 模型运行的设备
"""
DEVICE = "cuda:0"  # "cuda:id" or "cpu"

"""
THREADS
    value    : int
    defaule  : 20
    describe : 使用的线程数
"""
THREADS = 20

"""
WORKER_CONNECTIONS
    value    : int
    defaule  : 20
    describe : 支持最大的链接数
"""
WORKER_CONNECTIONS = 20

"""
PORT
    value    : int
    defaule  : 8186
    describe : 服务端口
"""
PORT = 8186

#######################################################
################### 2. Pre-process ####################
#######################################################
"""
VAD_TYPE
    value    : "speechbrain" or "silero"
    defaule  : "speechbrain"
    describe : VAD后端,silero只能使用cpu
"""
if DEVICE == "cpu":
    VAD_TYPE = "silero"
else:
    VAD_TYPE = "speechbrain" # "speechbrain" or "silero"

"""
DENOISE_TYPE
    value    : "denoiser"
    default  : "denoiser"
    describe : 降噪模型
"""
DENOISE_TYPE = "denoiser" # "none" or "denoiser"

"""
DENOISE_TIME
    value    : "before_vad" or "after_vad" or "before_vad_after_vad" or "none"
    default  : "before_vad"
    describe : 什么时候进行降噪
"""
DENOISE_TIME = "after_vad"

"""
WAV_START
    value    : int
    defaule  : 7
    describe : 音频从第几秒开始读取（即摒弃前几秒的数据）
"""
WAV_START = 7


# Self-test type
# 0: no self-test
# 1: equally divided into SELF_TEST_NUM parts
# 2: randomly divided into SELF_TEST_NUM parts
SELF_TEST_TYPE = 1
SELF_TEST_NUM = 2


"""
CLASSIFY
    value    : True or False
    defaule  : False
    describe : 是否对声纹进行预分类
"""
CLASSIFY = False

"""
CHECK_DUPLICATE
    value    : True or False
    defaule  : False
    describe : 是否检查重复文件,如果为True,会在注册时检查是否有重复文件
"""
CHECK_DUPLICATE = True

DUPLICATE_TYPE = "remove_old"

"""
LOG_PHONE_INFO
    value    : True or False
    defaule  : False
    describe : 是否统计手机地域信息（需要外网）
"""
LOG_PHONE_INFO = False

"""
CLIP_DETECT
    value    : True or False
    defaule  : True
    describe : 是否进行爆破音监测
"""
CLIP_DETECT = True

#######################################################
################### 3. Thresholds #####################
#######################################################
"""
VAD_TYPE
    value    : "speechbrain" or "silero"
    defaule  : "speechbrain"
    describe : VAD后端,silero只能使用cpu
"""
UPDATE = False

"""
VAD_TYPE
    value    : "speechbrain" or "silero"
    defaule  : "speechbrain"
    describe : VAD后端,silero只能使用cpu
"""
UPDATE_DAYS = 90


"""
BLACK_TH
    value    : float
    defaule  : 0.65
    describe : 黑库阈值
"""
BLACK_TH = 0.68

"""
POOL_LIMIT
    value    : int
    defaule  : 5
    describe : 声纹池出现多少次认为可疑
"""
POOL_LIMIT = 5

"""
POOL_TYPE
    value    : "recursion" or "quick"
    defaule  : "recursion"
    describe : 声纹池筛选方式
"""
POOL_TYPE = "quick"

"""
CLIP_TH
    value    : float
    defaule  : 0.3
    describe : 爆破音阈值
"""
CLIP_TH = 0.03

"""
UPDATE_TH
    value    : float
    defaule  : 0.8
    describe : 声纹更新特征阈值
"""
UPDATE_TH = 0.85

"""
UPDATE_DAYS
    value    : int
    defaule  : 90
    describe : 声纹更新时间阈值（天数）
"""
UPDATE_DAYS = 90

"""
MIN_LENGTH_REGISTER
    value    : float
    defaule  : 10.0
    describe : 音频注册时的最小有效时长
"""
MIN_LENGTH_REGISTER = 10.0

"""
MIN_LENGTH_TEST
    value    : float
    defaule  : 10.0
    describe : 音频推理时的最小有效时长
"""
MIN_LENGTH_TEST = 10.0

"""
SELF_TEST_TH
    value    : float
    defaule  : 0.8
    describe : 自我监测前后端相似度阈值
"""
SELF_TEST_TH = 0.76

"""
SELF_TEST_SL
    value    : 
    defaule  : 
    describe : 
"""
SELF_TEST_SL = 3

"""
SELF_TEST_SS
    value    : 
    defaule  : 
    describe : 
"""
SELF_TEST_SS = 2

"""
WAV_LENGTH
    value    : float
    defaule  : 180.0
    describe : 音频最长限制,最多只读取多少秒
"""
WAV_LENGTH = 180

"""
WAV_CHANNEL
    value    : int
    defaule  : 1
    describe : 使用音频的第几个通道 [WAV_LENGTH,:]
"""
WAV_CHANNEL = 0

"""
SAVE_PREPROCESSED_OSS
    value    : True or False
    defaule  : True
    describe : 保存预处理后的音频
"""
SAVE_PREPROCESSED_OSS = True


#######################################################
#################### 4. Databases #####################
#######################################################
MYSQL = {
    "host": "sh-cdb-cnzwlk0y.sql.tencentcdb.com",
    "port": 58974,
    "db": "si",
    "username": "root",
    "passwd": "Nt3380518!zhaosheng123",
} 

REDIS = {
    "host": "192.168.3.202",
    "port": 6379,
    "register_db": 1,
    "test_db": 2,
    "password": "",
}

MINIO = {
    "host": "192.168.3.202",
    "port": 9000,
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "test_save_days": 30,
    "register_save_days": -1,
    "register_raw_bucket": "register_raw",
    "register_preprocess_bucket": "register_preprocess",
    "test_raw_bucket": "test_raw",
    "test_preprocess_bucket": "test_preprocess",
    "pool_raw_bucket": "pool_raw",
    "pool_preprocess_bucket": "pool_preprocess",
    "black_raw_bucket": "black_raw",
    "black_preprocess_bucket": "black_preprocess",
    "white_raw_bucket": "white_raw",
    "white_preprocess_bucket": "white_preprocess",
}
BUCKETS = ["raw","preprocess","preprocessed","testing","sep"]

SQL_TABLES = ["si","si_pool"]
SQL_FILES = {
    "si": "./database/si_1124.sql",
    "si_pool": "./database/si_1124.sql",
}

SERVER_INFO = {"name": "lyxx-192.168.3.202","ip":"106.14.148.126","port":PORT}

"""
ASR SERVER
    value    : "http://192.168.3.202:8000/asr"
    default  : "http://192.168.3.202:8000/asr"
    describe : asr接口地址
"""
ASR_SERVER = "http://192.168.3.202:8000/asr"
BLACK_WORDS_PATH = "/VAF/src/black_words.txt"
=======
# Workers
WORKERS = 2

# Threads
THREADS = 10

# Device
DEVICE = "cpu"

# Max Connections
WORKER_CONNECTIONS = 10

# Port
PORT = 8180

# Do Pre Classify
pre_classify = False

# Log Phone Info Or Not
LOG_PHONE_INFO = False

# Clipping Detect
CLIP_DETECT = False

# Auto Test
AUTO_TEST = False

# Save Raw File (=None, means don't save)
RAW_FILE_PATH = None # "/VAF-System/src/wavs/raw"

# Save Preprocessed File (=None, means don't save)
VAD_FILE_PATH = None # "/VAF-System/src/wavs/preprocessed"

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
            "host": "",
            "port": 27546,
            "db": "si2",
            "username": "root",
            "passwd": ""
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
>>>>>>> aaf98c0f80d54045f84fd2aed04556c602508d9f
