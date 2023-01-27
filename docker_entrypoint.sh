#!/bin/bash

set -e

exec python3 ngrok_script.py &
exec python3 aio_ex.py 