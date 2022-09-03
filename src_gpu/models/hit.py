# @Time    : 2022-07-27  19:05:04
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/models/hit.py
# @Describe: Hit.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Hit(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(128),primary_key=True,unique=True)
    file_url = db.Column(db.String(256),primary_key=True,unique=True)
    preprocessed_file_url = db.Column(db.String(256),default="",primary_key=True,unique=True)
    province = db.Column(db.String(10))
    city = db.Column(db.String(10))
    phone_type = db.Column(db.String(10))
    area_code = db.Column(db.String(10))
    zip_code = db.Column(db.String(10))
    self_test_score_mean = db.Column(db.Float(8),default=0.0)
    self_test_score_min = db.Column(db.Float(8),default=0.0)
    self_test_score_max = db.Column(db.Float(8),default=0.0)
    call_begintime = db.Column(db.DateTime)
    call_endtime = db.Column(db.DateTime)
    span_time = db.Column(db.Integer())
    class_number = db.Column(db.Integer())
    hit_time = db.Column(db.DateTime,default=datetime.now)
    blackbase_phone = db.Column(db.String(128))
    blackbase_id = db.Column(db.String(12))
    hit_status =  db.Column(db.Integer())
    hit_score = db.Column(db.String(512))
    top_10 = db.Column(db.String(1280))
    valid_length = db.Column(db.Integer(),default=0)
    is_grey = db.Column(db.Integer(),default=0)