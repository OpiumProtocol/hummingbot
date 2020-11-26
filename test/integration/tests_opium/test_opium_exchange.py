import asyncio
import os
from decimal import Decimal

from hummingbot.connector.exchange.binance.binance_exchange import BinanceExchange
# from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange
from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange
from hummingbot.core.event.events import OrderType
import datetime as dt


class OpiumExchangeTest:

    @classmethod
    def test_opium_run(cls):
        async def run():
            ex = OpiumExchange(opium_api_key=os.getenv('opium_test_key'),
                               opium_secret_key=os.getenv('opium_test_secret'),
                               trading_pairs=['OEX_FUT_1DEC_135.00-DAI'])
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

            trading_pair = 'OEX_FUT_1DEC_135.00-DAI'
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

    @staticmethod
    def test_buy():

        trading_pair = 'OEX_FUT_1DEC_135.00-DAI'

        async def run():
            ex = OpiumExchange(opium_api_key=os.getenv('opium_test_key'),
                               opium_secret_key=os.getenv('opium_test_secret'),
                               trading_pairs=[trading_pair])
            await ex.start_network()
            await asyncio.sleep(5)


            r = ex.buy(trading_pair=trading_pair,
                       amount=Decimal('1'),
                       order_type=OrderType.LIMIT,
                       price=Decimal('14.5'))
            await asyncio.sleep(5)

            print(f"r: {r}")

        asyncio.run(run())

    @staticmethod
    def test_update_balances():

        trading_pair = 'OEX_FUT_1DEC_135.00-DAI'

        base_asset, quote_asset = trading_pair.split('-')

        async def run():
            ex = OpiumExchange(opium_api_key=os.getenv('opium_test_key'),
                               opium_secret_key=os.getenv('opium_test_secret'),
                               trading_pairs=[trading_pair])
            await ex.start_network()
            await asyncio.sleep(5)



            balance = await ex.get_available_balance('DAI')
            await asyncio.sleep(5)

            print(f"balance: {balance}")

        asyncio.run(run())

    def test_update_order_status(self):
        trading_pair = 'OEX_FUT_1DEC_135.00-DAI'

        base_asset, quote_asset = trading_pair.split('-')

        async def run():
            ex = OpiumExchange(opium_api_key=os.getenv('opium_test_key'),
                               opium_secret_key=os.getenv('opium_test_secret'),
                               trading_pairs=[trading_pair])
            await ex.start_network()
            await asyncio.sleep(5)

            # test buy
            print(ex.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))

            r = ex.buy(trading_pair=trading_pair,
                       amount=Decimal('1'),
                       order_type=OrderType.LIMIT,
                       price=Decimal('14.5')
                       )
            print(f"r: {r}")
            await asyncio.sleep(5)

            print(ex.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))

            await asyncio.sleep(10)

            order_status = await ex._update_order_status()
            await asyncio.sleep(5)

            print(f"order_status: {order_status}")

        asyncio.run(run())





if __name__ == '__main__':
    OpiumExchangeTest.test_opium_run()
