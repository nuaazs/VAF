# 上传
import os
from oss.oss_tool import OSS

def minio_set_object():
    pwd = os.getcwd()
    oss = OSS("gray")
    PATH_D = os.path.join(pwd, "data/gray/")
    file = os.listdir(PATH_D)
    for i in file:
        print(i)
        file_path = os.path.join(PATH_D, i)
        oss.upload_file("gray", file_path, i)

    oss = OSS("black")
    PATH_D = os.path.join(pwd, "data/black/")
    file = os.listdir(PATH_D)
    for i in file:
        print(i)
        file_path = os.path.join(PATH_D, i)
        oss.upload_file("black", file_path, i)


if __name__ == "__main__":
    # 上传
    minio_set_object()
