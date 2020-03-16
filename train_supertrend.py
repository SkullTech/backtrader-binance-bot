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
    (compression, entry_persistence, period, multiplier) = args
    compression = int(compression)
    entry_persistence = int(entry_persistence)
    period = int(entry_persistence)

    cerebro = bt.Cerebro(quicknotify=True)
    data = BinanceDataset(
        name=COIN_TARGET,
        dataname="dataset/binance_btc_cumulated_1m_klines.csv",
        timeframe=bt.TimeFrame.Minutes,
        fromdate=dateparser.parse('1 Jan 2019'),
        todate=dateparser.parse('1 Feb 2019'),
        nullvalue=0.0
    )

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=compression)
    broker = cerebro.getbroker()
    broker.setcommission(commission=0.001, name=COIN_TARGET)
    broker.setcash(100000.0)
    cerebro.addsizer(PragmaticSizer)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    cerebro.addstrategy(SuperTrendCCIStrategy, entry_persistence=entry_persistence, supertrend_period=period, supertrend_multiplier=multiplier)

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
for compression in [30, 45, 60]:
    for entry_persistence in [3, 5, 10]:
        for period in [5, 10, 20]: 
            for multiplier in [1.5, 2, 3]:
                fv, sqn = evaluate((compression, entry_persistence, period, multiplier))
                results.append(f'compression: {compression}, entry_persistence {entry_persistence}, period {period}, multiplier {multiplier}, sqn {sqn}')

for result in results:
    print(result)
