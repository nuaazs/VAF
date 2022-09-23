# coding = utf-8
# @Time    : 2022-09-05  09:42:43
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: main.

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


# Get score from two file.
@app.route("/score/<test_type>", methods=["POST"])
def score(test_type):
    if request.method == "POST":
        request_form = request.form
        response = get_score(request_form, get_type=test_type)
        return json.dumps(response, ensure_ascii=False)


# Test
@app.route("/test/<test_type>", methods=["POST"])
def test(test_type):
    if request.method == "POST":
        request_form = request.form
        response = general(request_form, get_type=test_type, action_type="test")
        return json.dumps(response, ensure_ascii=False)


# Register
@app.route("/register/<register_type>", methods=["POST"])
def register(register_type):
    if request.method == "POST":
        request_form = request.form
        response = general(request_form, get_type=register_type, action_type="register")
        return json.dumps(response, ensure_ascii=False)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0", threaded=False, port=8187, debug=True,
    )
