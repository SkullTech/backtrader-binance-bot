#!/usr/bin/env python3

import backtrader as bt


class Greater(bt.Indicator):
    lines = ('greater',)

    def __init__(self, line1, line2):
        self.l.greater = bt.Cmp(line1, line2)
