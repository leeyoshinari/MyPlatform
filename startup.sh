#!/usr/bin/sh
blind = 127.0.0.1
port = 8000
nohup daphne MyPlatform.asgi:application -b ${blind} -p ${port} > /dev/null 2>&1 &
echo "start server success ~"
