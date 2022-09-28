FROM si_clean:v1.3.3

# FROM python:3.8
WORKDIR /VAF-System/src
ENV timezone Asia/Shanghai
# RUN  sed -i 's/ports.ubuntu.com/mirror.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
# RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
# RUN  sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
# RUN  apt-get clean
# COPY ../deploy/src /VAF-System/src
COPY ./start.sh /VAF-System
COPY ./src /VAF-System/src

COPY requirements.txt /VAF-System
# RUN apt-get update -y
# RUN apt-get install -y --no-install-recommends build-essential gcc vim libsndfile1 fzf tmux screen ffmpeg
RUN apt-get install -y --no-install-recommends nginx htop zip
RUN pip install -r ../requirements.txt 
#-i https://pypi.tuna.tsinghua.edu.cn/simple
RUN chmod +x -R /VAF-System/*
ENTRYPOINT ["/bin/bash", "/VAF-System/start.sh"]