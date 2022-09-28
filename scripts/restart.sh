#!/bin/bash
docker rm -f si
rm -rf ./src/log/*
touch ./src/log/gunicorn_error.log
docker run --name si -v ${PWD}/cfg.py:/VAF-System/src/cfg.py\
                     -v ${PWD}/src/log:/VAF-System/src/log\
                     -v ${PWD}/register:/VAF-System/register\
                     -p 8180:8180\
                     -p 8083:8083\
                     -p 8292:8292\
                     -p 8291:8291\
                     --restart "always"\
                     si:v1.5.1
