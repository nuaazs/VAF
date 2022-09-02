# @Time    : 2022-07-27  18:56:26
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/orm.py
# @Describe: Flask orm.

import time

def init_info(db,Info):
    date = time.strftime("%Y%m%d",time.localtime(time.time()))
    for res in Info.query.filter_by(date=date).all():
        db.session.delete(res)
    db.session.commit()
    info=Info()
    info.date=date
    db.session.add(info)
    db.session.commit()
    return 'Ok'

def add_test(db,Info):
    print("# add test")
    date = time.strftime("%Y%m%d",time.localtime(time.time()))
    if len(Info.query.filter_by(date=date).all()) == 0:
        init_info(db,Info)
        print("# 自动init")
    res = Info.query.filter_by(date=date).first()
    res.test += 1
    db.session.commit()

def add_register(db,Info):
    print("# add register")
    date = time.strftime("%Y%m%d",time.localtime(time.time()))
    if len(Info.query.filter_by(date=date).all()) == 0:
        init_info(db,Info)
        print("# 自动init")
    res = Info.query.filter_by(date=date).first()
    res.register += 1
    db.session.commit()

def add_self_test(db,Info):
    print("# add self test")
    date = time.strftime("%Y%m%d",time.localtime(time.time()))
    if len(Info.query.filter_by(date=date).all()) == 0:
        init_info(db,Info)
        print("# 自动init")
    res = Info.query.filter_by(date=date).first()
    res.self_test += 1
    db.session.commit()

def add_hit(db,Info):
    print("# add hit")
    date = time.strftime("%Y%m%d",time.localtime(time.time()))
    if len(Info.query.filter_by(date=date).all()) == 0:
        init_info(db,Info)
        print("# 自动init")
    res = Info.query.filter_by(date=date).first()
    res.hit += 1
    db.session.commit()

def add_right(db,Info):
    print("# add right")
    date = time.strftime("%Y%m%d",time.localtime(time.time()))
    if len(Info.query.filter_by(date=date).all()) == 0:
        init_info(db,Info)
        print("# 自动init")
    res = Info.query.filter_by(date=date).first()
    res.right += 1
    db.session.commit()

def add_error(type,error_type,db,Info):
    column = f"{type}_error_{error_type}"
    print("# add error")
    date = time.strftime("%Y%m%d",time.localtime(time.time()))
    if len(Info.query.filter_by(date=date).all()) == 0:
        init_info(db,Info)
        print("# 自动init")
    res = Info.query.filter_by(date=date).first()
    if type == "test":
        if error_type == 1:
            res.test_error_1 += 1
        if error_type == 2:
            res.test_error_2 += 1
    else:
        if error_type == 1:
            res.register_error_1 += 1
        if error_type == 2:
            res.register_error_2 += 1
    db.session.commit()

def get_span(time2,time1):
    time2 = time.strptime(time2,"%Y-%m-%d %H:%M:%S")
    time1 = time.strptime(time1,"%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time2)-time.mktime(time1))
def add_hit_log(hit_info,db,Hit,preprocessed_file_path="",is_grey=False):
    info = Hit()
    info.phone = hit_info["phone"]
    info.file_url = hit_info["file_url"]
    
    #
    info.province = hit_info["province"]
    info.city = hit_info["city"]
    info.phone_type = hit_info["phone_type"]
    info.area_code = hit_info["area_code"]
    info.zip_code = hit_info["zip_code"]
    info.self_test_score_mean = hit_info["self_test_score_mean"]
    info.self_test_score_min = hit_info["self_test_score_min"]
    info.self_test_score_max = hit_info["self_test_score_max"]
    info.call_begintime = hit_info["call_begintime"]
    info.call_endtime = hit_info["call_endtime"]
    info.span_time =  get_span(info.call_endtime,info.call_begintime)
    info.class_number = hit_info["class_number"]
    info.hit_time = hit_info["hit_time"]
    info.blackbase_phone = hit_info["blackbase_phone"]
    info.blackbase_id = hit_info["blackbase_id"]
    info.top_10 = hit_info["top_10"]
    # 1~10
    info.hit_status = hit_info["hit_status"]
    info.hit_score = hit_info["hit_scores"]
    if is_grey:
        info.is_grey = 1
    else:
        info.is_grey = 0
    info.preprocessed_file_url = preprocessed_file_path
    db.session.add(info)
    db.session.commit()

def add_speaker(spk_info,db,Speaker,preprocessed_file_path=""):
    info=Speaker()
    info.name = spk_info["name"]
    info.phone = spk_info["phone"]
    info.file_url = spk_info["uuid"]
    info.register_time = spk_info["register_time"]
    info.province = spk_info["province"]
    info.city = spk_info["city"]
    info.phone_type = spk_info["phone_type"]
    info.area_code = spk_info["area_code"]
    info.zip_code = spk_info["zip_code"]
    info.self_test_score_mean = spk_info["self_test_score_mean"]
    info.self_test_score_min = spk_info["self_test_score_min"]
    info.self_test_score_max = spk_info["self_test_score_max"]
    info.call_begintime = spk_info["call_begintime"]
    info.call_endtime = spk_info["call_endtime"]
    info.class_number = spk_info["max_class_index"]
    info.preprocessed_file_url = preprocessed_file_path
    info.span_time =  get_span(info.call_endtime,info.call_begintime)
    db.session.add(info)
    db.session.commit()

def delete_in_speaker(spk_info,db,Speaker,preprocessed_file_path=""):
    info=Speaker()
    info.name = spk_info["name"]
    info.phone = spk_info["phone"]
    info.file_url = spk_info["uuid"]
    info.register_time = spk_info["register_time"]
    info.province = spk_info["province"]
    info.city = spk_info["city"]
    info.phone_type = spk_info["phone_type"]
    info.area_code = spk_info["area_code"]
    info.zip_code = spk_info["zip_code"]
    info.self_test_score_mean = spk_info["self_test_score_mean"]
    info.self_test_score_min = spk_info["self_test_score_min"]
    info.self_test_score_max = spk_info["self_test_score_max"]
    info.call_begintime = spk_info["call_begintime"]
    info.call_endtime = spk_info["call_endtime"]
    info.class_number = spk_info["max_class_index"]
    info.preprocessed_file_url = preprocessed_file_path
    info.span_time =  get_span(info.call_endtime,info.call_begintime)
    db.session.add(info)
    db.session.commit()

def add_log(log_info,db,Log):
    log = Log()
    log.hit_time = log_info["hit_time"]
    log.phone = log_info["phone"]
    log.province = log_info["province"]
    log.city = log_info["city"]
    log.phone_type = log_info["phone_type"]
    db.session.add(log)
    db.session.commit()
    