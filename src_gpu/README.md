# GPU Version
cuda版本 11.4


log : 日志目录
nn  : 预训练模型保存目录
utils : 工具函数
templates : 测试页面
cfg.py : 项目配置
gunicorn.py : gunicorn配置
main.py : 项目入口
requirements.txt : 项目依赖


## 启动方式一
```shell
gunicorn -c gunicorn.py si_server_gpu:app
```
## 启动方式二
```shell
python si_server_gpu.py
```