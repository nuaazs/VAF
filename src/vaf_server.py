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
    system_info = init_service()
    kwargs = {
        "spks_num": system_info["spks_num"],
        "spks": system_info["spks"][:10],
        "name": system_info["name"],
    }
    return render_template("index.html", **kwargs)

# Register Or Reasoning.
@app.route("/<action_type>/<file_mode>", methods=["POST"])
def register_or_reasoning(action_type, file_mode):
    if request.method == "POST":
        response = general(
            request_form=request.form, file_mode=file_mode, action_type=action_type
        )
        return json.dumps(response, ensure_ascii=False)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0", threaded=False, port=cfg.PORT, debug=True,
    )
