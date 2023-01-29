<<<<<<< HEAD
# coding = utf-8
# @Time    : 2022-09-05  09:46:15
# @Author  : zhaosheng@nuaa.edu.cn
# @Describe: Gunicorn config file.

=======
# Email: zhaosheng@nuaa.edu.cn
# Time  : 2022-05-06  22:28:08
# Desc  : gunicorn config file
>>>>>>> aaf98c0f80d54045f84fd2aed04556c602508d9f
import cfg

workers = cfg.WORKERS
threads = cfg.THREADS
bind = f"0.0.0.0:{cfg.PORT}"
<<<<<<< HEAD
daemon = "false"
=======
daemon = 'false'
>>>>>>> aaf98c0f80d54045f84fd2aed04556c602508d9f
worker_class = "gevent"
worker_connections = cfg.WORKER_CONNECTIONS
pidfile = "./log/gunicorn.pid"
accesslog = "./log/gunicorn_access.log"
errorlog = "./log/gunicorn_error.log"
loglevel = "info"
