import asyncio
import os

from hummingbot.connector.exchange.binance.binance_exchange import BinanceExchange


def test_binance_run():
    async def run():
        ex = BinanceExchange(binance_api_key=os.getenv('binance_test_key'),
                             binance_api_secret=os.getenv('binance_test_secret'),
                             trading_pairs=['ETHUSDT'])

        print(ex.name)
        print(ex.order_books)
        print(ex.get_balance('BNB'))
        await ex.start_network()
        await asyncio.sleep(10)
        print(ex.status_dict)

    asyncio.run(run())