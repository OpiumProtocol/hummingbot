import asyncio

from hummingbot.market.binance.binance_order_book_tracker import BinanceOrderBookTracker
from hummingbot.market.opium.opium_order_book_tracker import OpiumOrderBookTracker


def test_binance_order_book_tracker():
    async def run():
        tracker = BinanceOrderBookTracker(['ETHUSDT'])
        tracker.start()
        await asyncio.sleep(10)

        for ob in tracker.order_books.values():
            print(ob.last_trade_price)

    asyncio.run(run())


test_binance_order_book_tracker()


def test_opium_order_book_tracker():
    tracker = OpiumOrderBookTracker(['OEX-FUT-1DEC-135.00'])
    print(f"tracker: {tracker}")
