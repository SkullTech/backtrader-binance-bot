import backtrader as bt


class PragmaticSizer(bt.Sizer):
    params = (
        ('percents', 99),
        ('cashlimit', 100000)
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if not position:
            size = min(cash, self.p.cashlimit) / data.close[0] * (self.params.percents / 100)
        else:
            size = position.size

        return size
