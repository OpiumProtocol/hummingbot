import asyncio
import os
from decimal import Decimal

from hummingbot.connector.exchange.binance.binance_exchange import BinanceExchange
# from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange
from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange
from hummingbot.core.event.events import OrderType


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


import datetime as dt


class OpiumExchangeTest:


    @classmethod
    def test_opium_run(cls):
        async def run():
            ex = OpiumExchange(opium_api_key=os.getenv('opium_test_key'),
                               opium_api_secret=os.getenv('opium_test_secret'),
                               trading_pairs=['OEX-FUT-1DEC-135.00'])
            print(ex.name)
            print(ex.order_books)
            print(ex.get_balance('DAI'))
            await ex.start_network()
            await asyncio.sleep(10)

            r = await ex.check_network()
            print(f"network_status: {r}")

            print(f"orders_status: {ex.limit_orders}")
            print(f"tracking_states: {ex.tracking_states}")

            await asyncio.sleep(10)
            print(ex.status_dict)

            trading_pair = 'OEX-FUT-1DEC-135.00'
            print(ex.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))

            r = ex.buy(trading_pair=trading_pair,
                       amount=Decimal('1'),
                       order_type=OrderType.LIMIT,
                       price=Decimal('14.5')
                       )
            print(f"r: {r}")



            print(ex.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))
            await asyncio.sleep(15)
            # r = ex.cancel(trading_pair, r)

            print('cancel all')
            r = await ex.cancel_all(10)
            print(f"r: {r}")
            # r = ex.cancel(trading_pair, r)
            print(ex.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))

            print(f"r: {r}")

            await asyncio.sleep(10000)
            await ex.stop_network()

        asyncio.run(run())


if __name__ == '__main__':
    OpiumExchangeTest.test_opium_run()
