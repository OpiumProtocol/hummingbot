import asyncio

from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource


class OpiumAPIUserStreamDataSource(UserStreamTrackerDataSource):
    

    def __init__(self, ): # TODO: Add auth, trading_pairs
        super().__init__()
        self._last_recv_time: float = 0.


    @property
    def last_recv_time(self) -> float:
        return self._last_recv_time
    

    # TODO: Handle with SocketIO
    # TODO: update self._last_recv_time on each new message
    async def listen_for_user_stream(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        pass
