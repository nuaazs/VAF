# coding = utf-8
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask_cors import CORS
from flask_sock import Sock

# utils
from utils.advanced import test
from utils.advanced import register
from utils.advanced import init_service
from utils.log import logger

# config
import cfg

# model
from models.log import db as log_db,Log
from models.speaker import db as speaker_db,Speaker
from models.hit import db as hit_db,Hit

# app
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=f"mysql+pymysql://{cfg.MYSQL['username']}:\
            {cfg.MYSQL['passwd']}@{cfg.MYSQL['host']}:{cfg.MYSQL['port']}/{cfg.MYSQL['db']}"
app.config["SQLALCHEMY_TRACK_MOD/IFICATIONS"]=False

log_db.app = app
speaker_db.app = app
log_db.init_app(app)
speaker_db.init_app(app)
sock = Sock(app)
CORS(app, supports_credentials=True,
        origins="*", methods="*", allow_headers="*")

system_info = init_service()

# HomePage
@app.route("/", methods=["GET"])
def index():
    kwargs = {
        "spks_num": system_info["spks_num"],
        "spks":system_info["spks"][:10],
        "name":system_info["name"]
    }
    return render_template('index.html',**kwargs)

# Test
@app.route("/test/<test_type>", methods=["POST"])
def test(test_type):
    if request.method == "POST":
        request_form = request.form
        response = test(request_form,cfg,get_type=test_type)
        return json.dumps(response, ensure_ascii=False)

# Register
@app.route("/register/<register_type>", methods=["POST"])
def register(register_type):
    if request.method == "POST":
        request_form = request.form
        response = register(request_form,cfg,get_type=register_type)
        return json.dumps(response, ensure_ascii=False)

#with app.app_context():
#    log_db.create_all()
#    speaker_db.create_all()
#    hit_db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=False, port=8180, debug=True,)
