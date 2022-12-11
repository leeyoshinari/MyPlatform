#!/bin/sh
nohup daphne MyPlatform.asgi:application -b 0.0.0.0 -p 15200 > /dev/null 2>&1 &
echo "start server success ~"
