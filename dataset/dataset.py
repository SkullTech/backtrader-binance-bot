import backtrader as bt


class BinanceDataset(bt.feeds.GenericCSVData):
    params = (
        ('time', -1),
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('close_time', 6),
        ('quote_av', 7),
        ('trades', 8),
        ('tb_base_av', 9),
        ('tb_quote_av', 10),
        ('ignore', 11),
    )
