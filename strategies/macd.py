import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase
from indicators.trend import Trend


class MACDStrategy(StrategyBase):
    params = dict(
        movav=bt.indicators.EMA,
        macd_period_fast=12,
        macd_period_slow=26,
        macd_period_signal=9,
        macd_band=20,

        entry_persistence=5,
        close_persistence=0,
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.log('Using MACD strategy')

        self.p.movav(period=self.p.macd_period_fast)
        self.p.movav(period=self.p.macd_period_slow)
        self.macd = bt.indicators.MACD(movav=self.p.movav, period_me1=self.p.macd_period_fast, period_me2=self.p.macd_period_slow, period_signal=self.p.macd_period_signal)
        self.macd.lines.signal.plot = False
        self.trend = Trend(self.macd, upperband=self.p.macd_band, lowerband=-self.p.macd_band)

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
                if self.trend <= -self.p.close_persistence:
                    self.close()
            if self.last_operation == "SELL":
                if self.trend >= self.p.close_persistence:
                    self.close()
        
        if self.trend >= self.p.entry_persistence:
            self.long()
        if self.trend <= -self.p.entry_persistence:
            self.short()
