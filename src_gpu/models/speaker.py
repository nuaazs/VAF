# @Time    : 2022-07-27  19:05:39
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/models/speaker.py
# @Describe: Speaker.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Speaker(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10),default="none")
    file_url = db.Column(db.String(256),primary_key=True,unique=True)
    preprocessed_file_url = db.Column(db.String(256),primary_key=True,unique=True)
    phone = db.Column(db.String(128),primary_key=True,unique=True)
    register_time = db.Column(db.DateTime, default=datetime.now)
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
    delete_time = db.Column(db.DateTime)
    span_time = db.Column(db.Integer())
    status = db.Column(db.Integer(),default=1)                          # 0.未激活  1.激活
    class_number = db.Column(db.Integer())                              # 声纹预分类的类别
    hit_count = db.Column(db.Integer(),default=0)
    input_reason = db.Column(db.Integer(),default=1)
    delete_reason = db.Column(db.Integer(),default=0)
    delete_remark = db.Column(db.String(255))
    valid_length = db.Column(db.Integer(),default=0)