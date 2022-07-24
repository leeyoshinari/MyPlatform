#!/bin/sh
ps -ef|grep daphne |grep -v grep |awk '{print $2}' |xargs kill -9
echo "stop success ~"