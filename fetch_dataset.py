from binance.client import Client
import pandas as pd
import yaml
import argparse

with open('secrets.yaml') as f:
    secrets = yaml.load(f, Loader=yaml.FullLoader)


parser = argparse.ArgumentParser(description='Binance BTC/USDT historical klines dataset downloader.')
parser.add_argument('-f', '--fromdate', required=True, type=str, help='Start date')
parser.add_argument('-t', '--todate', required=True, type=str, help='End date')
parser.add_argument('-o', '--output', type=str, default='dataset/binance_1m_klines.csv', help='Output CSV file name.')
args = parser.parse_args()


client = Client(secrets['Binance']['APIKey'], secrets['Binance']['SecretKey'])
klines = client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, args.fromdate, args.todate)
data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data.to_csv(args.output, index=False)
