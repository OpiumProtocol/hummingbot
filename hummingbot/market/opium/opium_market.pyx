from typing import (
    Dict,
    List,
    # AsyncIterable,
    Optional,
    # Coroutine,
    Tuple,
)

import asyncio

from decimal import Decimal

from hummingbot.core.network_iterator import NetworkStatus
from hummingbot.core.data_type.order_book cimport OrderBook
from hummingbot.core.data_type.order_book_tracker import OrderBookTrackerDataSourceType
from hummingbot.core.event.events import MarketEvent
from hummingbot.core.data_type.cancellation_result import CancellationResult
from hummingbot.core.data_type.limit_order import LimitOrder
from hummingbot.market.market_base import MarketBase

# API_VERSION = 'v1'
# API_HOST = 'api-test.opium.exchange'

cdef class OpiumMarket(MarketBase):
    def __init__(self,
                 opium_api_key: str,
                 opium_api_secret: str,
                 ):
        super().__init__()
        # self._api_url: str = f'https://api-test.opium.exchange/v1'
        # self._opium_client = OpiumClient(opium_api_key, opium_api_secret)
        self._opium_client = ""
        # self._ev_loop = asyncio.get_event_loop()

    # TODO
    async def _update_balances(self):
        cdef:
            dict account_info
            list balances
            str asset_name
            set local_asset_names = set(self._account_balances.keys())
            set remote_asset_names = set()
            set asset_names_to_remove

        # account_info = await self.query_api(self._binance_client.get_account)
        # TODO: query the API; TEST DATA
        account_info = {
            "balances": [
                {"asset": "BTC", "free": 10, "locked": "10"},
                {"asset": "ETH", "free": 10, "locked": 10},
                {"asset": "USDT", "free": 10, "locked": 10}
            ]
        }

        balances = account_info["balances"]

        for balance_entry in balances:
            asset_name = balance_entry["asset"]
            free_balance = Decimal(balance_entry["free"])
            total_balance = Decimal(balance_entry["free"]) + Decimal(balance_entry["locked"])
            self._account_available_balances[asset_name] = free_balance
            self._account_balances[asset_name] = total_balance
            remote_asset_names.add(asset_name)

        asset_names_to_remove = local_asset_names.difference(remote_asset_names)
        for asset_name in asset_names_to_remove:
            del self._account_available_balances[asset_name]
            del self._account_balances[asset_name]

    @property
    def name(self) -> str:
        return "opium"

    # TODO
    @property
    def opium_client(self) -> None:  # TODO: -> OpiumClient
        # return self._opium_client
        return None

    # TODO
    @property
    def order_books(self) -> Dict[str, OrderBook]:
        return self._order_book_tracker.order_books

    # TODO
    @property
    def status_dict(self) -> Dict[str, bool]:
        return {
            "order_books_initialized": True,  # self._order_book_tracker.ready,
            "account_balance": True,  # len(self._account_balances) > 0 if self._trading_required else True,
            "trading_rule_initialized": True,  # len(self._trading_rules) > 0,
            "trade_fees_initialized": True,  # len(self._trade_fees) > 0
        }

    # TODO
    @staticmethod
    def split_trading_pair(trading_pair: str) -> Optional[Tuple[str, str]]:
        try:
            # m = TRADING_PAIR_SPLITTER.match(trading_pair)
            print("SPLITTING LIKE A MAD MAN")
            print(trading_pair)
            return ["ETH", "USDT"]
            # return m.group(1), m.group(2)
        # Exceptions are now logged as warnings in trading pair fetcher
        except Exception as e:
            return None

    # TODO
    @property
    def limit_orders(self) -> List[LimitOrder]:
        return [
            # in_flight_order.to_limit_order()
            # for in_flight_order in self._in_flight_orders.values()
        ]

    @property
    def ready(self) -> bool:
        return all(self.status_dict.values())

    # ----------------------------------------
    # Account Balances

    # TODO
    def get_all_balances(self) -> Dict[str, float]:
        print("getting all balances")
        self._account_balances = {"ETH": 50.0, "USDT": 1000, "ETH-USDT": 500}
        return self._account_balances

    cdef object c_get_balance(self, str currency):
        return self._account_balances[currency]

    # TODO
    async def check_network(self) -> NetworkStatus:
        try:
            # await self.query_api(self._binance_client.ping)
            pass
        except asyncio.CancelledError:
            raise
        except Exception:
            return NetworkStatus.NOT_CONNECTED
        return NetworkStatus.CONNECTED

    # TODO
    async def cancel_all(self, timeout_seconds: float) -> List[CancellationResult]:
        return []
        # incomplete_orders = [o for o in self._in_flight_orders.values() if not o.is_done]
        # tasks = [self.execute_cancel(o.trading_pair, o.client_order_id) for o in incomplete_orders]
        # order_id_set = set([o.client_order_id for o in incomplete_orders])
        # successful_cancellations = []

        # try:
        #     async with timeout(timeout_seconds):
        #         cancellation_results = await safe_gather(*tasks, return_exceptions=True)
        #         for cr in cancellation_results:
        #             if isinstance(cr, BinanceAPIException):
        #                 continue
        #             if isinstance(cr, dict) and "origClientOrderId" in cr:
        #                 client_order_id = cr.get("origClientOrderId")
        #                 order_id_set.remove(client_order_id)
        #                 successful_cancellations.append(CancellationResult(client_order_id, True))
        # except Exception:
        #     self.logger().network(
        #         f"Unexpected error cancelling orders.",
        #         exc_info=True,
        #         app_warning_msg="Failed to cancel order with Binance. Check API key and network connection."
        #     )

        # failed_cancellations = [CancellationResult(oid, False) for oid in order_id_set]
        # return successful_cancellations + failed_cancellations
