# @Time    : 2022-07-27  18:57:54
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/phone_util.py
# @Describe: Get phone info.

from phone import Phone

def getPhoneInfo(phoneNum):
    info = Phone().find(phoneNum)
    if info == None:
        return {}
    return info