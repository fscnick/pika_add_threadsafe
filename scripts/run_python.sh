#!/bin/bash

count=$1
if [ "x$count" = "x" ];then
    count=1000
fi

docker run -it --rm pika_test:latest python /app/main.py -c $count