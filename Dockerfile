FROM si-gpu:base

ADD . /voiceprint-recognition-system

WORKDIR /voiceprint-recognition-system

ENV timezone Asia/Shanghai

RUN pip install phone -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["/bin/bash", "gunicorn_start.sh"]