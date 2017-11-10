import json

from flask import Blueprint, request, jsonify
from app import db

from util.markowitz_procedure import Markowitz

mod_markowitz = Blueprint('markowitz', __name__, url_prefix='/markowitz')


@mod_markowitz.route('/', methods=['GET', 'POST'])
def get_index_markowitz():
    return "Markowitz"




@mod_markowitz.route('/create', methods=['GET', 'POST'])
def create_portfolio_markowitz():
    stock_string_list = request.args.get("stocks")
    percentile = request.args.get("percentile")
    not_string = request.args.get("not_string")
    try:
        stock_list = eval(stock_string_list)
        percentile = float(percentile)
    except:
        stock_list = []

    if len(stock_list) < 2:
        return json.dumps({"Error": "Not enough stocks ( < 2)."})

    try:
        with Markowitz() as mark:
            result = mark.get_efficient_portfolio(tickers=stock_list, percentile=percentile)
    except:
        return jsonify({"Error": "Markowitz procedure couldn't be performed."})

    def create_string_result(resp):
        ans = """
            **Markowitz Portfolio**

            - *Percentile*: {p}
            - *Annual return*: {annual_return}
            - *Annual volatility*: {annual_volatility}
            """.format(
            p=str(resp["frontier-percentile"]),
            annual_return=str(resp["annual-return"]),
            annual_volatility=str(resp["annual-volatility"])
        ).replace('            ', "")
        for key in resp:
            if key in ["frontier-percentile", "annual-return", "annual-volatility", "daily-return", "daily-volatility"]:
                continue
            ans += "\n- *{key}*: {val}".format(key=key, val=resp[key])
        return ans

    if not_string:
        return jsonify(result)
    return create_string_result(result)

