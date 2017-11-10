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

    return jsonify(result)

