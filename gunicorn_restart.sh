#!/bin/bash
cd ./src_cpu
rm -rf ./log/*
./scripts/stop.sh
./scripts/start.sh &
cd ../src_gpu
rm -rf ./log/*
./scripts/stop.sh
./scripts/start.sh &