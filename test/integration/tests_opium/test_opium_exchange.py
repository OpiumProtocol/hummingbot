import asyncio
import os
from decimal import Decimal

from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange
from hummingbot.core.event.events import OrderType
import datetime as dt


class OpiumExchangeTest:
    base_asset: str = 'OEX-FUT-1JAN-135.00'
    quote_asset: str = 'DAI'

    trading_pair: str = base_asset.replace('-', '_') + '-' + quote_asset

    opium_exchange_creds = dict(opium_api_key=os.getenv('opium_test_key'),
                                opium_secret_key=os.getenv('opium_test_secret'),
                                trading_pairs=[trading_pair])

    @classmethod
    def get_exchange(cls):
        return OpiumExchange(**cls.opium_exchange_creds)

    @classmethod
    def test_opium_run(cls):
        async def run():
            exchange = cls.get_exchange()

            assert exchange.name == 'opium'

            await exchange.start_network()
            await asyncio.sleep(10)

            print(f"trading_rules: {exchange.trading_rules}")

            network_status = await exchange.check_network()
            print(f"network_status: {network_status}")

            print(exchange.order_books)

            print(f'balance: {exchange.get_balance(cls.quote_asset)}')

            print(f"orders_status: {exchange.limit_orders}")
            print(f"tracking_states: {exchange.tracking_states}")

            await asyncio.sleep(10)
            print(exchange.status_dict)

            print(exchange.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))

            r = exchange.buy(trading_pair=cls.trading_pair,
                             amount=Decimal('1'),
                             price=Decimal('14.5'))
            print(f"r: {r}")
            await exchange._update_order_status()

            print(exchange.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))
            await asyncio.sleep(15)

            print('update_order_status')
            await exchange._update_order_status()

            # r = ex.cancel(trading_pair, r)
            await asyncio.sleep(15)

            print('cancel all')
            r = await exchange.cancel_all(10)
            print(f"r: {r}")
            # r = ex.cancel(trading_pair, r)
            print(exchange.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))

            print(f"r: {r}")

            await asyncio.sleep(10000)
            await exchange.stop_network()

        asyncio.run(run())

    @classmethod
    def test_buy(cls):
        async def run():
            ex = cls.get_exchange()
            await ex.start_network()
            await asyncio.sleep(5)
            order_id = ex.buy(trading_pair=cls.trading_pair, amount=Decimal('1'), price=Decimal('6.4'))

            print(f"order_id: {order_id}")
            await ex._update_order_status()
            assert cls.base_asset in order_id, order_id

            await asyncio.sleep(15)

        asyncio.run(run())

    @classmethod
    def test_update_balances(cls):
        async def run():
            ex = cls.get_exchange()
            await ex.start_network()
            await asyncio.sleep(5)

            balance = ex.get_available_balance('OEX-FUT-1JAN-135.00')
            # quote_balance = ex.get_available_balance('DAI')
            print(f"balance: {balance}")
            # print(f"quote_balance: {quote_balance}")
            await ex.stop_network()

            await asyncio.sleep(5)

        asyncio.run(run())

    @classmethod
    def test_update_order_status(cls):
        async def run():
            ex = cls.get_exchange()
            await ex.start_network()
            await asyncio.sleep(5)

            # test buy
            print(ex.tick((dt.datetime.now() - dt.timedelta(days=-5)).timestamp()))

            r = ex.buy(trading_pair=cls.trading_pair,
                       amount=Decimal('1'),
                       price=Decimal('16.38')
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
