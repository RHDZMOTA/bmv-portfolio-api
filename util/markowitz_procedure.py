
import pandas as pd
import numpy as np

from cvxopt import matrix, solvers
from util import data_holder


def random_portfolio(returns):
    w = np.asmatrix(np.random.dirichlet(np.ones(returns.shape[1]), size=1)[0])
    rp = w.dot(np.asmatrix(returns.mean().values).T)
    rp = np.asscalar(rp)
    varp = w.dot(np.asmatrix(returns.cov().values)).dot(w.T)
    varp = np.asscalar(varp)
    return rp, np.sqrt(varp)


def generate_multiple_portfolios(m, returns):
    results = {'rp': [], 'std': []}
    for i in range(m):
        temp = random_portfolio(returns)
        results['rp'].append(100 * temp[0])
        results['std'].append(100 * temp[1])
    return pd.DataFrame(results)


def calculate_portfolio(w, returns):
    rp = w.dot(np.asmatrix(returns.mean().values).T)
    rp = np.asscalar(rp)
    varp = w.dot(np.asmatrix(returns.cov().values)).dot(w.T)
    varp = np.asscalar(varp)
    return 100 * rp, 100 * np.sqrt(varp)


class Markowitz(object):

    alive = False

    def __init__(self):
        self.alpha_to_range = np.arange(1, 500)
        self.port_opt = None

    def __enter__(self):
        if not self.alive:
            self.alive = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Close all
        if self.alive:
            self.alive = False

    def get_solution(self, returns, alpha_1=1, alpha_2=1):
        solvers.options['show_progress'] = False
        r = returns.shape[1]  # number of vars
        mu = returns.mean()
        covs = returns.cov()
        # PARAMETERS FOR QUADRATIC PROGRAMMING
        P = matrix(alpha_2 * covs.values)
        Q = matrix(-alpha_1 * mu.values)
        G = matrix(-1. * np.identity(r))
        h = matrix([0. for i in range(r)])
        A = matrix([1. for i in range(r)], (1, r))
        b = matrix(1.)
        # SOLUTION
        sol = solvers.qp(P, Q, G, h, A, b)
        return np.asmatrix([i for i in sol['x']])

    def iterative_selection_process(self, returns, w_opt_list=None, tolerance=0.05, alpha_to_range=np.arange(1,500)):
        if w_opt_list is None:
            w_opt_list = [self.get_solution(returns, alpha_2=a2) for a2 in alpha_to_range]
        save_sum = []
        for i in w_opt_list:
            temp = [i[0, j] for j in range(np.shape(i)[1])]
            save_sum = (save_sum + np.array(temp)) if len(save_sum) != 0 else np.array(temp)
        selection = pd.DataFrame(save_sum).apply(lambda x: x > tolerance).values
        cont = len(selection) - np.sum(selection)
        self.selection = [j for i, j in zip(selection, returns.columns) if i]
        return returns[self.selection], cont, save_sum

    def get_weights(self, tickers):
        condition = True
        w_opt_list = None
        returns = data_holder.get_returns_df(tickers)
        while condition:
            returns, cond, ss = self.iterative_selection_process(returns, w_opt_list, tolerance=0.05 * 500)
            w_opt_list = [self.get_solution(returns, alpha_2=a2) for a2 in np.arange(1, 500)]
            condition = False if cond == 0 else condition
        self.returns = returns
        self.w_opt_list = w_opt_list

    def simulate_rand_port(self):
        self.portfolios = generate_multiple_portfolios(5000, self.returns)

    def generate_efficient_frontier(self):
        port_opt = []
        for i in self.w_opt_list:
            port_opt.append(calculate_portfolio(i, self.returns))

        self.port_opt = pd.DataFrame(port_opt)
        self.port_opt.columns = ['returns', 'volatility']
        self.port_opt.index = self.alpha_to_range

    def get_it_done(self, tickers='all'):
        self.get_weights(tickers)
        self.simulate_rand_port()
        self.generate_efficient_frontier()

    def get_efficient_portfolio(self, tickers, percentile=0):
        self.get_it_done(tickers)
        length = len(self.port_opt)
        select = int(np.percentile(np.arange(length), 100 - percentile))
        desc = self.port_opt.iloc[[select]]
        desc = desc.T.values
        weights = pd.DataFrame(100 * self.w_opt_list[select], columns=self.returns.columns, index=[select])
        return {
            "frontier-percentile": percentile,
            "weights": weights.values.tolist()[0],
            "stocks": list(weights.columns.values),
            "daily-return": desc[0].item(),
            "daily-volatility": desc[-1].item(),
            "annual-return": 360*desc[0].item(),
            "annual-volatility": np.sqrt(360)*desc[-1].item()
        }
