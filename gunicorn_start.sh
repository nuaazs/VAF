#!/bin/bash
cd ./src_cpu
./scripts/start.sh &
cd ../src_gpu
./scripts/start.sh &