from asyncio import FIRST_COMPLETED, BaseEventLoop
from typing import Callable, Dict, List

import aiohttp

from hummingbot.connector.exchange.binance.binance_api_order_book_data_source import BinanceAPIOrderBookDataSource
import asyncio

from hummingbot.connector.exchange.opium.opium_api_order_book_data_source import OpiumAPIOrderBookDataSource


def test_get_last_traded_price_binance() -> float:
    """
    381.18
    """
    order_book_api = BinanceAPIOrderBookDataSource(['ETHUSDT'])

    return asyncio.run(order_book_api.get_last_traded_price('ETHUSDT'))


def test_get_last_traded_price_opium() -> float:
    """
    381.18
    """
    order_book_api = OpiumAPIOrderBookDataSource(['OEX-FUT-1DEC-135.00'])

    return asyncio.run(order_book_api.get_last_traded_price('OEX-FUT-1DEC-135.00'))


def test_get_last_traded_prices_binance() -> Dict[str, float]:
    """
    return: {'ETHUSDT': 380.7, 'BNBUSDT': 30.6446}
    """
    order_book_api = BinanceAPIOrderBookDataSource(['ETHUSDT'])

    return asyncio.run(order_book_api.get_last_traded_prices(['ETHUSDT', 'BNBUSDT']))


def test_get_last_traded_prices_opium() -> Dict[str, float]:
    """
    return: {'ETHUSDT': 380.7, 'BNBUSDT': 30.6446}
    """
    order_book_api = OpiumAPIOrderBookDataSource(['OEX-FUT-1DEC-135.00'])

    return asyncio.run(order_book_api.get_last_traded_prices(['OEX-FUT-1DEC-135.00', 'OEX-FUT-1NOV-135.00']))


def test_fetch_trading_pairs_binance() -> List[str]:
    """
    ['ETH-BTC', 'LTC-BTC', 'BNB-BTC', 'NEO-BTC', 'QTUM-ETH']
    """
    order_book_api = BinanceAPIOrderBookDataSource(['ETHUSDT'])

    return asyncio.run(order_book_api.fetch_trading_pairs())


def test_fetch_trading_pairs_opium() -> List[str]:
    order_book_api = OpiumAPIOrderBookDataSource(['OEX-FUT-1DEC-135.00'])

    return asyncio.run(order_book_api.fetch_trading_pairs())


def test_get_snapshot_binance():
    """
    return: {'lastUpdateId': 3486706525, 'bids': [['380.48000000', '1.75000000'], ['380.47000000', '8.43429000'],
    ['380.46000000', '30.00000000'], ['380.45000000', '0.11201000'], ['380.44000000', '30.00000000'],
    ....
    ['392.65000000', '0.29000000'], ['392.66000000', '1.61626000'], ['392.67000000', '198.24511000'],
    ['392.68000000', '0.09729000'], ['392.70000000', '1.07150000'], ['392.71000000', '2.27962000']]}

    """
    order_book_api = BinanceAPIOrderBookDataSource(['ETHUSDT'])

    async def run():
        async with aiohttp.ClientSession() as client:
            return await order_book_api.get_snapshot(client, 'ETHUSDT')

    return asyncio.run(run())


def test_get_new_order_book():
    order_book_api = BinanceAPIOrderBookDataSource(['ETHUSDT'])

    """
    return: [1000 rows x 3 columns],       price    amount     update_id
                                    0    380.90   5.03050  3.485955e+09
                                    1    380.92   2.63000  3.485955e+09
                                    2    380.93  14.93154  3.485955e+09
                                    3    380.94   6.00000  3.485955e+09
                                    4    380.95   9.97644  3.485955e+09
    """
    return asyncio.run(order_book_api.get_new_order_book('ETHUSDT')).snapshot


def test_listen_for(method: Callable):
    """
    method: b.listen_for_trades / b.listen_for_order_book_diffs / b.listen_for_order_book_snapshots

    listen_for_trades returns:
    OrderBookMessage(type=<OrderBookMessageType.TRADE: 3>, content={'trading_pair': 'ETH-USDT', 'trade_type': 1.0, 'trade_id': 199324566, 'update_id': 1603786371199, 'price': '393.55000000', 'amount': '0.87674000'}, timestamp=1603786371.1990001)

    """

    async def read_from_queue(queue):
        """
        message format: OrderBookMessage(type=<OrderBookMessageType.TRADE: 3>, content={'trading_pair': 'ETHUSDT', 'trade_type': 2.0, 'trade_id': 196062668, 'update_id': 1602676892630, 'price': '378.62000000', 'amount': '0.05281000'}, timestamp=1602676892.63)
        """
        while True:
            message = await queue.get()
            print(f"message: {message}")
            queue.task_done()

    async def run():
        output = asyncio.Queue()

        loop: BaseEventLoop = None  # we don't use it inside b.listen_for_trades(...)
        socket_2_task = asyncio.create_task(read_from_queue(output))
        socket_1_task = asyncio.create_task(method(ev_loop=loop, output=output))

        done, pending = await asyncio.wait({socket_1_task, socket_2_task}, return_when=FIRST_COMPLETED)
        print(done)
        print(pending)

    return asyncio.run(run())


if __name__ == '__main__':
    # order_book_api_ = BinanceAPIOrderBookDataSource(['ETHUSDT'])
    order_book_api_ = OpiumAPIOrderBookDataSource(['OEX-FUT-1DEC-135.00'])

    # print(test_fetch_trading_pairs_opium())
    print(test_listen_for(order_book_api_.listen_for_order_book_snapshots))
