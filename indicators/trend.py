import backtrader as bt


class Persistence(bt.Indicator):
    lines = ('persistence',)

    def next(self):
        self.lines.persistence[0] = self.lines.persistence[-1] + 1 if self.data else 0


class Trend(bt.Indicator):
    lines = ('trend',)
    params = (
        ('upperband', 20),
        ('lowerband', -20),
    )

    def __init__(self):
        super().__init__()
        uptrend = Persistence(self.data >= self.p.upperband)
        downtrend = Persistence(self.data < self.p.lowerband)
        self.lines.trend = uptrend - downtrend
