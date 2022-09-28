import time
import os


class ARGS:
    ip = "127.0.0.1"
    # 端口
    port = "8187"
    # 方式  default： test | register
    path = "test"
    # default： url | file
    mode = "url"
    # 间隔时间
    time = 1
    # 文件获取方式
    pattern = "rclone"
    # 黑库桶名
    buckets_name_black = "check"
    # 本地黑库文件夹路径[日期目录]
    wav_path_black = "/mnt/panjiawei/date"
    # 灰库桶名
    buckets_name_gray = "check"
    # 本地灰库文件夹路径[日期目录]
    wav_path_gray = "/mnt/panjiawei/date"
    # 本地linux的minio名称 -> 可在linux上面的 ~/.config/rclone/rclone.conf 文件中查看
    rclone_name = "minio"

    url_register = r"http://{0}:{1}/{2}/{3}".format(ip, port, "register", mode)
    url_test = r"http://{0}:{1}/{2}/{3}".format(ip, port, "test", mode)


def rclone_join(pattern, file_path, buckets_name):
    if pattern == "copy":
        return "rclone copy %s %s:/%s/%s" % (
            file_path,
            ARGS.rclone_name,
            buckets_name,
            file_path.split("/")[-1],
        )


def file_synchronization(all_size, info, buckets_name, wav_path):
    """
    all_size:
        All file size
    info:
        Each information
    buckets_name: 
        buckets name
    wav_path:
        wav file path
    """
    with os.popen("du -c %s/*" % (wav_path)) as f1:
        data_new = f1.read().strip().split("\n")
    dict_new = {}
    all_new, _ = data_new[-1].split("\t")

    if all_new != all_size:
        for file in data_new:
            size, name = file.split("\t")
            if name == "总用量":
                continue
            dict_new[name] = size

        if len(info) == len(dict_new) or len(info) != len(dict_new):
            for value in dict_new.keys():
                if dict_new.get(value) == info.get(value):
                    continue
                # os.system(rclone_join("copy", value, buckets_name))
                print(rclone_join("copy", value, buckets_name))
    return all_new


def get_file(wav_path):
    """
    wav_path:
        /mnt/panjiawei/date/2022-9-21/ acquire fil date
    """
    with os.popen("du -c %s/*" % (wav_path)) as f1:
        data_outdated = f1.read().strip().split("\n")
    dict_black = {}
    all_size, _ = data_outdated[-1].split("\t")
    for file in data_outdated:
        size, name = file.split("\t")
        if name == "总用量":
            continue
        dict_black[name] = size
    return all_size, dict_black


def run():
    """
    file synchronization
    """
    wav_path_black = ARGS.wav_path_black
    buckets_name_black = ARGS.buckets_name_black
    all_black_size_outdated, dict_black_outdated = get_file(wav_path_black)

    wav_path_gray = ARGS.wav_path_gray
    buckets_name_gray = ARGS.buckets_name_gray
    all_gray_size_outdated, dict_gray_outdated = get_file(wav_path_gray)

    while True:
        time.sleep(ARGS.time)
        all_black_size_outdated = file_synchronization(
            all_black_size_outdated,
            dict_black_outdated,
            buckets_name_black,
            wav_path_black,
        )
        all_gray_size_outdated = file_synchronization(
            all_gray_size_outdated, dict_gray_outdated, buckets_name_gray, wav_path_gray
        )


if __name__ == "__main__":
    run()
