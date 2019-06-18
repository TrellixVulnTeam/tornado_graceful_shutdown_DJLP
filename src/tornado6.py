# -*- coding: utf-8 -*-
# Created by CaoDa on 2019/6/18 10:25

import signal
import time
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
import asyncio


class CustomizeHTTPServer(HTTPServer):
    async def close_all_connections(self) -> None:
        while self._connections:
            # Peek at an arbitrary element of the set
            conn = next(iter(self._connections))
            while not conn._serving_future.done():
                await gen.sleep(0)
            await conn.close()


def all_task_done():
    for task in asyncio.Task.all_tasks():
        if not task.done():
            return False
    return True


def all_callback_done():
    s = getattr(io_loop.asyncio_loop, '_scheduled')
    for c in s:
        print(c._cancelled, c._scheduled)
        if not c._cancelled:
            return False
    return True


def shutdown():
    wait_seconds = 60
    print('Stopping server...')
    print('Will shutdown in {} seconds ...'.format(wait_seconds))
    deadline = time.time() + wait_seconds

    def stop_loop():
        now = time.time()
        # if not all_task_done() and now < deadline:
        #     io_loop.add_timeout(now + 1, stop_loop)
        if (io_loop.handlers or not all_callback_done()) and now < deadline:
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            print('Server stopped.')

    stop_loop()


def sig_handler(sig, frame):
    print('Caught signal: {}'.format(sig))
    IOLoop.current().add_callback_from_signal(shutdown)


def loop_call_later():
    print('loop call later')
    IOLoop.current().call_later(1, loop_call_later)


class MainHandler(RequestHandler):

    @classmethod
    async def s(cls):
        await gen.sleep(3)
        print('sleep 3 seconds.')

    async def get(self):
        print('please wait 3 seconds...')
        await gen.sleep(3)
        self.write("Hello, world")
        IOLoop.current().add_callback(self.s)
        IOLoop.current().call_later(4, print, '...')
        # IOLoop.current().add_callback(loop_call_later)


async def test_fetch():
    res = await http_client.fetch('http://127.0.0.1:8888', method='GET')
    print('get response! -> ', res.body)


if __name__ == '__main__':
    app = Application([
        (r"/", MainHandler),
    ])
    http_client = AsyncHTTPClient()

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    server = CustomizeHTTPServer(app)
    server.bind(8888)
    server.start()

    IOLoop.current().call_later(1, test_fetch)
    IOLoop.current().call_later(2, server.stop)
    IOLoop.current().call_later(2, shutdown)

    io_loop = IOLoop.instance()
    io_loop.start()
