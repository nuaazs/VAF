#/bin/bash
gunicorn -c gunicorn.py server:app
