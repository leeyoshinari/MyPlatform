#!/bin/sh
nohup daphne MyPlatform.asgi:application -b 127.0.0.1 -p 15200 > /dev/null 2>&1 &
echo "start server success ~"
