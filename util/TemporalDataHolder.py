
import pandas as pd
import numpy as np

from util.download import get_multiple_data, get_returns


class TemporalDataHolder(object):

    tickers = []

    def __init__(self):
        self.tickers = []
        self.prices = pd.DataFrame([])
        self.returns = pd.DataFrame([])

    def get_prices_df(self, tickers):
        if not len(tickers):
            return self.prices
        missing_tickers = [ticker for ticker in tickers if ticker not in self.tickers]
        if not len(missing_tickers):
            return self.prices
        missing_data = get_multiple_data(missing_tickers)
        data = pd.concat([missing_data, self.prices], 1).dropna()
        self.prices = data
        self.tickers = list(data.columns)
        return data[tickers]

    def get_returns_df(self, tickers):
        df = self.get_prices_df(tickers)
        self.returns = get_returns(df)
        return self.returns[tickers]
