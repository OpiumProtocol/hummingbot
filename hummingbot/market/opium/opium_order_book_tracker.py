import asyncio
from typing import (
    List,
    Optional
)

from hummingbot.market.opium.opium_api_order_book_data_source import OpiumAPIOrderBookDataSource

from hummingbot.core.data_type.order_book_tracker import OrderBookTracker


class OpiumOrderBookTracker(OrderBookTracker):
    
    def __init__(self, trading_pairs: Optional[List[str]] = None):
        print(trading_pairs)
        super().__init__(
            data_source=OpiumAPIOrderBookDataSource(trading_pairs=trading_pairs),
            trading_pairs=trading_pairs
        )

        # self._order_book_diff_stream: asyncio.Queue = asyncio.Queue()
        # self._order_book_snapshot_stream: asyncio.Queue = asyncio.Queue()
        # self._ev_loop: asyncio.BaseEventLoop = asyncio.get_event_loop()
        # self._saved_message_queues: Dict[str, Deque[OrderBookMessage]] = defaultdict(lambda: deque(maxlen=1000))

    @property
    def exchange_name(self) -> str:
        return "opium"

    # TODO Opium
    async def _order_book_diff_router(self):
        pass

    # TODO Opium
    async def _track_single_book(self, trading_pair: str):
        pass