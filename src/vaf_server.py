# coding = utf-8
# @Time    : 2022-09-05  09:42:43
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: The main function entry of the project.

import json
import os

import torchaudio
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
from utils.preprocess import save_file, save_url, vad, resample

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
    cuda_check_result, cuda_check_message = check_cuda()
    minio_check_result, minio_check_message = check_minio()
    redis_check_result, redis_check_message = check_redis()
    mysql_check_result, mysql_check_message = check_mysql()
    kwargs = {
        "spks_num": system_info["spks_num"],
        "spks": system_info["spks"][:10],
        "name": system_info["name"],
        "config": str(cfg),
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
        response = general(request_form=request.form, file_mode=file_mode, action_type=action_type)
        if "cuda" in cfg.DEVICE:
            torch.cuda.empty_cache()
        return json.dumps(response, ensure_ascii=False)


@app.route("/vad/<file_mode>", methods=["POST"])
def get_vad(file_mode):
    """
    VAD API
    Args:
        file_mode:

    Returns:

    """
    spkid = request.form["spkid"]

    # STEP 1: Get wav file.
    if file_mode == "file":
        new_file = request.files["wav_file"]
        filepath, _ = save_file(file=new_file, spk=spkid)
    elif file_mode == "url":
        new_url = request.form.get("wav_url")
        filepath, _ = save_url(url=new_url, spk=spkid)

    # STEP 1.5: Resample wav file.
    wav = resample(wav_filepath=filepath, action_type=None)

    # STEP 2: VAD
    vad_result = vad(wav=wav, spkid=spkid)
    os.makedirs(f"/tmp/output_vad", exist_ok=True)
    torchaudio.save(f"/tmp/output_vad/{spkid}.wav", vad_result['wav_torch'].reshape(1, -1), cfg.SR)

    if "cuda" in cfg.DEVICE:
        torch.cuda.empty_cache()
    response = {'output_vad_file_path': f"/tmp/output_vad/{spkid}.wav"}

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
