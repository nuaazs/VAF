# Email: zhaosheng@nuaa.edu.cn
# Time  : 2022-05-06  22:28:08
# Desc  : gunicorn config file
import cfg

workers = cfg.WORKERS
threads = cfg.THREADS
bind = f"0.0.0.0:{cfg.PORT}"
daemon = 'false'
worker_class = "gevent"
worker_connections = cfg.WORKER_CONNECTIONS
pidfile = "./log/gunicorn.pid"
accesslog = "./log/gunicorn_access.log"
errorlog = "./log/gunicorn_error.log"
loglevel = "info"
