import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase
from indicators.trend import Trend
from indicators.supertrend import SuperTrend


class SuperTrendCCIStrategy(StrategyBase):
    params = dict(
        supertrend_period=14,
        supertrend_multiplier=9,

        cci_period=20,
        entry_persistence=10,
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.log('Using SuperTrend strategy')

        self.supertrend = SuperTrend(period=self.p.supertrend_period, multiplier=self.p.supertrend_multiplier)
        self.cci = bt.indicators.CCI(period=self.p.cci_period)
        self.trend = Trend(self.data - self.supertrend, upperband=0, lowerband=0)

    def update_indicators(self):
        self.profit = 0
        if self.last_operation == 'BUY' and self.last_buy_price:
            self.profit = float(self.data0.close[0] - self.last_buy_price) / self.last_buy_price
        if self.last_operation == 'SELL' and self.last_sell_price:
            self.profit = float(self.last_sell_price - self.data0.close[0]) / self.last_sell_price

    def next(self):
        self.update_indicators()

        if self.status != "LIVE" and ENV == PRODUCTION:
            return

        if self.order:
            return

        if self.profit < -0.03:
            self.log("STOP LOSS: percentage %.3f %%" % self.profit)
            self.close()

        if self.position:
            if self.last_operation == "BUY":
                if self.trend <= 0:
                    self.close()
            if self.last_operation == "SELL":
                if self.trend >= 0:
                    self.close()
        
        if self.trend > 0 and self.trend <= self.p.entry_persistence and self.cci >= 100:
            self.long()
        if self.trend < 0 and self.trend >= -self.p.entry_persistence and self.cci <= -100:
            self.short()
