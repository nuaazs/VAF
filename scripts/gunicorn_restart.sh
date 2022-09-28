#!/bin/bash
cd ../src
rm -rf ./log/*
./scripts/stop.sh
./scripts/start.sh &