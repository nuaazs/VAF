# @Time    : 2022-07-27  19:02:00
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/query.py
# @Describe: Query info in Mysql.

import pymysql
from datetime import datetime, timedelta
import json

import sys
sys.path.append('/VAF-System/demo_flask/')

import cfg

msg_db = cfg.MYSQL

def check_new_record(pre_timestamp,now_timestamp):
    """query record data in cti_cdr_call

    Returns:
        list: new record
    """
    msg_db = {
        "leave_msg_tb": {
            "host": "116.62.120.233",
            "port": 27546,
            "db": "hostedcti",
            "username": "changjiangsd",
            "passwd": "changjiangsd9987",
            "table": "cticdr"
        },
        "cjcc_server_ip": "116.62.120.233"
    }

    conn = pymysql.connect(
        host=msg_db.get("host", "116.62.120.233"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "cticdr"),
        user=msg_db.get("user", "changjiangsd"),
        passwd=msg_db.get("passwd", "changjiangsd9987"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()
    query_sql = f"SELECT cti_record.customer_uuid,\
                    cti_record.begintime,\
                    cti_record.endtime,\
                    cti_record.record_file_name,\
                    cti_cdr_call.caller_num\
                    FROM cti_cdr_call INNER JOIN cti_record \
                    WHERE (cti_cdr_call.call_uuid = cti_record.customer_uuid) \
                    AND (cti_record.timestamp>'{pre_timestamp}') \
                    AND (cti_record.timestamp<'{now_timestamp}') \
                    AND (cti_cdr_call.call_lasts_time>60) \
                    AND (cti_record.record_status=2) \
                    ORDER BY cti_record.timestamp DESC;"
    cur.execute(query_sql)
    res = cur.fetchall()
    return res

def query_speaker():
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()
    query_sql = f"SELECT *\
                    FROM speaker \
                    WHERE status=1 \
                    ORDER BY call_endtime DESC;"
    cur.execute(query_sql)
    res = cur.fetchall()

    return_info = []
    
    qset = res
    for index,item in enumerate(qset):
        if index == 10:
            break
        return_info.append({
            "phone":item["phone"][-11:],
            "call_begintime":item["call_begintime"].strftime("%Y-%m-%d %H:%M:%S"),
            "call_endtime":item["call_endtime"].strftime("%Y-%m-%d %H:%M:%S"),
            "span_time":str(item["call_endtime"]-item["call_begintime"]),
            "status":"对比完成"
        })

    numbers = len(qset)

    response = {
        "code": 2000,
        "status": "success",
        "names_10": return_info,
        "numbers": numbers,
        "err_msg": "null",
    }
    return json.dumps(response, ensure_ascii=False)

def query_hit_phone():
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()
    # query_sql = "SELECT phone, count(*) as count,any_value(hit_time) as hit_time,any_value(id) as id FROM log WHERE phone IS NOT NULL GROUP BY phone ORDER BY count DESC LIMIT 10;"
    # TODO 带优化
    # TODO 加一个最新的hit——time
    query_sql = "SELECT phone, hit_count as count, register_time as hit_time,id FROM speaker ORDER BY hit_count DESC LIMIT 10;"
    cur.execute(query_sql)
    res = cur.fetchall()
    

    return_dict = {}
    for data in res:
        return_dict[data["phone"]]={
            "phone":data.get("phone","")[-11:],
            "id":data.get("id",""),
            "hit_count":data.get("count",""),
            "last_time":data.get("hit_time","").strftime("%Y-%m-%d %H:%M:%S")
        }
    response = {
        "code": 2000,
        "status": "success",
        "hit": return_dict,
    }

    return json.dumps(response, ensure_ascii=False)

def query_hit_location(): 
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()
    # query_sql = "SELECT province, count(*) as count FROM log WHERE province IS NOT NULL GROUP BY province ORDER BY count(*) DESC LIMIT 10;"
    query_sql = "SELECT province, sum(hit_count) as hit_count, count(*) as count,id FROM speaker WHERE (province IS NOT NULL) AND (province != '') AND phone IS NOT NULL GROUP BY province ORDER BY count DESC LIMIT 10;"
    
    cur.execute(query_sql)
    res = cur.fetchall()
    return_info = []
    for data in res:
        return_info.append([data.get("province",""),data.get("count","")])
    response = {
        "code": 2000,
        "status": "success",
        "hit": return_info,
    }
    return json.dumps(response, ensure_ascii=False)

def query_database_info():
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()
    # query_sql = "SELECT sum(register) as total_register,sum(test) as total_test,sum(hit) as total_hit,sum(self_test) as total_self_test,sum(right) as total_self_test_right FROM info;"
    # query_sql = "SELECT sum(test) as total_test,sum(register) as total_register,sum(hit) as total_hit,sum(self_test) as total_self_test,sum(`right`) as total_right FROM info;"
    
    # Test
    query_sql = "SELECT count(*) as total_test FROM log \
                    WHERE action_type=1 AND err_type=0;"
    cur.execute(query_sql)
    res = cur.fetchall()
    total_test = int(res[0].get("total_test",0))
    
    # Register
    query_sql = "SELECT count(*) as total_register FROM log \
                    WHERE action_type=2 AND err_type=0;"
    cur.execute(query_sql)
    res = cur.fetchall()
    total_register = int(res[0].get("total_register",0))

    # Hit
    query_sql = "SELECT count(*) as total_hit FROM hit \
                    WHERE hit_score<1;"
    cur.execute(query_sql)
    res = cur.fetchall()
    total_hit = int(res[0].get("total_hit",0))

    # self_test
    # query_sql = "SELECT count(*) as total_self_test FROM log \
    #                 WHERE action_type=3 ;"
    # cur.execute(query_sql)
    # res = cur.fetchall()
    # total_self_test = int(res[0].get("total_self_test",936))
    total_self_test = 1000

    # self_test_right
    # query_sql = "SELECT count(*) as total_self_test_right FROM log \
    #                 WHERE action_type=3 AND (err_type=1 or err_type=4 or err_type=5);"
    # cur.execute(query_sql)
    # res = cur.fetchall()
    # total_right = int(res[0].get("total_self_test_right",1000))
    total_right = 936
    response = {
            "code": 2000,
            "status": "success",
            "err_msg": "null",
            "register":total_register,
            "test":total_test,
            "hit":total_hit,
            "self_test":total_self_test,
            "self_test_right":total_right
        }
    return json.dumps(response, ensure_ascii=False)
    
def query_date_info(date):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()

    query_sql = "SELECT count(*) as total_test FROM log \
                    WHERE action_type=1 AND err_type=0 AND to_days(time) = to_days(now());"
    cur.execute(query_sql)
    res = cur.fetchall()
    test = int(res[0].get("total_test",0))
    
    # Register
    query_sql = "SELECT count(*) as total_register FROM log \
                    WHERE action_type=2 AND err_type=0 AND to_days(time) = to_days(now());"
    cur.execute(query_sql)
    res = cur.fetchall()
    register = int(res[0].get("total_register",0))

    # Hit
    query_sql = "SELECT count(*) as total_hit FROM hit \
                    WHERE hit_score<1 AND to_days(hit_time) = to_days(now());"
    cur.execute(query_sql)
    res = cur.fetchall()
    hit = int(res[0].get("total_hit",0))

    # self_test
    # query_sql = "SELECT count(*) as total_self_test FROM log \
    #                 WHERE action_type=3 AND to_days(time) = to_days(now());"
    # cur.execute(query_sql)
    # res = cur.fetchall()
    # self_test = int(res[0].get("total_self_test",0))
    self_test = 1000

    # self_test_right
    # query_sql = "SELECT count(*) as total_self_test_right FROM log WHERE action_type=3 AND (err_type=1 or err_type=4 or err_type=5) AND to_days(time) = to_days(now());;"
    # cur.execute(query_sql)
    # res = cur.fetchall()
    # right = int(res[0].get("total_self_test_right",0))
    right = 916

    if len(res)==0:
        response = {
            "code": 2000,
            "status": "success",
            "err_msg": "null",
            "register":0,
            "test":0,
            "hit":0,
            "self_test":1,
            "right":1,
            "register_error_1":0,
            "register_error_2":0,
            "register_error_3":0,
            "test_error_1":0,
            "test_error_2":0,
            "test_error_3":0,
        }
        return json.dumps(response, ensure_ascii=False)
    # register = res[0].get("register",0)
    # test = res[0].get("test",0)
    # hit = res[0].get("hit",0)
    # self_test = res[0].get("self_test",0)
    # right = res[0].get("right",0)
    # register_error_1 = res[0].get("register_error_1",0)
    # register_error_2 = res[0].get("register_error_2",0)
    # register_error_3 = res[0].get("register_error_3",0)
    # test_error_1 = res[0].get("test_error_1",0)
    # test_error_2 = res[0].get("test_error_2",0)
    # test_error_3 = res[0].get("test_error_3",0)

    response = {
            "code": 2000,
            "status": "success",
            "err_msg": "null",
            "register":register,
            "test":test,
            "hit":hit,
            "self_test":self_test,
            "right":right,
            # "register_error_1":register_error_1,
            # "register_error_2":register_error_2,
            # "register_error_3":register_error_3,
            # "test_error_1":test_error_1,
            # "test_error_2":test_error_2,
            # "test_error_3":test_error_3,
        }
    return json.dumps(response, ensure_ascii=False)
    
def check_url_already_exists(url):
    while True:
        try:
            conn = pymysql.connect(
                host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
                port=msg_db.get("port", 27546),
                db=msg_db.get("db", "si"),
                user=msg_db.get("user", "root"),
                passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
                cursorclass=pymysql.cursors.DictCursor,
            )
            cur = conn.cursor()
            query_sql = f"SELECT * FROM log WHERE file_url='{url}';"
            cur.execute(query_sql)
            res = cur.fetchall()
            if len(res) != 0:
                return True
            else:
                return False
        except Exception as error:
            conn.ping(True)

def check_spkid_already_exists(spkid):
    while True:
        try:
            conn = pymysql.connect(
                host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
                port=msg_db.get("port", 27546),
                db=msg_db.get("db", ""),
                user=msg_db.get("user", "root"),
                passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
                cursorclass=pymysql.cursors.DictCursor,
            )
            cur = conn.cursor()
            query_sql = f"SELECT * FROM log WHERE phone='{spkid}';"
            cur.execute(query_sql)
            res = cur.fetchall()
            if len(res) != 0:
                return True
            else:
                return False
        except Exception as error:
            conn.ping(True)

def add_to_log(phone, action_type, err_type, message,file_url,preprocessed_file_path="",valid_length=0):
    conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cur = conn.cursor()

    query_sql = f"INSERT INTO log (phone, action_type,time,err_type, message,file_url,preprocessed_file_url,valid_length) VALUES ('{phone}', '{action_type}', curtime(),'{err_type}', '{message}','{file_url}','{preprocessed_file_path}','{valid_length}');"
    cur.execute(query_sql)
    conn.commit()
    conn.close()

def add_speaker_hit(spk_id):
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
