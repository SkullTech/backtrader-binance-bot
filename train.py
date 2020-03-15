import time
import dateparser
import argparse
import backtrader as bt
import datetime as dt
from config import secrets, ENV, PRODUCTION, COIN_TARGET, COIN_REFER, DEBUG

from dataset.dataset import BinanceDataset
from sizer.percent import FullMoney
from strategies.basic import MACDStrategy
from utils import print_trade_analysis, print_sqn, send_telegram_message


compression = 35
entry_persistence = 5
macd_band = 20
results = []


for compression in [30, 45, 60, 90]:
    for entry_persistence in [5, 8, 10, 15]: 
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
        cerebro.addsizer(FullMoney)
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

        cerebro.addstrategy(MACDStrategy, entry_persistence=entry_persistence, macd_band=macd_band)

        initial_value = cerebro.broker.getvalue()
        print('Starting Portfolio Value: %.2f' % initial_value)
        result = cerebro.run()

        # Print analyzers - results
        final_value = cerebro.broker.getvalue()

        print('Final Portfolio Value: %.2f' % final_value)
        print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))
        # print_trade_analysis(result[0].analyzers.ta.get_analysis())
        sqn = print_sqn(result[0].analyzers.sqn.get_analysis())
        results.append(f'compression: {compression}, entry_persistence {entry_persistence}, macd_band {macd_band}, sqn {sqn}')
        print(results)

print(results)
