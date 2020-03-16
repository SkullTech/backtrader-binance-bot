#!/usr/bin/env python3

import time
import dateparser
import argparse
import backtrader as bt
import datetime as dt

from ccxtbt import CCXTStore
from config import secrets, ENV, PRODUCTION, COIN_TARGET, COIN_REFER, DEBUG

from dataset.dataset import BinanceDataset, NIFTY50Dataset
from sizer.pragmatic import PragmaticSizer
from strategies.macd import MACDStrategy
from strategies.supertrend_cci import SuperTrendCCIStrategy
from utils import print_trade_analysis, print_sqn, send_telegram_message


def main(args):
    cerebro = bt.Cerebro(quicknotify=True)

    if ENV == PRODUCTION:  # Live trading with Binance
        broker_config = {
            'apiKey': secrets['BINANCE']['APIKey'],
            'secret': secrets['BINANCE']['SecretKey'],
            'nonce': lambda: str(int(time.time() * 1000)),
            'enableRateLimit': True,
        }

        store = CCXTStore(exchange='binance', currency=COIN_REFER, config=broker_config, retries=5, debug=DEBUG)

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.Stop: 'stop-loss',
                bt.Order.StopLimit: 'stop limit'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'status',
                    'value': 'canceled'
                }
            }
        }

        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)

        hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=30000)
        data = store.getdata(
            dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
            name='%s%s' % (COIN_TARGET, COIN_REFER),
            timeframe=bt.TimeFrame.Minutes,
            fromdate=hist_start_date,
            compression=30,
            ohlcv_limit=99999
        )

        # Add the feed
        cerebro.adddata(data)

    else:  # Backtesting with CSV file
        data = BinanceDataset(
            name=COIN_TARGET,
            dataname="dataset/binance_btc_cumulated_1m_klines.csv",
            timeframe=bt.TimeFrame.Minutes,
            fromdate=dateparser.parse(args.fromdate),
            todate=dateparser.parse(args.todate),
            nullvalue=0.0
        )
        # data = NIFTY50Dataset(
        #     name='NIFTY50',
        #     dataname='dataset/NIFTY50/TATAMOTORS/TATAMOTORS_FEB.txt',
        #     timeframe=bt.TimeFrame.Minutes,
        #     nullvalue=0.0
        # )

        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=args.compression)

        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001, name=COIN_TARGET)  # Simulating exchange fee
        broker.setcash(100000.0)
        cerebro.addsizer(PragmaticSizer, cashlimit=100000)
        # cerebro.addsizer(bt.sizers.AllInSizer)

    # Analyzers to evaluate trades and strategies
    # SQN = Average( profit / risk ) / StdDev( profit / risk ) x SquareRoot( number of trades )
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Include Strategy
    if args.strategy == 'supertrend':
        cerebro.addstrategy(SuperTrendCCIStrategy)
    elif args.strategy == 'macd':
        cerebro.addstrategy(MACDStrategy)

    # Starting backtrader bot
    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    result = cerebro.run()

    # Print analyzers - results
    final_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final_value)
    print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))
    # print_trade_analysis(result[0].analyzers.ta.get_analysis())
    print_sqn(result[0].analyzers.sqn.get_analysis())

    if DEBUG:
        cerebro.plot()


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--fromdate', required=True, type=str, help='From date')
        parser.add_argument('-t', '--todate', required=True, type=str, help='To date')
        parser.add_argument('-c', '--compression', required=True, type=int, help='Compression')
        parser.add_argument('-s', '--strategy', required=True, type=str, help='Strategy')
        args = parser.parse_args()
        main(args)
    except KeyboardInterrupt:
        print("finished.")
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        send_telegram_message("Bot finished by user at %s" % time)
    except Exception as err:
        send_telegram_message("Bot finished with error: %s" % err)
        print("Finished with error: ", err)
        raise
