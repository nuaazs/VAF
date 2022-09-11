# coding = utf-8
# @Time    : 2022-09-05  15:06:29
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Query in SQL.

import re
import pymysql
import time

import cfg

msg_db = cfg.MYSQL


def get_span(time2,time1):
    time2 = time.strptime(time2,"%Y-%m-%d %H:%M:%S")
    time1 = time.strptime(time1,"%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time2)-time.mktime(time1))

def check_url(url):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    while True:
        try:
            cur = conn.cursor()
            query_sql = f"SELECT * FROM speaker WHERE file_url='{url}';"
            cur.execute(query_sql)
            res = cur.fetchall()
            if len(res) != 0:
                conn.close()
                return True
            else:
                conn.close()
                return False
        except Exception as error:
            conn.ping(True)
    
def check_spkid(spkid):
    while True:
        try:
            cur = conn.cursor()
            query_sql = f"SELECT * FROM speaker WHERE phone='{spkid}';"
            cur.execute(query_sql)
            res = cur.fetchall()
            if len(res) != 0:
                return True
            else:
                return False
        except Exception as error:
            conn.ping(True)

def to_log(phone,action_type, err_type, message,file_url,show_phone,preprocessed_file_path="",valid_length=0):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    # todo 添加showphone
    conn.ping(reconnect=True)
    cur = conn.cursor()
    

    date_num = int(time.strftime("%d", time.localtime()))

    query_sql = f"INSERT INTO log_{date_num} (phone,show_phone,action_type,time,err_type, message,file_url,preprocessed_file_url) VALUES ('{phone}','{show_phone}','{action_type}', curtime(),'{err_type}', '{message}','{file_url}','{preprocessed_file_path}');"
    print(query_sql)
    cur.execute(query_sql)
    conn.commit()
    conn.close()
 

def add_hit(hit_info,is_grey):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    phone = hit_info["phone"]
    show_phone = hit_info["show_phone"]
    file_url = hit_info["file_url"]
    #
    province = hit_info["province"]
    city = hit_info["city"]
    phone_type = hit_info["phone_type"]
    area_code = hit_info["area_code"]
    zip_code = hit_info["zip_code"]
    self_test_score_mean = hit_info["self_test_score_mean"]
    self_test_score_min = hit_info["self_test_score_min"]
    self_test_score_max = hit_info["self_test_score_max"]
    call_begintime = hit_info["call_begintime"]
    call_endtime = hit_info["call_endtime"]
    valid_length =  get_span(call_endtime,call_begintime)
    class_number = hit_info["class_number"]
    hit_time = hit_info["hit_time"]
    blackbase_phone = hit_info["blackbase_phone"]
    blackbase_id = hit_info["blackbase_id"]
    top_10 = hit_info["top_10"]
    # 1~10
    hit_status = hit_info["hit_status"]
    hit_score = hit_info["hit_scores"]
    preprocessed_file_path = hit_info["preprocessed_file_path"]
    if is_grey:
        is_grey = 1
    else:
        is_grey = 0
    cur = conn.cursor()
    query_sql = f"INSERT INTO hit (phone, file_url, phone_type,area_code,\
                    self_test_score_mean,self_test_score_min,self_test_score_max,call_begintime,\
                    call_endtime,valid_length,class_number,blackbase_phone,blackbase_id,top_10,hit_status,hit_score,preprocessed_file_url,is_grey,show_phone,hit_time) \
                        VALUES ('{phone}', '{file_url}','{phone_type}','{area_code}',\
                    '{self_test_score_mean}','{self_test_score_min}','{self_test_score_max}','{call_begintime}',\
                    '{call_endtime}','{valid_length}','{class_number}','{blackbase_phone}','{blackbase_id}','{top_10}',\
                    '{hit_status}','{hit_score}','{preprocessed_file_path}','{is_grey}','{show_phone}',NOW());"
    cur.execute(query_sql)
    conn.commit()
    conn.close()
def add_speaker(spk_info):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    name = spk_info["name"]
    phone = spk_info["phone"]
    file_url = spk_info["uuid"]
    register_time = spk_info["register_time"]
    province = spk_info["province"]
    city = spk_info["city"]
    phone_type = spk_info["phone_type"]
    area_code = spk_info["area_code"]
    zip_code = spk_info["zip_code"]
    self_test_score_mean = spk_info["self_test_score_mean"]
    self_test_score_min = spk_info["self_test_score_min"]
    self_test_score_max = spk_info["self_test_score_max"]
    call_begintime = spk_info["call_begintime"]
    call_endtime = spk_info["call_endtime"]
    class_number = spk_info["max_class_index"]
    preprocessed_file_path = spk_info["preprocessed_file_path"]
    show_phone = spk_info["show_phone"]
    valid_length =  get_span(call_endtime,call_begintime)
    cur = conn.cursor()
    query_sql = f"INSERT INTO speaker (name,phone, file_url,phone_type,area_code,\
                    self_test_score_mean,self_test_score_min,self_test_score_max,call_begintime,\
                    call_endtime,valid_length,class_number,preprocessed_file_url,show_phone,register_time) \
                        VALUES ('{name}','{phone}', '{file_url}', '{phone_type}','{area_code}',\
                    '{self_test_score_mean}','{self_test_score_min}','{self_test_score_max}','{call_begintime}',\
                    '{call_endtime}','{valid_length}','{class_number}','{preprocessed_file_path}','{show_phone}',NOW());"
    print(query_sql)
    cur.execute(query_sql)
    conn.commit()
    conn.close()

def add_hit_count(spk_id):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()
    query_sql = f"update speaker set hit_count = hit_count + 1 where phone='{spk_id}' limit 1;"
    cur.execute(query_sql)
    conn.commit()
    conn.close()


def get_blackid(blackbase_phone):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()
    query_sql = f"select id from speaker where phone='{blackbase_phone}' limit 1;"
    print(query_sql)
    cur.execute(query_sql)
    result = cur.fetchall()
    print(result)
    if len(result)>0:
        conn.close()
        return result[0]["id"]
    else:
        conn.close()
        return 0
    
