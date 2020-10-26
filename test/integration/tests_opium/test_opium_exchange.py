import asyncio
import os

from hummingbot.connector.exchange.binance.binance_exchange import BinanceExchange
# from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange
from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange


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


def test_opium_run():
    async def run():

        ex = OpiumExchange(opium_api_key=os.getenv('opium_test_key'),
                           opium_api_secret=os.getenv('opium_test_secret'),
                           trading_pairs=['OEX-FUT-1DEC-135.00'])
        print(ex.name)
        print(ex.order_books)
        print(ex.get_balance('BNB'))
        await ex.start_network()
        await asyncio.sleep(10)
        print(ex.status_dict)
    asyncio.run(run())


if __name__ == '__main__':
    test_opium_run()
