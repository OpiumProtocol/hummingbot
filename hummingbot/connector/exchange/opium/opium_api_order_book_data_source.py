import logging
import re
import time

from typing import List, Optional, Dict, Any

import aiohttp
import asyncio
from opium_sockets import OpiumApi

from hummingbot.connector.exchange.opium.opium_active_order_tracker import OpiumActiveOrderTracker
from hummingbot.connector.exchange.opium.opium_order_book import OpiumOrderBook
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_message import OrderBookMessage
from hummingbot.core.data_type.order_book_tracker_data_source import OrderBookTrackerDataSource
from hummingbot.core.utils.async_utils import safe_gather
from hummingbot.logger import HummingbotLogger

TRADING_PAIR_FILTER = re.compile(r"(BTC|ETH|USDT)$")

SNAPSHOT_REST_URL = "TODO"
DIFF_STREAM_URL = "TODO WSS"
TICKER_PRICE_CHANGE_URL = "TODO"
EXCHANGE_INFO_URL = "TODO"


class OpiumAPIOrderBookDataSource(OrderBookTrackerDataSource):
    _logger: Optional[HummingbotLogger] = None

    @classmethod
    def logger(cls) -> Optional[HummingbotLogger]:
        if cls._logger is None:
            cls._logger = logging.getLogger(__name__)
        return cls._logger

    def __init__(self, trading_pairs: Optional[List[str]] = None):
        super().__init__(trading_pairs)
        self._trading_pairs: Optional[List[str]] = trading_pairs
        self._order_book_create_function = lambda: OrderBook()

    @classmethod
    async def get_last_traded_prices(cls, trading_pairs: List[str]) -> Dict[str, float]:
        tasks = [cls.get_last_traded_price(t_pair) for t_pair in trading_pairs]
        results = await safe_gather(*tasks)
        return {t_pair: result for t_pair, result in zip(trading_pairs, results)}

    @classmethod
    async def get_last_traded_price(cls, trading_pair: str) -> float:
        oa = OpiumApi(test_api=True)
        r = await oa.get_latest_price(trading_pair)
        return float(r[trading_pair])

    @staticmethod
    async def get_order_book_data(trading_pair: str) -> Dict[str, any]:
        """
        Get whole orderbook
        """
        oa = OpiumApi(test_api=True)

        return await oa.get_new_order_book(trading_pair)

    async def get_new_order_book(self, trading_pair: str) -> OrderBook:
        snapshot: Dict[str, Any] = await self.get_order_book_data(trading_pair)
        snapshot_timestamp: float = time.time()
        snapshot_msg: OrderBookMessage = OpiumOrderBook.snapshot_message_from_exchange(
            snapshot,
            snapshot_timestamp,
            metadata={"trading_pair": trading_pair}
        )
        order_book = self.order_book_create_function()
        active_order_tracker: OpiumActiveOrderTracker = OpiumActiveOrderTracker()
        bids, asks = active_order_tracker.convert_snapshot_message_to_order_book_row(snapshot_msg)
        order_book.apply_snapshot(bids, asks, snapshot_msg.update_id)
        return order_book

    @staticmethod
    async def fetch_trading_pairs() -> List[str]:
        try:
            async with aiohttp.ClientSession() as client:
                async with client.get('https://api-test.opium.exchange/v1/tickers?expired=false') as resp:
                    return [instrument['productTitle'] for instrument in await resp.json()]
        except Exception:
            pass

        return []

    async def listen_for_order_book_diffs(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        pass

    async def listen_for_order_book_snapshots(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        pass

    async def listen_for_trades(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        """
        Listen for trades using websocket trade channel
        """
        opium_socketio: OpiumApi = OpiumApi(test_api=True)

        trading_pair = 'OEX-FUT-1DEC-135.00'
        while True:
            try:
                async for trade in opium_socketio.listen_for_trades(trading_pair):
                    if trade is None:
                        continue

                    trade: Dict[Any] = trade
                    trade_timestamp: int = trade['timestamp']
                    trade_msg: OrderBookMessage = OpiumOrderBook.trade_message_from_exchange(trade,
                                                                                             trade_timestamp,
                                                                                             metadata={"trading_pair": trading_pair})
                    output.put_nowait(trade_msg)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger().error("Unexpected error.", exc_info=True)
                await asyncio.sleep(5.0)
