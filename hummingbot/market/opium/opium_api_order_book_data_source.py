import asyncio
import logging
from typing import List, Optional, Dict, Any
import re
import time

# import aiohttp
# import pandas as pd
# import ujson
import socketio

from hummingbot.core.data_type.order_book import OrderBook
# from hummingbot.core.data_type.order_book_message import OrderBookMessage
from hummingbot.core.data_type.order_book_tracker_data_source import OrderBookTrackerDataSource

from hummingbot.logger import HummingbotLogger


TRADING_PAIR_FILTER = re.compile(r"(BTC|ETH|USDT)$")

SNAPSHOT_REST_URL = "TODO"
DIFF_STREAM_URL = "TODO WSS"
TICKER_PRICE_CHANGE_URL = "TODO"
EXCHANGE_INFO_URL = "TODO"

sio: socketio.Client = socketio.AsyncClient(engineio_logger=True, logger=True)

# class OpiumSIOClient(socketio.AsyncClientNamespace):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.trades_queue = asyncio.Queue()
#         self.snapshot_queue = asyncio.Queue()
#         self._subbed = False

#     def on_connect(self):
#         print("connected")
#         self._subbed = True


#     async def on_listen_trades(self, data):
#         print("on_listen_trades")
#         await self.trades_queue.put(data)

#     async def on_get_snapshot(self, data):
#         print("on_get_snapshot")
#         await self.snapshot_queue.put(data)

#     async def on_error(self, err=None):
#         print("on_error")
#         print(err)
trades_queue = asyncio.Queue()
snapshot_queue = asyncio.Queue()
order_book_diffs_queue = asyncio.Queue()
order_book_snapshots_queue = asyncio.Queue()
_subbed = False


@sio.on("connect", namespace="/v1")
async def on_connect():
    # TODO: Move this somewhere where we have access to ticker and currency
    ticker = '0x598cc7d5b3a09a27e68b450610d5b47d86cc8602308f23232c03571f79e65a77'
    currency = '0x0558dc82f203C8c5f5b9033061aa5AdefFC40AF7'
    print("connected")
    await sio.emit(event='subscribe', data={'ch': 'orderbook:orders:ticker', 't': ticker, 'c': currency}, namespace='/v1')


@sio.on("orderbook:orders:ticker", namespace="/v1")
async def on_listen_trades(data):
    print("on_listen_trades")
    await trades_queue.put(data)
    await order_book_diffs_queue.put(data)
    await order_book_snapshots_queue.put(data)


async def on_error(err=None):
    print("on_error")
    print(err)
# @sio.on("orderbook:orders:ticker", namespace="/v1")
# async def on_get_snapshot(data):
#     print("on_get_snapshot")
#     await snapshot_queue.put(data)

