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

# utils
from utils.advanced import general
from utils.advanced import init_service
from utils.advanced import get_score
from utils.advanced import check_new
from utils.advanced import update_embedding
from utils.log import err_logger
from utils.log import logger

# config
import cfg

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
    kwargs = {
        "spks_num": system_info["spks_num"],
        "spks": system_info["spks"][:10],
        "name": system_info["name"],
    }
    return render_template("index.html", **kwargs)


# Get the similarity of two audio files.
@app.route("/score/<test_type>", methods=["POST"])
def score(test_type):
    if request.method == "POST":
        response = get_score(request.form, get_type=test_type)
        return json.dumps(response, ensure_ascii=False)


# TODO: Get the similarity of the two audio tracks and compare the ratings 
# to determine whether to replace the new audio with the old one
# Perform the audio update process
@app.route("/update/<file_type>", methods=["POST"])
def update(file_type):
    if request.method == "POST":
        check_result = check_new(request.form, get_type=file_type)
        print(check_result)
        if check_result["replace"]:
            response = update_embedding(request.form, get_type=file_type)
            return json.dumps(response, ensure_ascii=False)
        else:
            return json.dumps(check_result, ensure_ascii=False)


# Register Or Reasoning.
@app.route("/<action_type>/<test_type>", methods=["POST"])
def register_or_reasoning(action_type, test_type):
    if request.method == "POST":
        response = general(
            request_form=request.form, get_type=test_type, action_type=action_type
        )
        return json.dumps(response, ensure_ascii=False)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0", threaded=False, port=cfg.PORT, debug=False,
    )
