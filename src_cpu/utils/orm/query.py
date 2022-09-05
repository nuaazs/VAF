# @Time    : 2022-07-27  19:02:00
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/query.py
# @Describe: Query info in Mysql.

import pymysql
import cfg
msg_db = cfg.MYSQL

def check_url(url):
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

def check_spkid(spkid):
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

def to_log(phone, action_type, err_type, message,file_url,preprocessed_file_path="",valid_length=0):
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

def add_hit():
    pass
def add_hit(spk_id):
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
