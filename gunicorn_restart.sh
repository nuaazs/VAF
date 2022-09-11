#!/bin/bash
cd ./src_cpu
./scripts/stop.sh
./scripts/start.sh &
cd ../src_gpu
./scripts/stop.sh
./scripts/start.sh &