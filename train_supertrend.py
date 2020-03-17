import time
import dateparser
import argparse
import backtrader as bt
import datetime as dt
from config import secrets, ENV, PRODUCTION, COIN_TARGET, COIN_REFER, DEBUG

from dataset.dataset import BinanceDataset
from sizer.pragmatic import PragmaticSizer
from strategies.supertrend_cci import SuperTrendCCIStrategy
from utils import print_trade_analysis, print_sqn, send_telegram_message


def evaluate(args):
    (compression, entry_persistence, period, multiplier, cci_period) = args
    compression = int(compression)
    entry_persistence = int(entry_persistence)
    period = int(period)

    cerebro = bt.Cerebro(quicknotify=True)
    data = BinanceDataset(
        name=COIN_TARGET,
        dataname="dataset/binance_btc_cumulated_1m_klines.csv",
        timeframe=bt.TimeFrame.Minutes,
        fromdate=dateparser.parse('1 Jan 2019'),
        todate=dateparser.parse('31 Dec 2019'),
        nullvalue=0.0
    )

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=compression)
    broker = cerebro.getbroker()
    broker.setcommission(commission=0.001, name=COIN_TARGET)
    broker.setcash(100000.0)
    cerebro.addsizer(PragmaticSizer)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    cerebro.addstrategy(SuperTrendCCIStrategy, entry_persistence=entry_persistence, supertrend_period=period, supertrend_multiplier=multiplier, cci_period=cci_period)

    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    result = cerebro.run()

    # Print analyzers - results
    final_value = cerebro.broker.getvalue()

    print('Final Portfolio Value: %.2f' % final_value)
    print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))
    # print_trade_analysis(result[0].analyzers.ta.get_analysis())
    sqn = print_sqn(result[0].analyzers.sqn.get_analysis())
    print(f'compression: {compression}, entry_persistence {entry_persistence}, period {period}, multiplier {multiplier}, sqn {sqn}')
    return final_value, sqn


results = []
for compression in [30]:
    for entry_persistence in [10]:
        for period in [14]:
            for multiplier in [9]:
                for cci_period in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 25]:
                    fv, sqn = evaluate((compression, entry_persistence, period, multiplier, cci_period))
                    results.append(f'compression: {compression}, entry_persistence {entry_persistence}, period {period}, multiplier {multiplier}, sqn {sqn}, cci_period {cci_period}')

for result in results:
    print(result)