# _opium_sio_client = OpiumSIOClient("/v1")


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
        self.logger = logging.getLogger(__name__)
        # self._sio = socketio.AsyncClient(engineio_logger=True)
        self._sio = sio
        self._sio_connected = False
        # self._opium_sio_client = _opium_sio_client
        self._sio.logger = self.logger

    @staticmethod
    async def get_snapshot(queue: asyncio.Queue) -> Dict[str, Any]:
        print("get_snapshot")
        while True:
            print("getting snapshot data...")
            data = await queue.get()
            print("data from snapshot queue!")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(data)
            return data
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    # TODO: opium
    # - [ ] figure out how to use socketio
    # - [ ] get api calls for trading pairs
    # What do we use instead of trading pairs? We have different types of contracts,
    # do we treat that as a pair? ETH-FUTURE == a trading pair?
    # async def get_trading_pairs(self) -> List[str]:
    #     self.logger.info("getting trading pairs")
    #     if not self._trading_pairs:
    #         try:
    #             self.logger.info("getting active exchange markets")
    #             active_markets: pd.DataFrame = await self.get_active_exchange_markets()
    #             self._trading_pairs = active_markets.index.tolist()
    #         except Exception:
    #             self._trading_pairs = []
    #             self.logger().network(
    #                 f"Error getting active exchange information.",
    #                 exc_info=True,
    #                 app_warning_msg=f"Error getting active exchange information. Check network connection."
    #             )
    #     self.logger.info("trading pairs: ", self._trading_pairs)
    #     return self._trading_pairs

    # TODO Opium
    async def get_active_exchange_markets(self):
        print("getting active exchange markets")
        return ["ETH-USDC"]

    # TODO: opium
    # - [ ] get the api route / socketio namespace for getting trading pairs
    async def get_trading_pairs(self):
        print("getting trading pairs")
        return ["ETH-USDC"]

    # @classmethod
    async def get_last_traded_prices(cls, trading_pairs: List[str]) -> Dict[str, float]:
        return {"test": 10}
        # return await self._op

    async def connect_sio(self):
        ticker = '0x598cc7d5b3a09a27e68b450610d5b47d86cc8602308f23232c03571f79e65a77'
        currency = '0x0558dc82f203C8c5f5b9033061aa5AdefFC40AF7'
        if not self._sio_connected:
            print("connecting sio")
            # self._sio.register_namespace(self._opium_sio_client)
            await self._sio.connect(url='https://api-test.opium.exchange',
                                        transports=['polling', 'websocket'], namespaces=["/v1"])
            # self._sio.on("orderbook:orders:ticker", handler=on_listen_trades, namespace='/v1')
            await self._sio.emit(event='subscribe', data={'ch': 'orderbook:orders:ticker', 't': ticker, 'c': currency}, namespace='/v1')
            # self._sio.on("orderbook:orders:ticker", handler=self._opium_sio_client.on_listen_trades, namespace='/v1')
            # self._sio.on("orderbook:orders:ticker", handler=self._opium_sio_client.on_listen_trades, namespace='/v1')
            # orderbook:orders:ticker
            self._sio_connected = True

    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for listening to trades
    async def listen_for_trades(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        ticker = '0x598cc7d5b3a09a27e68b450610d5b47d86cc8602308f23232c03571f79e65a77'
        currency = '0x0558dc82f203C8c5f5b9033061aa5AdefFC40AF7'
        if self._baobds_logger is not None:
            self._sio.logger = self.logger
        if not self._sio_connected:
            await self.connect_sio()

        while True:
            self.logger.info("listen for trades")
            self.logger.info("waiting for data...")
            # data = await self._opium_sio_client.trades_queue.get()
            data = await trades_queue.get()
            self.logger.info("data from trades queue!")
            self.logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            self.logger.info(data)
            self.logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            await asyncio.sleep(0.01)

    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for getting new order book
    async def get_new_order_book(self, trading_pair: str) -> OrderBook:
        self.logger.info("get_new_order_book")
        self.logger.info("before get_snapshot")
        # snapshot: Dict[str, Any] = await self.get_snapshot(self._opium_sio_client.snapshot_queue)
        snapshot: Dict[str, Any] = await self.get_snapshot(trades_queue)
        self.logger.info("after get_snapshot")
        snapshot_timestamp: float = time.time()
        order_book: OrderBook = self.order_book_create_function()
        # TODO:
        # snapshot_msg: OrderBookMessage = OpiumOrderBook.snapshot_message_from_exchange(
        #     snapshot,
        #     snapshot_timestamp,
        #     metadata={"trading_pair": trading_pair}
        # )
        # TODO:
        # order_book.apply_snapshot(snapshot_msg.bids, snapshot_msg.asks, snapshot_msg.update_id)
        return order_book

    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for order book snapshots
    async def listen_for_order_book_diffs(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        ticker = '0x598cc7d5b3a09a27e68b450610d5b47d86cc8602308f23232c03571f79e65a77'
        currency = '0x0558dc82f203C8c5f5b9033061aa5AdefFC40AF7'
        if not self._sio_connected:
            await self.connect_sio()

        while True:
            self.logger.info("waiting for order book diffs...")
            # data = await self._opium_sio_client.trades_queue.get()
            data = await order_book_diffs_queue.get()
            self.logger.info("data from order book diffs queue!")
            self.logger.info("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            self.logger.info(data)
            self.logger.info("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            await asyncio.sleep(0.01)

        # sio.register_namespace(self._opium_sio_client)
        # await sio.connect(url='https://api-test.opium.exchange', transports=['polling', 'websocket'], namespaces=['/v1'])

        # await sio.emit("subscribe", {'ch': 'error:message'})
        # await sio.emit("subscribe", {
        #         'ch': 'orderbook:orders:ticker',
        #         't': ticker,
        #         'c': currency})

        # @sio.on('orderbook:orders:ticker')
    # async def update_diff(self):
    #     while True:
    #         print("updating diff")
    #         data = await self._opium_sio_client.trades_queue.get()
    #         self.logger .info("data update diff!")
    #         self.logger .info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    #         self.logger .info(data)
    #         self.logger .info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        #     try:
        #         # ws_path: str = "/".join([f"{trading_pair.lower()}@depth" for trading_pair in self._trading_pairs])
        #         # TODO
        #         ws_path = ""
        #         stream_url: str = f"{DIFF_STREAM_URL}/{ws_path}"
        #         print("Listening for order book diffs")
        #         await asyncio.sleep(30)
        #         # async with websockets.connect(stream_url) as ws:
        #         #     ws: websockets.WebSocketClientProtocol = ws
        #             # async for raw_msg in self._inner_messages(ws):
        #             #     msg = ujson.loads(raw_msg)
        #                 # order_book_message: OrderBookMessage = OpiumOrderBook.diff_message_from_exchange(
        #                 #     msg, time.time())
        #                 # output.put_nowait(order_book_message)
        #     except asyncio.CancelledError:
        #         raise
        #     except Exception:
        #         self.logger().error("Unexpected error with WebSocket connection. Retrying after 30 seconds...",
        #                             exc_info=True)
        #         await asyncio.sleep(30.0)

    # TODO: opium
    # - [ ] figure out how to use socketio lib instead of websockets lib
    # - [ ] get the api route / socketio namespace for order book snapshots
    async def listen_for_order_book_snapshots(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        # print("listening for order book snapshots")
        while True:
            self.logger.info("listening for order book snapshots")
            # data = await self._opium_sio_client.trades_queue.get()
            data = await order_book_snapshots_queue.get()
            self.logger.info("data listen_for_order_book_snapshots!")
            self.logger.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            self.logger.info(data)
            self.logger.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

        # while True:
        #     print("listening for order book snapshots")
        #     try:
        #         async with aiohttp.ClientSession() as client:
        #             for trading_pair in self._trading_pairs:
        #                 try:
        #                     # snapshot: Dict[str, Any] = await self.get_snapshot(client, trading_pair)
        #                     snapshot_timestamp: float = time.time()
        #                     # snapshot_msg: OrderBookMessage = OpiumOrderBook.snapshot_message_from_exchange(
        #                     #     snapshot,
        #                     #     snapshot_timestamp,
        #                     #     metadata={"trading_pair": trading_pair}
        #                     # )
        #                     # output.put_nowait(snapshot_msg)
        #                     self.logger().debug(f"Saved order book snapshot for {trading_pair}")
        #                     # Be careful not to go above Binance's API rate limits.
        #                     await asyncio.sleep(5.0)
        #                 except asyncio.CancelledError:
        #                     raise
        #                 except Exception:
        #                     self.logger().error("Unexpected error.", exc_info=True)
        #                     await asyncio.sleep(5.0)
        #             this_hour: pd.Timestamp = pd.Timestamp.utcnow().replace(minute=0, second=0, microsecond=0)
        #             next_hour: pd.Timestamp = this_hour + pd.Timedelta(hours=1)
        #             delta: float = next_hour.timestamp() - time.time()
        #             await asyncio.sleep(delta)
        #     except asyncio.CancelledError:
        #         raise
        #     except Exception:
        #         self.logger().error("Unexpected error.", exc_info=True)
        #         await asyncio.sleep(5.0)

    # TODO
    async def listen_for_order_book_stream(self,
                                           ev_loop: asyncio.BaseEventLoop,
                                           snapshot_queue: asyncio.Queue,
                                           diff_queue: asyncio.Queue):
        pass
        # while True:
            # connection, hub = await self.websocket_connection()
            # try:
                # async for raw_message in self._socket_stream():
        # print("in listen_for_order_book_stream")
        # await self._opium_sio_client.emit("subscribe", {
        #         'ch': 'orderbook:orders:ticker',
        #         't': ticker,
        #         'c': currency})
        
        #             decoded: Dict[str, Any] = self._transform_raw_message(raw_message)
        #             trading_pair: str = decoded["results"].get("M")
        #             if not trading_pair:  # Ignores any other websocket response messages
        #                 continue
        #             # Processes snapshot messages
        #             if decoded["type"] == "snapshot":
        #                 snapshot: Dict[str, any] = decoded
        #                 snapshot_timestamp = snapshot["nonce"]
        #                 snapshot_msg: OrderBookMessage = BittrexOrderBook.snapshot_message_from_exchange(
        #                     snapshot["results"], snapshot_timestamp
        #                 )
        #                 snapshot_queue.put_nowait(snapshot_msg)
        #                 self._snapshot_msg[trading_pair] = {
        #                     "timestamp": int(time.time()),
        #                     "content": snapshot_msg
        #                 }
        #             # Processes diff messages
        #             if decoded["type"] == "update":
        #                 diff: Dict[str, any] = decoded
        #                 diff_timestamp = diff["nonce"]
        #                 diff_msg: OrderBookMessage = BittrexOrderBook.diff_message_from_exchange(
        #                     diff["results"], diff_timestamp
        #                 )
        #                 diff_queue.put_nowait(diff_msg)

        #     except Exception:
        #         self.logger().error("Unexpected error when listening on socket stream.", exc_info=True)
        #     finally:
        #         connection.close()
        #         self._websocket_connection = self._websocket_hub = None
        #         self.logger().info("Reinitializing websocket connection...")

    def _transform_raw_message(self, msg) -> Dict[str, Any]:
        output: Dict[str, Any] = {}
