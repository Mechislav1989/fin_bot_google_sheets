#!/bin/bash

set -e

exec python3 ngrok_script.py &
sleep $WORKER_SLEEP 5
exec python3 aio_ex.py 