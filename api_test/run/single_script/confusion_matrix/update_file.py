# 上传
def minio_set_object():
    oss = OSS("gray")
    PATH_D = "/mnt/panjiawei/run_2/data/gray"
    file = os.listdir(PATH_D)
    for i in file:
        print(i)
        file_path = os.path.join(PATH_D, i)
        oss.upload_file("gray", file_path, i)
    
    oss = OSS("black")
    PATH_D = "/mnt/panjiawei/run_2/data/black"
    file = os.listdir(PATH_D)
    for i in file:
        print(i)
        file_path = os.path.join(PATH_D, i)
        oss.upload_file("black", file_path, i)

if __name__ == "__main__":
    # 上传
    minio_set_object()