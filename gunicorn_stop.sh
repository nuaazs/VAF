#!/bin/bash
cd ./src_cpu
./scripts/stop.sh &
cd ../src_gpu
./scripts/stop.sh &