# Voice print recognition system (Speaker identification system)
声纹识别系统后台 (CPU版-src_cpu)
声纹识别系统后台 (CUDA版-src_gpu)

## Requirements
1. Mysql 5.7
2. Docker 20.10.12
3. redis 5.0.7
4. Minio
5. Python 3.8

## Files
```shell

```

## Install

### Database
1. 安装并启动Mysql和Redis服务
Mysql运行脚本`si.sql`，创建表单

2. 在存储服务器上运行minio对象存储服务
```shell
sudo ./minio server <where/to/save/data> --console-address ":9001"
```

3. 修改配置文件
```shell
vim ./src/cfg.py
```

### backend
```shell
sudo docker load -i si_v1_0.tar
sudo docker run --entrypoint="" --name si_server_1_0 -it -p 8180:8180 -v <path/to/VAF-System>:/VAF-System nuaazs/si:v1.0 /bin/bash
```
### docker
```shell
cd ./src
# gunicorn运行
./scripts/start.sh

# python运行
python vvs_service.py
```