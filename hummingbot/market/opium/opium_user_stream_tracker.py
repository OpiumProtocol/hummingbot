from hummingbot.core.data_type.user_stream_tracker import UserStreamTracker
from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource


class OpiumUserStreamTracker(UserStreamTracker):
    @property
    def data_source(self) -> UserStreamTrackerDataSource:
        pass

    async def start(self):
        pass
