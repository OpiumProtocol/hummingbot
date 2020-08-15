import logging
import re

from typing import List, Optional, Dict

import ujson
import asyncio
import websockets

from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_message import OrderBookMessage
from hummingbot.core.data_type.order_book_tracker_data_source import OrderBookTrackerDataSource

from hummingbot.logger import HummingbotLogger

from hummingbot.market.binance.binance_order_book import BinanceOrderBook

TRADING_PAIR_FILTER = re.compile(r"(BTC|ETH|USDT)$")

SNAPSHOT_REST_URL = "TODO"
DIFF_STREAM_URL = "TODO WSS"
TICKER_PRICE_CHANGE_URL = "TODO"
EXCHANGE_INFO_URL = "TODO"


class OpiumAPIOrderBookDataSource(OrderBookTrackerDataSource):

    @classmethod
    async def get_last_traded_prices(cls, trading_pairs: List[str]) -> Dict[str, float]:
        pass

    async def get_new_order_book(self, trading_pair: str) -> OrderBook:
        pass

    async def listen_for_order_book_diffs(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        pass

    async def listen_for_order_book_snapshots(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        pass

    _baobds_logger: Optional[HummingbotLogger] = None

    @classmethod
    def logger(cls) -> Optional[HummingbotLogger]:
        if cls._baobds_logger is None:
            cls._baobds_logger = logging.getLogger(__name__)
        return cls._baobds_logger

    def __init__(self, trading_pairs: Optional[List[str]] = None):
        super().__init__(trading_pairs)
        self._trading_pairs: Optional[List[str]] = trading_pairs
        self._order_book_create_function = lambda: OrderBook()

    # TODO
    async def get_trading_pairs(self) -> List[str]:
        # if not self._trading_pairs:
        #     try:
        #         active_markets: pd.DataFrame = await self.get_active_exchange_markets()
        #         self._trading_pairs = active_markets.index.tolist()
        #     except Exception:
        #         self._trading_pairs = []
        #         self.logger().network(
        #             f"Error getting active exchange information.",
        #             exc_info=True,
        #             app_warning_msg=f"Error getting active exchange information. Check network connection."
        #         )
        # return self._trading_pairs
        return []

    # TODO
    async def get_active_exchange_markets(self):
        pass

    # TODO
    async def listen_for_trades(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        while True:
            try:
                trading_pairs: List[str] = await self.get_trading_pairs()
                ws_path: str = "/".join([f"{trading_pair.lower()}@trade" for trading_pair in trading_pairs])
                stream_url: str = f"{DIFF_STREAM_URL}/{ws_path}"

                async with websockets.connect(stream_url) as ws:
                    ws: websockets.WebSocketClientProtocol = ws
                    async for raw_msg in self._inner_messages(ws):
                        msg = ujson.loads(raw_msg)
                        trade_msg: OrderBookMessage = BinanceOrderBook.trade_message_from_exchange(msg)

                        output.put_nowait(trade_msg)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger().error("Unexpected error with WebSocket connection. Retrying after 30 seconds...",
                                    exc_info=True)
                await asyncio.sleep(30.0)
