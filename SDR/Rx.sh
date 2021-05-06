#!/bin/bash


source ~/PlutoSDR/SDRenv/setup_env.sh

printf "%s" "waiting for ServerXY ..."
while ! timeout 0.2 ping -c 1 -n 10.0.0.2 &> /dev/null
do
    printf "%c" "."
done
printf "\n%s\n"  "Server is back online"

python ~/DDS/SDR/Rx.py
