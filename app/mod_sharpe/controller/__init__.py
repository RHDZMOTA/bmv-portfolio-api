import json

from flask import Blueprint, request
from app import db

#from app.mod_stocks.service import StatisticsService
from util.sharpe_procedure import find_max_sharpe

mod_sharpe = Blueprint('sharpe', __name__, url_prefix='/sharpe')


@mod_sharpe.route('/', methods=['GET', 'POST'])
def get_index():
    return "Sharpe"


@mod_sharpe.route('/create', methods=['GET', 'POST'])
def create_portfolio():
    stock_string_list = request.args.get("stocks")
    try:
        stock_list = eval(stock_string_list)
    except:
        stock_list = []

    if len(stock_list) < 2:
        return json.dumps({"Error": "Not enough stocks ( < 2)."})

    try:
        max_sharpe_results = find_max_sharpe(stock_list)
    except:
        return json.dumps({"Error": "Sharpe procedure couldn't be performed."})

    return json.dumps(max_sharpe_results)

