# coding = utf-8
# @Time    : 2022-09-05  09:42:43
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: The main function entry of the project.

import time
import json
import torch
from flask import Flask
from flask import request
from flask_cors import CORS
from flask_sock import Sock
from flask import render_template

# utils
from utils.advanced import general
from utils.advanced import init_service

# config
import cfg

# checker
from checker import check_all


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
    # init service
    system_info = init_service()
    # check
    check, check_result, check_message = check_all()
    kwargs = {
        "spks_num": system_info["spks_num"],
        "spks": system_info["spks"][:10],
        "name": system_info["name"],
        "config": str(cfg),
        "ip": cfg.SERVER_INFO["ip"],
        "port": cfg.SERVER_INFO["port"],
        "cuda_check_result": check_result["cuda"],
        "cuda_check_message": check_message["cuda"],
        "minio_check_result": check_result["minio"],
        "minio_check_message": check_message["minio"],
        "redis_check_result": check_result["redis"],
        "redis_check_message": check_message["redis"],
        "mysql_check_result": check_result["mysql"],
        "mysql_check_message": check_message["mysql"],
        "asr_check_result": check_result["asr"],
        "asr_check_message": check_message["asr"],
    }
    return render_template("index.html", **kwargs)


# Register Or Reasoning.
@app.route("/<action_type>/<file_mode>", methods=["POST"])
def register_or_reasoning(action_type, file_mode):
    """register or reasoning API

    Args:
        action_type (string): "register" or "test"
        file_mode (string): "url" or "file"

    Returns:
        json: response
    """
    if action_type not in ["register", "test"]:
        return json.dumps({"code": 4000, "status": "fail", "err_type": 1, "err_msg": "action_type error"})
    if request.method == "POST":
        response = general(request_form=request.form, file_mode=file_mode, action_type=action_type)
        if "cuda" in cfg.DEVICE:
            # clear cuda cache
            torch.cuda.empty_cache()
        return json.dumps(response, ensure_ascii=False)


@app.route("/vad/<file_mode>", methods=["POST"])
def get_vad(file_mode):
    """get vad result
    
    Args:
        file_mode (string): "url" or "file"

    Returns:
        json: response
    """
    response = {}
    return json.dumps(response, ensure_ascii=False)


# Test ALL API
@app.route("/pretest/<action_type>", methods=["GET"])
def pretest(action_type):
    # generate random id
    random_id = str(time.time()).replace(".", "")[-5:]
    wav_url = f"http://{cfg.MINIO['host']}:{cfg.MINIO['port']}/testing/2p2c16k.wav"
    test_form = {
        "spkid": f"999{random_id}",
        "spkname": f"just_for_test_{random_id}",
        "show_phone": f"999{random_id}",
        "wav_channel": "1",
        "wav_url": wav_url,
        "pool": False
    }
    if action_type == "pool":
        test_form["pool"] = True
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=cfg.PORT, debug=False)