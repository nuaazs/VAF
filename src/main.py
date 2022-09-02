# @Time    : 2022-07-27  19:17:59
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/vvs_service.py
# @Describe: App.

import json
import time
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_sock import Sock

# utils
from utils.database import get_all_embedding
from utils.query import query_speaker,query_hit_phone,query_hit_location,query_database_info,query_date_info
from utils.log_wraper import logger
from utils.main import get_form_data,get_slience_form_data

# config
import cfg

# encoder
from encoder.encoder import *

# model
from models.log import db as log_db,Log
from models.speaker import db as speaker_db,Speaker
from models.hit import db as hit_db,Hit

# app
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=f"mysql+pymysql://{cfg.MYSQL['username']}:{cfg.MYSQL['passwd']}@{cfg.MYSQL['host']}:{cfg.MYSQL['port']}/{cfg.MYSQL['db']}"
app.config["SQLALCHEMY_TRACK_MOD/IFICATIONS"]=False

log_db.app = app
speaker_db.app = app
log_db.init_app(app)
speaker_db.init_app(app)
sock = Sock(app)
CORS(app, supports_credentials=True,
        origins="*", methods="*", allow_headers="*")

# Load blackbase
load_blackbase_start = time.time()
black_database = get_all_embedding(blackbase=cfg.BLACK_BASE,class_index=-1)
spks = list(black_database.keys())
spks_num = len(spks)
logger.info(f"** Start! Load database used:{time.time() - load_blackbase_start:.2f}s. Total speaker num:{spks_num}")

# HomePage
@app.route("/", methods=["GET"])
def index():
    spks = list(black_database.keys())
    spks_num = len(spks)
    kwargs = {
        "spks_num": spks_num,
        "spks":spks[:10],
        "name":cfg.SERVER_INFO["name"]
    }
    return render_template('index.html',**kwargs)

# Test
@app.route("/test/<test_type>", methods=["POST"])
def test(test_type):
    if request.method == "POST":
        request_form = request.form
        response = get_form_data(request_form,cfg,get_type=test_type,action="test")
        return json.dumps(response, ensure_ascii=False)

# Register
@app.route("/register/<register_type>", methods=["POST"])
def register(register_type):
    if request.method == "POST":
        request_form = request.form
        response = get_form_data(request_form,cfg,get_type=register_type,action="register")
        return json.dumps(response, ensure_ascii=False)

# Register
@app.route("/slience/<file_type>", methods=["POST"])
def slience(file_type):
    if request.method == "POST":
        request_form = request.form
        response = get_slience_form_data(request_form,cfg,get_type=file_type)
        return json.dumps(response, ensure_ascii=False)

# Websockets
@sock.route('/namelist_ws')
def namelist_ws(sock):
    while True:
        sock.send(query_speaker())
        time.sleep(10)

@sock.route('/hit_phone_info_ws')
def hit_phone_info_ws(sock):
    while True:
        sock.send(query_hit_phone())
        time.sleep(10)

@sock.route('/hit_info_ws')
def hit_info_ws(sock):
    while True:
        sock.send(query_hit_location())
        time.sleep(10)
 
@sock.route('/database_info_ws')
def database_info_ws(sock):
    while True:
        sock.send(query_database_info())
        time.sleep(10)

@sock.route('/date_info_ws')
def date_info_ws(sock):
    while True:
        date = time.strftime("%Y%m%d",time.localtime(time.time()))
        sock.send(query_date_info(date))
        time.sleep(10)

#with app.app_context():
#    log_db.create_all()
#    speaker_db.create_all()
#    hit_db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=False, port=8180, debug=True,)
