import asyncio
import logging
from typing import Optional

from opium_api import OpiumClient
from opium_sockets import OpiumApi

from hummingbot.core.data_type.user_stream_tracker_data_source import \
    UserStreamTrackerDataSource
from hummingbot.logger import HummingbotLogger


class OpiumAPIUserStreamDataSource(UserStreamTrackerDataSource):
    _logger: Optional[HummingbotLogger] = None

    @classmethod
    def logger(cls) -> HummingbotLogger:
        if cls._logger is None:
            cls._logger = logging.getLogger(__name__)
        return cls._logger

    def __init__(self, opium_client):
        self._client: OpiumClient = opium_client
        self.last_message_time: int = 0

    @property
    def last_recv_time(self) -> float:
        return self.last_message_time

    async def get_listen_key(self):
        pass

    async def listen_for_user_stream(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):

        opium_socketio: OpiumApi = OpiumApi(test_api=True)

        while True:
            try:
                async for msg in opium_socketio.listen_for_account_trades_orders(trading_pair=self._client.trading_pair,
                                                                                       maker_addr=self._client.get_public_key(),
                                                                                       sig=self._client.get_sig()):
                    self.last_message_time = opium_socketio.get_last_message_time()
                    if msg['result']:
                        await output.put(msg)
            except Exception as ex:
                self.logger().error(f"{ex} error while maintaining the user event listen key. Retrying after "
                                    "5 seconds...", exc_info=True)
                await asyncio.sleep(5)
