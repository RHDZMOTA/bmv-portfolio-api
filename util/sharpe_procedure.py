
import numpy as np
import pandas as pd
import scipy.optimize as sco

from util.download import get_multiple_data, get_returns

RISK_FREE = 0.065

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
        print(missing_tickers)
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


data_holder = TemporalDataHolder()


def get_portfolio_params(tickers, weights):
    returns = data_holder.get_returns_df(tickers)
    rp = 360 * sum(weights * returns.mean().values)
    sd = np.sqrt(360 * np.asscalar((np.asmatrix(weights).dot(np.asmatrix(returns.cov()))).dot(np.asmatrix(weights).T)))
    return rp, sd


def simple_sharpe(rp, sd, rf):
    return (rp-rf)/sd


def sharpe_function(weights, tickers):
    rp, sd = get_portfolio_params(tickers, weights)
    return simple_sharpe(rp, sd, RISK_FREE)


def objective_function(x, tickers):
    return -sharpe_function(weights=x, tickers=tickers)


def loose_decimals(z):
    return int(100*z)/100


def find_max_sharpe(tickers):
    n = len(tickers)
    args = (tickers)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for i in range(n))
    opts = sco.minimize(objective_function, n * [1. / n, ],
                        method='SLSQP',
                        bounds=bounds,
                        constraints=constraints,
                        args=args)

    return {
        "sharpe": sharpe_function(opts.x, tickers=tickers),
        "stocks": tickers,
        "weights": [loose_decimals(100 * i) for i in opts.x],
        "risk-free-rate": RISK_FREE
    }
