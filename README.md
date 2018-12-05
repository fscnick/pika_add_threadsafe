# Pika add_callback_threadsafe test

Test one connection and multiple channels with Pika. Related issue [Using one connection and multiple channels to receive and send messages](https://github.com/pika/pika/issues/699)

## Usage

Run rabbitmq: `./scripts/run_rabbitmq.sh`

Run python script `src/main.py` directly. Or build docker `./scripts/build_python.sh` and `./scripts/run_python.sh`.

## Issue

* Encounter `RuntimeError: can't start new thread` when processing 100000 messages with `no_ack` is `False`. But processing 80000 messages works fine.