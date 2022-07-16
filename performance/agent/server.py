#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
import os
import time
import asyncio
import traceback
from aiohttp import web
from common import get_ip, logger, get_config
from taskController import Task

HOST = get_ip()
task = Task()


async def index(request):
    """
    Home, basic data can be displayed by visiting http://ip:port
    :param request:
    :return:
    """
    return web.Response(body=f'The server system version is')


async def run_task(request):
    """
    :param request:
    :return:
    """
    try:
        data = await request.json()
        task_id = data.get('taskId')
        # plan_id = data.get('planId')
        agent_num = data.get('agentNum')
        file_path = data.get('filePath')
        res = task.run_task(task_id, file_path, agent_num)
        res.update({'data': {'taskId': task_id}})
        return web.json_response(res)
    except Exception as err:
        logger.error(traceback.format_exc())
        return web.json_response({'code': 1, 'msg': str(err), 'data': None})


async def download_file(request):
    """
     Get the list of monitoring ports
    :param request:
    :return:
    """
    task_id = request.match_info['task_id']


async def change_tps(request):
    """
    :param request:
    :return:
    """
    try:
        data = await request.json()
        task_id = data.get('taskId')
        tps = data.get('tps')
        res = task.change_TPS(tps)

    except Exception:
        logger.error(traceback.format_exc())


async def stop_task(request):
    try:
        task_id = request.match_info['task_id']
        task.stop_task()
        logger.info('Stop the Task successfully!')
        return web.Response(body='Stop the agent successfully!')
    except:
        logger.error(traceback.format_exc())
        return web.Response(body='Agent is not running!')


async def main():
    app = web.Application()

    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/stopTask/{task_id}', stop_task)
    app.router.add_route('POST', '/runTask', run_task)
    app.router.add_route('POST', '/change', change_tps)
    app.router.add_route('GET', '/download/{task_id}', download_file)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, get_config('port'))
    await site.start()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
