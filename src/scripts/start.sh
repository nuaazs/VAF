#/bin/bash
gunicorn -c gunicorn.py si_server_gpu:app
