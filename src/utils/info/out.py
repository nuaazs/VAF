from utils.log import err_logger

class OutInfo:
    """
    out dict info
    """

    used_time = {
        "download_used_time": 0,
        "vad_used_time": 0,
        "classify_used_time": 0,
        "embedding_used_time": 0,
        "self_test_used_time": 0,
        "to_database_used_time": 0,
        "test_used_time": 0,
    }

    def __init__(self):
        self.response = {"code": 2000, "status": "error"}
        self.response_check_new = {
            "code": 2000,
            "status": "error",
            "err_type": "None",
            "err_msg": "None",
            "inbase": True,
            "code": 2000,
            "replace": False,
        }

    def response_error(self, spkid, err_type, err_msg, used_time=None, oss_path="None"):
        err_logger.info("%s, %s, %s, %s" % (spkid, oss_path, err_type, err_msg))
        self.response["err_type"] = err_type
        self.response["err_msg"] = err_msg
        if used_time != None:
            self.response["used_time"] = used_time
        return self.response

    def response_vad(self, err_type, err_msg, used_time=None):
        self.response["err_type"] = err_type
        self.response["err_msg"] = err_msg
        if used_time != None:
            self.response["used_time"] = used_time
        return self.response

    def response_check(self, err_type, err_msg):
        self.response_check_new["err_type"] = err_type
        self.response_check_new["err_msg"] = err_msg
        return self.response

