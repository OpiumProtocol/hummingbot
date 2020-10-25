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
        self._opium_client: OpiumClient = opium_client
        self._opium_socketio: OpiumApi = OpiumApi(test_api=True)

    @property
    def last_recv_time(self) -> float:
        return self._opium_socketio.get_last_message_time()

    async def get_listen_key(self):
        pass

    async def listen_for_user_stream(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        # TODO: parametrize it
        trading_pair = 'OEX-FUT-1DEC-135.00'
        token = '0x' + self._opium_client.generate_access_token()
        while True:
            try:
                await self._opium_socketio.listen_for_orders(trading_pair=trading_pair,
                                                             maker_addr=self._opium_client.get_public_key(),
                                                             sig=token,
                                                             output=output)

            except Exception as ex:
                self.logger().error(f"{ex} error while maintaining the user event listen key. Retrying after "
                                    "5 seconds...", exc_info=True)
                await asyncio.sleep(5)
