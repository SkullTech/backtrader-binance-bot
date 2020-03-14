import os
import yaml

with open('secrets.yaml') as f:
    secrets = yaml.load(f, Loader=yaml.FullLoader)

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "BTC"
COIN_REFER = "USDT"

ENV = os.getenv("ENVIRONMENT", DEVELOPMENT)
DEBUG = True

print("ENV = ", ENV)
