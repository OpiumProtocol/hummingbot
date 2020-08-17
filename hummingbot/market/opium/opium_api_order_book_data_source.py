import asyncio
import logging
from typing import List, Optional, Dict
import re
import time

import aiohttp
import pandas as pd
import ujson
# import socketio
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


    _baobds_logger: Optional[HummingbotLogger] = None

    @classmethod
    def logger(cls) -> HummingbotLogger:
        if cls._baobds_logger is None:
            cls._baobds_logger = logging.getLogger(__name__)
        return cls._baobds_logger

    def __init__(self, trading_pairs: Optional[List[str]] = None):
        super().__init__(trading_pairs)
        self._trading_pairs: Optional[List[str]] = trading_pairs
        self._order_book_create_function = lambda: OrderBook()

    # TODO: opium
    # - [ ] figure out how to use socketio
    # - [ ] get api calls for trading pairs
    # What do we use instead of trading pairs? We have different types of contracts,
    # do we treat that as a pair? ETH-FUTURE == a trading pair?
    async def get_trading_pairs(self) -> List[str]:
        if not self._trading_pairs:
            try:
                active_markets: pd.DataFrame = await self.get_active_exchange_markets()
                self._trading_pairs = active_markets.index.tolist()
            except Exception:
                self._trading_pairs = []
                self.logger().network(
                    f"Error getting active exchange information.",
                    exc_info=True,
                    app_warning_msg=f"Error getting active exchange information. Check network connection."
                )
        return self._trading_pairs

    # TODO Opium
    async def get_active_exchange_markets(self):
        return ["BTCETH"]

    # TODO: opium
    # - [ ] get the api route / socketio namespace for getting trading pairs
    async def get_trading_pairs(self):
        ["ETH-USDC"]


    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for listening to trades
    async def listen_for_trades(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        while True:
            try:
                trading_pairs: List[str] = await self.get_trading_pairs()
                # ws_path: str = "/".join([f"{trading_pair.lower()}@trade" for trading_pair in trading_pairs])
                # TODO 
                ws_path = ""
                stream_url: str = f"{DIFF_STREAM_URL}/{ws_path}"
                print("Listening for trades")
                await asyncio.sleep(30)

                # async with socketio_client.connect('https://api-test.opium.exchange', transports=['polling', 'websocket'], namespaces=['/v1']) as ws:

                    # await socketio_client.wait()
                    # ws: websockets.WebSocketClientProtocol = ws
                    # async for raw_msg in self._inner_messages(ws):
                        # msg = ujson.loads(raw_msg)
                        # trade_msg: OrderBookMessage = OpiumOrderBook.trade_message_from_exchange(msg)

                        # output.put_nowait(trade_msg)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger().error("Unexpected error with WebSocket connection. Retrying after 30 seconds...",
                                    exc_info=True)
                await asyncio.sleep(30.0)

    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for getting new order book
    async def get_new_order_book(self, trading_pair: str) -> OrderBook:
        async with aiohttp.ClientSession() as client:
            # snapshot: Dict[str, Any] = await self.get_snapshot(client, trading_pair, 1000)
            snapshot_timestamp: float = time.time()
            # snapshot_msg: OrderBookMessage = OpiumOrderBook.snapshot_message_from_exchange(
            #     snapshot,
            #     snapshot_timestamp,
            #     metadata={"trading_pair": trading_pair}
            # )
            # order_book = self.order_book_create_function()
            # order_book.apply_snapshot(snapshot_msg.bids, snapshot_msg.asks, snapshot_msg.update_id)
            return "order_book"

    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for order book snapshots
    async def listen_for_order_book_diffs(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        while True:
            try:
                # ws_path: str = "/".join([f"{trading_pair.lower()}@depth" for trading_pair in self._trading_pairs])
                # TODO
                ws_path = ""
                stream_url: str = f"{DIFF_STREAM_URL}/{ws_path}"
                print("Listening for order book diffs")
                await asyncio.sleep(30)
                # async with websockets.connect(stream_url) as ws:
                #     ws: websockets.WebSocketClientProtocol = ws
                    # async for raw_msg in self._inner_messages(ws):
                    #     msg = ujson.loads(raw_msg)
                        # order_book_message: OrderBookMessage = OpiumOrderBook.diff_message_from_exchange(
                        #     msg, time.time())
                        # output.put_nowait(order_book_message)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger().error("Unexpected error with WebSocket connection. Retrying after 30 seconds...",
                                    exc_info=True)
                await asyncio.sleep(30.0)

    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for order book snapshots
    async def listen_for_order_book_snapshots(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        while True:
            try:
                async with aiohttp.ClientSession() as client:
                    for trading_pair in self._trading_pairs:
                        try:
                            # snapshot: Dict[str, Any] = await self.get_snapshot(client, trading_pair)
                            snapshot_timestamp: float = time.time()
                            # snapshot_msg: OrderBookMessage = OpiumOrderBook.snapshot_message_from_exchange(
                            #     snapshot,
                            #     snapshot_timestamp,
                            #     metadata={"trading_pair": trading_pair}
                            # )
                            # output.put_nowait(snapshot_msg)
                            self.logger().debug(f"Saved order book snapshot for {trading_pair}")
                            # Be careful not to go above Binance's API rate limits.
                            await asyncio.sleep(5.0)
                        except asyncio.CancelledError:
                            raise
                        except Exception:
                            self.logger().error("Unexpected error.", exc_info=True)
                            await asyncio.sleep(5.0)
                    this_hour: pd.Timestamp = pd.Timestamp.utcnow().replace(minute=0, second=0, microsecond=0)
                    next_hour: pd.Timestamp = this_hour + pd.Timedelta(hours=1)
                    delta: float = next_hour.timestamp() - time.time()
                    await asyncio.sleep(delta)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger().error("Unexpected error.", exc_info=True)
                await asyncio.sleep(5.0)