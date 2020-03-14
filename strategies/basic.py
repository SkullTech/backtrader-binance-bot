#!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase
from indicators.macd_hist import Greater


class Basic(StrategyBase):
    params = dict(
        ma_period_fast=10,
        ma_period_slow=120,
        
        adx_period=10,
        adx_upper_bound=40,
        adx_lower_bound=20,
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.log('Using RSI/EMA strategy')

        self.ma_fast = bt.indicators.EMA(period=self.p.ma_period_fast)
        self.ma_slow = bt.indicators.EMA(period=self.p.ma_period_slow)
        self.lines.ma_uptrend = self.ma_fast >= self.ma_slow
        self.lines.ma_downtrend = self.ma_fast < self.ma_slow

        self.macd = bt.indicators.MACD(period_me1=self.p.macd_period_fast, period_me2=self.p.macd_period_slow, period_signal=self.p.macd_period_signal, plot=True)
        self.macd_uptrend = self.macd.lines.macd >= self.macd.lines.signal
        self.macd_downtrend = self.macd.lines.macd < self.macd.lines.signal
        self.macd_positive = self.macd.lines.macd >= 0
        self.macd_negative = self.macd.lines.macd < 0

        self.adx = bt.indicators.ADX(period=self.p.adx_period)
        self.adx_strong = self.adx > self.p.adx_upper_bound
        self.adx_weak = self.adx <= self.p.adx_lower_bound
        self.profit = 0


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
                if self.macd_downtrend or self.ma_downtrend or self.adx_weak:
                    self.close()
            if self.last_operation == "SELL":
                if self.macd_uptrend or self.ma_uptrend or self.adx_weak:
                    self.close()
        
        # if self.macd_uptrend:
        if self.ma_uptrend and self.macd_uptrend and self.adx_strong:
            self.long()
        # if self.macd_downtrend:
        if self.ma_downtrend and self.macd_downtrend and self.adx_strong:
            self.short()
