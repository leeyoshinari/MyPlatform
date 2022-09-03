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
        if task.status > 0:
            return web.json_response({'code': 1, 'msg': f'Host {task.IP} is busy ~', 'data': None})
        data = await request.json()
        task_id = data.get('taskId')
        # plan_id = data.get('planId')
        agent_num = data.get('agentNum')
        file_path = data.get('filePath')
        is_debug = data.get('isDebug')
        task.start_thread(task.run_task, (task_id, file_path, agent_num, is_debug,))
        return web.json_response({'code': 0, 'msg': '', 'data': None})
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
    res = task.download_log(task_id)
    return web.Response(content_type='application/octet-stream',
                        headers={'Content-Disposition': f'attachment;filename={task_id}.zip'},
                        body=res)


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
        task.start_thread(task.stop_task, (task_id,))
        logger.info('Stop the Task successfully!')
        return web.json_response({'code': 0, 'msg': 'Stop the Task successfully', 'data': None})
    except:
        logger.error(traceback.format_exc())
        return web.json_response({'code': 1, 'msg': 'Stop the Task failure', 'data': None})


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
