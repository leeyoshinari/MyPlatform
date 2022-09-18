#!/bin/sh
pid=$(ps -ef|grep daphne |grep -v grep |awk '{print $2}' |xargs)
if [ $pid ]; then
	kill -9 $pid
fi
echo "Stop $pid success ~"
