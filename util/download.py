
import datetime as dt
import pandas as pd
import numpy as np
import requests

from io import StringIO
from dateutil import parser


GOOGLE_URL = "http://finance.google.com/finance/historical?q=BMV:{symbol}&startdate={startdate}&enddate={enddate}&output=csv"
N_YEARS = 2


def get_dates():
    now = dt.datetime.now()
    year, month, day = now.year, now.month, now.day
    startdate = str(day).zfill(2) + str(month).zfill(2) + str(year-N_YEARS)
    enddate = now.strftime("%d%m%Y")
    return startdate, enddate


def get_request_content(url):
    r = requests.get(url=url)
    return r.text


def get_data(stock):
    startdate, enddate = get_dates()
    string_data = get_request_content(GOOGLE_URL.format(
        symbol=stock,
        startdate=startdate,
        enddate=enddate
    ))
    df = pd.read_csv(StringIO(string_data))
    price = df[["Close"]]
    price.index = df.Date.apply(lambda x: parser.parse(x), 1)
    return price.sort_index()


def get_multiple_data(list_stocks):
    dfs = [get_data(s) for s in list_stocks]
    df = pd.concat(dfs, 1).dropna()
    df.columns = list_stocks
    return df


def get_returns(df):
    return df.apply(calculate_returns, 0)


def calculate_returns(prices):
    prices = np.array(prices)
    return [0] + list(prices[1:] / prices[:-1] - 1)



