#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. >/dev/null && pwd )"
cd $DIR

docker build -f build/Dockerfile -t pika_test .