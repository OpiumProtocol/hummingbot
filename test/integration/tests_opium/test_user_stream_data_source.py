import asyncio
import os
from asyncio import BaseEventLoop, FIRST_COMPLETED

from binance.client import Client
from opium_api import OpiumClient

from hummingbot.market.binance.binance_api_user_stream_data_source import BinanceAPIUserStreamDataSource
from hummingbot.market.opium.opium_api_user_stream_data_source import OpiumAPIUserStreamDataSource


def test_listen_for_user_stream_binance():
    async def read_from_queue(queue):
        while True:
            message = await queue.get()
            print(f"message: {message}")
            queue.task_done()

    async def run():
        binance_client = Client(api_key=os.getenv('binance_test_key'), api_secret=os.getenv('binance_test_secret'))

        ds = BinanceAPIUserStreamDataSource(binance_client=binance_client)

        output = asyncio.Queue()

        loop: BaseEventLoop = None  # we don't use it inside b.listen_for_trades(...)
        socket_2_task = asyncio.create_task(read_from_queue(output))
        socket_1_task = asyncio.create_task(ds.listen_for_user_stream(ev_loop=loop, output=output))

        done, pending = await asyncio.wait({socket_1_task, socket_2_task}, return_when=FIRST_COMPLETED)
        print(done)
        print(pending)

    return asyncio.run(run())


def test_listen_for_user_stream_opium():
    async def read_from_queue(queue):
        while True:
            message = await queue.get()
            print(f"message: {message}")
            queue.task_done()

    async def run():
        opium = OpiumClient(public_key=os.getenv('opium_test_key'), private_key=os.getenv('opium_test_secret'))

        ds = OpiumAPIUserStreamDataSource(opium_client=opium)

        output = asyncio.Queue()

        loop: BaseEventLoop = None  # we don't use it inside b.listen_for_trades(...)
        socket_2_task = asyncio.create_task(read_from_queue(output))
        socket_1_task = asyncio.create_task(ds.listen_for_user_stream(ev_loop=loop, output=output))

        done, pending = await asyncio.wait({socket_1_task, socket_2_task}, return_when=FIRST_COMPLETED)
        print(done)
        print(pending)

    return asyncio.run(run())
