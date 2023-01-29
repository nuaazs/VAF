# coding = utf-8
# @Time    : 2022-09-05  09:42:43
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: The main function entry of the project.

import json
from flask import Flask
from flask import render_template
from flask import request
from flask_cors import CORS
from flask_sock import Sock
import time
import torch


# utils
from utils.advanced import general
from utils.advanced import init_service

# ws query
from utils.orm.ws_query import *
# config
import cfg

# checker
from checker.cuda_checker import check as check_cuda
from checker.minio_checker import check as check_minio
from checker.redis_checker import check as check_redis
from checker.mysql_checker import check as check_mysql

# app
app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+pymysql://{cfg.MYSQL['username']}:\
            {cfg.MYSQL['passwd']}@{cfg.MYSQL['host']}:{cfg.MYSQL['port']}/{cfg.MYSQL['db']}"
app.config["SQLALCHEMY_TRACK_MOD/IFICATIONS"] = False
sock = Sock(app)
CORS(app, supports_credentials=True, origins="*", methods="*", allow_headers="*")

system_info = init_service()

# HomePage
@app.route("/", methods=["GET"])
def index():
    system_info = init_service()
    cuda_check_result,cuda_check_message = check_cuda()
    minio_check_result,minio_check_message = check_minio()
    redis_check_result,redis_check_message = check_redis()
    mysql_check_result,mysql_check_message = check_mysql()
    kwargs = {
        "spks_num": system_info["spks_num"],
        "spks": system_info["spks"][:10],
        "name": system_info["name"],
        "config" : str(cfg),
        "ip": cfg.SERVER_INFO["ip"],
        "port": cfg.SERVER_INFO["port"],
        "cuda_check_result": cuda_check_result,
        "cuda_check_message": cuda_check_message,
        "minio_check_result": minio_check_result,
        "minio_check_message": minio_check_message,
        "redis_check_result": redis_check_result,
        "redis_check_message": redis_check_message,
        "mysql_check_result": mysql_check_result,
        "mysql_check_message": mysql_check_message,
    }
    return render_template("index.html", **kwargs)

# Register Or Reasoning.
@app.route("/<action_type>/<file_mode>", methods=["POST"])
def register_or_reasoning(action_type, file_mode):
    if action_type not in ["register", "test"]:
        return json.dumps({"code": 4000, "status": "fail", "err_type": 1, "err_msg": "action_type error"})
    if request.method == "POST":
        response = general(
            request_form=request.form, file_mode=file_mode, action_type=action_type
        )
        if "cuda" in cfg.DEVICE:
            torch.cuda.empty_cache()
        return json.dumps(response, ensure_ascii=False)

# Register Or Reasoning.
@app.route("/pretest/<action_type>", methods=["GET"])
def pretest(action_type):

    # generate random id
    random_id = str(time.time()).replace(".", "")[-5:]
    wav_url = f"http://{cfg.MINIO['host']}:{cfg.MINIO['port']}/testing/2p2c16k.wav"
    test_form = {
        "spkid": f"999{random_id}",
        "spkname": f"just_for_test_{random_id}",
        "show_phone":f"999{random_id}",
        "wav_channel": "1",
        "wav_url": wav_url,
        "pool":False
    }
    if action_type=="pool":
        test_form["pool"]=True
        response = general(
            request_form=test_form, file_mode="url", action_type="test"
        )
        if "cuda" in cfg.DEVICE:
            torch.cuda.empty_cache()
        return json.dumps(response, ensure_ascii=False)

    response = general(
        request_form=test_form, file_mode="url", action_type=action_type
    )
    if "cuda" in cfg.DEVICE:
        torch.cuda.empty_cache()
    return json.dumps(response, ensure_ascii=False)

# Websockets
@sock.route('/namelist_ws')
def namelist_ws(sock):
    while True:
        sock.send(query_speaker())
        time.sleep(3)


@app.route('/namelist', methods=["GET"])
def namelist():
    return json.dumps(query_speaker(), ensure_ascii=False)


@sock.route('/hit_phone_info_ws')
def hit_phone_info_ws(sock):
    while True:
        sock.send(query_hit_phone())
        time.sleep(3)

# 省份信息删除了
# @sock.route('/hit_info_ws')
# def hit_info_ws(sock):
#     while True:
#         sock.send(query_hit_location())
#         time.sleep(3)
 
@sock.route('/database_info_ws')
def database_info_ws(sock):
    while True:
        sock.send(query_database_info())
        time.sleep(3)

@sock.route('/date_info_ws')
def date_info_ws(sock):
    while True:
        date = time.strftime("%Y%m%d",time.localtime(time.time()))
        sock.send(query_date_info(date))
        time.sleep(3)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0", threaded=False, port=cfg.PORT, debug=False,
    )
