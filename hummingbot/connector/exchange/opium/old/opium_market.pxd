from hummingbot.market.market_base cimport MarketBase

cdef class OpiumMarket(MarketBase):
    cdef:
        public object _opium_client
