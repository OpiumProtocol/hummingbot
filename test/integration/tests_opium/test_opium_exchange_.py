import asyncio
import contextlib
import os
import time
import unittest
from decimal import Decimal
from os.path import realpath, join
from typing import List

from hummingbot.connector.exchange.opium.opium_exchange import OpiumExchange
from hummingbot.core.clock import Clock
from hummingbot.core.clock_mode import ClockMode
from hummingbot.core.event.event_logger import EventLogger
from hummingbot.core.event.events import MarketEvent, OrderType, OrderFilledEvent, BuyOrderCompletedEvent, \
    SellOrderCreatedEvent, SellOrderCompletedEvent, BuyOrderCreatedEvent


class OpiumExchangeUnitTest(unittest.TestCase):
    events: List[MarketEvent] = [
        MarketEvent.BuyOrderCompleted,
        MarketEvent.SellOrderCompleted,
        MarketEvent.OrderFilled,
        MarketEvent.TransactionFailure,
        MarketEvent.BuyOrderCreated,
        MarketEvent.SellOrderCreated,
        MarketEvent.OrderCancelled,
        MarketEvent.OrderFailure
    ]
    connector: OpiumExchange
    event_logger: EventLogger
    trading_pair = 'OEX_FUT_1JAN_135.00-DAI'
    base_token, quote_token = trading_pair.split("-")
    stack: contextlib.ExitStack

    @classmethod
    def setUpClass(cls):
        global MAINNET_RPC_URL

        cls.ev_loop = asyncio.get_event_loop()

        cls.clock: Clock = Clock(ClockMode.REALTIME)
        cls.connector: OpiumExchange = OpiumExchange(
            opium_api_key=os.getenv('opium_test_key'),
            opium_secret_key=os.getenv('opium_test_secret'),
            trading_pairs=[cls.trading_pair],
            trading_required=True
        )
        print("Initializing Opium market... this will take about a minute.")
        cls.clock.add_iterator(cls.connector)
        cls.stack: contextlib.ExitStack = contextlib.ExitStack()
        cls._clock = cls.stack.enter_context(cls.clock)
        cls.ev_loop.run_until_complete(cls.wait_til_ready())
        print("Ready.")

    def setUp(self):
        self.db_path: str = realpath(join(__file__, "../connector_test.sqlite"))
        try:
            os.unlink(self.db_path)
        except FileNotFoundError:
            pass

        self.event_logger = EventLogger()
        for event_tag in self.events:
            self.connector.add_listener(event_tag, self.event_logger)

    def tearDown(self):
        for event_tag in self.events:
            self.connector.remove_listener(event_tag, self.event_logger)
        self.event_logger = None

    @classmethod
    async def wait_til_ready(cls, connector=None):
        if connector is None:
            connector = cls.connector
        while True:
            now = time.time()
            next_iteration = now // 1.0 + 1
            if connector.ready:
                break
            else:
                await cls._clock.run_til(next_iteration)
            await asyncio.sleep(1.0)

    def _place_order(self, is_buy, amount, order_type, price) -> str:
        if is_buy:
            cl_order_id = self.connector.buy(self.trading_pair, amount, order_type, price)
        else:
            cl_order_id = self.connector.sell(self.trading_pair, amount, order_type, price)
        return cl_order_id

    def test_buy_and_sell(self):
        price = self.connector.get_price(self.trading_pair, True) * Decimal("1.05")
        price = self.connector.quantize_order_price(self.trading_pair, price)
        amount = self.connector.quantize_order_amount(self.trading_pair, Decimal("1"))
        quote_bal = self.connector.get_available_balance(self.quote_token)
        print(f"price: {price}")
        print(f"amount: {amount}")
        print(f"quote_bal: {quote_bal}")
        base_bal = self.connector.get_available_balance(self.base_token)
        print(f"base_bal: {base_bal}")

        order_id = self._place_order(True, amount, OrderType.LIMIT, price)
        order_completed_event = self.ev_loop.run_until_complete(self.event_logger.wait_for(BuyOrderCompletedEvent))
        self.ev_loop.run_until_complete(asyncio.sleep(2))
        trade_events = [t for t in self.event_logger.event_log if isinstance(t, OrderFilledEvent)]
        base_amount_traded = sum(t.amount for t in trade_events)
        quote_amount_traded = sum(t.amount * t.price for t in trade_events)
        print(f"base_amount_traded: {base_amount_traded}")
        print(f"quote_amount_traded: {quote_amount_traded}")

        self.assertTrue([evt.order_type == OrderType.LIMIT for evt in trade_events])
        self.assertEqual(order_id, order_completed_event.order_id)
        self.assertEqual(amount, order_completed_event.base_asset_amount)
        print(f"order_completed_event.base_asset: {order_completed_event.base_asset}")
        print(f"order_completed_event.quote_asset: {order_completed_event.quote_asset}")
        # TODO: returns: OEX, FUT
        # self.assertEqual("OEX_FUT_1DEC_135.00", order_completed_event.base_asset)
        # self.assertEqual("DAI", order_completed_event.quote_asset)
        self.assertAlmostEqual(base_amount_traded, order_completed_event.base_asset_amount)
        self.assertAlmostEqual(quote_amount_traded, order_completed_event.quote_asset_amount)
        self.assertGreaterEqual(order_completed_event.fee_amount, Decimal(0))
        self.assertTrue(any([isinstance(event, BuyOrderCreatedEvent) and event.order_id == order_id
                             for event in self.event_logger.event_log]))

        # check available quote balance gets updated, we need to wait a bit for the balance message to arrive
        expected_quote_bal = quote_bal - quote_amount_traded
        self.ev_loop.run_until_complete(asyncio.sleep(1))

        available_balance = self.connector.get_available_balance(self.quote_token)
        self.assertAlmostEqual(expected_quote_bal, available_balance)

        # Reset the logs
        self.event_logger.clear()

        # Try to sell back the same amount to the exchange, and watch for completion event.
        price = self.connector.get_price(self.trading_pair, True) * Decimal("0.95")
        price = self.connector.quantize_order_price(self.trading_pair, price)
        amount = self.connector.quantize_order_amount(self.trading_pair, Decimal("1"))
        order_id = self._place_order(False, amount, OrderType.LIMIT, price)
        order_completed_event = self.ev_loop.run_until_complete(self.event_logger.wait_for(SellOrderCompletedEvent))
        trade_events = [t for t in self.event_logger.event_log if isinstance(t, OrderFilledEvent)]
        base_amount_traded = sum(t.amount for t in trade_events)
        quote_amount_traded = sum(t.amount * t.price for t in trade_events)

        self.assertTrue([evt.order_type == OrderType.LIMIT for evt in trade_events])
        self.assertEqual(order_id, order_completed_event.order_id)
        self.assertEqual(amount, order_completed_event.base_asset_amount)
        self.assertEqual("OEX_FUT_1DEC_135.00", order_completed_event.base_asset)
        self.assertEqual("DAI", order_completed_event.quote_asset)
        self.assertAlmostEqual(base_amount_traded, order_completed_event.base_asset_amount)
        self.assertAlmostEqual(quote_amount_traded, order_completed_event.quote_asset_amount)
        self.assertGreater(order_completed_event.fee_amount, Decimal(0))
        self.assertTrue(any([isinstance(event, SellOrderCreatedEvent) and event.order_id == order_id
                             for event in self.event_logger.event_log]))

        # check available base balance gets updated, we need to wait a bit for the balance message to arrive
        expected_base_bal = base_bal
        self.ev_loop.run_until_complete(asyncio.sleep(1))
        bl = self.connector.get_available_balance(self.base_token)
        print(f"bl: {bl}")
        self.assertAlmostEqual(expected_base_bal, bl, 5)
