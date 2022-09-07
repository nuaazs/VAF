#/bin/bash
gunicorn -c gunicorn.py si_server:app
