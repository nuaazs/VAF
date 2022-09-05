# @Time    : 2022-07-27  19:02:00
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/query.py
# @Describe: Query info in Mysql.

import pymysql
import cfg
import time


msg_db = cfg.MYSQL
conn = pymysql.connect(
        host=msg_db.get("host", "zhaosheng.mysql.rds.aliyuncs.com"),
        port=msg_db.get("port", 27546),
        db=msg_db.get("db", "si"),
        user=msg_db.get("user", "root"),
        passwd=msg_db.get("passwd", "Nt3380518!zhaosheng123"),
        cursorclass=pymysql.cursors.DictCursor,
    )

def get_span(time2,time1):
    time2 = time.strptime(time2,"%Y-%m-%d %H:%M:%S")
    time1 = time.strptime(time1,"%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time2)-time.mktime(time1))

def check_url(url):
    while True:
        try:
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

def check_spkid(spkid):
    while True:
        try:
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

def to_log(phone, action_type, err_type, message,file_url,preprocessed_file_path="",valid_length=0):
    cur = conn.cursor()
    query_sql = f"INSERT INTO log (phone, action_type,time,err_type, message,file_url,preprocessed_file_url,valid_length) VALUES ('{phone}', '{action_type}', curtime(),'{err_type}', '{message}','{file_url}','{preprocessed_file_path}','{valid_length}');"
    cur.execute(query_sql)
    conn.commit()
 

def add_hit(hit_info,is_grey):
    phone = hit_info["phone"]
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
    span_time =  get_span(info.call_endtime,info.call_begintime)
    class_number = hit_info["class_number"]
    hit_time = hit_info["hit_time"]
    blackbase_phone = hit_info["blackbase_phone"]
    blackbase_id = hit_info["blackbase_id"]
    top_10 = hit_info["top_10"]
    # 1~10
    hit_status = hit_info["hit_status"]
    hit_score = hit_info["hit_scores"]
    if is_grey:
        is_grey = 1
    else:
        is_grey = 0
    cur = conn.cursor()
    query_sql = f"INSERT INTO hit (phone, file_url,province,city, phone_type,area_code,\
                    zip_code,self_test_score_mean,self_test_score_min,self_test_score_max,call_begintime,\
                    call_endtime,span_time,class_number,hit_time,blackbase_phone,blackbase_id,top_10,hit_status,hit_score,is_grey) \
                        VALUES ('{phone}', '{file_url}','{province}','{city}', '{phone_type}','{area_code}',\
                    '{zip_code}','{self_test_score_mean}','{self_test_score_min}','{self_test_score_max}','{call_begintime}',\
                    '{call_endtime}','{span_time}','{class_number}','{hit_time}','{blackbase_phone}','{blackbase_id}','{top_10}',\
                    '{hit_status}','{hit_score}','{is_grey}');"
    cur.execute(query_sql)
    conn.commit()



def add_speaker(spk_info):

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
    
    span_time =  get_span(call_endtime,call_begintime)
    cur = conn.cursor()
    query_sql = f"INSERT INTO hit (name,phone, file_url,province,city, phone_type,area_code,\
                    zip_code,self_test_score_mean,self_test_score_min,self_test_score_max,call_begintime,\
                    call_endtime,span_time,class_number) \
                        VALUES ('{name},'{phone}', '{file_url}','{province}','{city}', '{phone_type}','{area_code}',\
                    '{zip_code}','{self_test_score_mean}','{self_test_score_min}','{self_test_score_max}','{call_begintime}',\
                    '{call_endtime}','{span_time}','{class_number}');"
    print(query_sql)
    cur.execute(query_sql)
    conn.commit()



def add_hit_count(spk_id):
    cur = conn.cursor()
    query_sql = f"update speaker set hit_count = hit_count + 1 where phone='{spk_id}' limit 1;"
    cur.execute(query_sql)
    conn.commit()


if __name__ == "__main__":
    cur = conn.cursor()
    query_sql = f"select * from speaker;"
    cur.execute(query_sql)
    res = cur.fetchall()
    print(res)
    conn.commit()
