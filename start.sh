cd ./src
gunicorn -c gunicorn.py vaf_server:app