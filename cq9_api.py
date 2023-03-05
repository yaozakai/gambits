import requests
import json
from flask import Blueprint, jsonify, request
from db_access import db_getuser_username, db_bet, db_endround, db_check_mtcode, db_rollout, db_refund, db_get_bet, \
    db_rollin, db_takeall
from utils import get_timestamp, check_token, authKey, url
from config import app


# from database import app


# myobj = {'somekey': 'somevalue'}


cq9_api = Blueprint('cq9_api', __name__, template_folder='templates')
# @cq9_api.route('/loadGames', methods=['GET', 'POST'])
# def game_list():
#     myobj = {'Authorization': authKey, 'Content-Type': 'application/json; charset=UTF-8'}
#     x = requests.get(url + 'game/list/cq9', headers=myobj)
#     for key in x.json()['data']:
#         print(x.text)


def game_history(username):
    header = {'Authorization': authKey, 'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'account': username, 'gamehall': 'cq9', 'gameplat': 'WEB',
        'lang': 'en'
    }
    x = requests.post(url + 'gameboy/player/sw/gamelink', headers=header, data=body)
    launch_url = json.loads(x.text)['data']['url']
    return launch_url


def game_launch(username, game_code):
    header = {'Authorization': authKey, 'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'account': username, 'gamehall': 'cq9', 'gameplat': 'WEB',
        'gamecode': game_code, 'lang': 'en'
    }
    x = requests.post(url + 'gameboy/player/sw/gamelink', headers=header, data=body)
    launch_url = json.loads(x.text)['data']['url']
    return launch_url


@cq9_api.route('/cq9/player/check/<username>', methods=['GET'])
def cq9_check(username):
    if check_token():
        datetime = get_timestamp()
        user_exists = db_getuser_username(username) is not None

        model = {
              "data": user_exists,
              "status": {
                "code": "0",
                "message": "Success",
                "datetime": datetime
              }
            }

        return jsonify(model)


@cq9_api.route('/cq9/transaction/balance/<username>', methods=['GET', 'POST'])
def cq9_balance(username):
    if check_token():
        datetime = get_timestamp(False)
        user = db_getuser_username(username)

        model = {
              "data": {
                "balance": float(user.balance),
                "currency": "USD"
              },
              "status": {
                "code": "0",
                "message": "Success",
                "datetime": datetime
              }
            }

        return jsonify(model)


@cq9_api.route('/cq9/transaction/game/bet', methods=['POST'])
def cq9_bet():
    if check_token() and db_check_mtcode():
        # if db_getuser_username(request.form['account']) is not None:
        balance = db_bet()
        if balance > 0:
            error_code = '0'
        else:
            error_code = '1003'
        model = {
            "data": {
                "balance": balance,
                "currency": "USD"
            },
            "status": {
                "code": error_code,
                "message": "Success",
                "datetime": get_timestamp()
            }
        }
        return jsonify(model)


@cq9_api.route('/cq9/transaction/game/endround', methods=['POST'])
def cq9_endround():
    if check_token() and db_check_mtcode():
        # if db_getuser_username(request.form['account']) is not None:
        balance = db_endround()
        if balance > 0:
            error_code = '0'
        else:
            error_code = '1003'
        model = {
            "data": {
                "balance": round(balance, 4),
                "currency": "USD"
            },
            "status": {
                "code": error_code,
                "message": "Success",
                "datetime": get_timestamp()
            }
        }
        return jsonify(model)


@cq9_api.route('/cq9/transaction/game/credit', methods=['POST'])
def cq9_credit():
    if check_token():
        pass


@cq9_api.route('/cq9/transaction/game/rollout', methods=['POST'])
def cq9_rollout():
    if check_token() and db_check_mtcode():
        # if db_getuser_username(request.form['account']) is not None:
        balance = db_rollout()
        if balance > 0:
            error_code = '0'
        else:
            error_code = '1003'
        model = {
            "data": {
                "balance": round(balance, 4),
                "currency": "USD"
            },
            "status": {
                "code": error_code,
                "message": "Success",
                "datetime": get_timestamp()
            }
        }
        return jsonify(model)


@cq9_api.route('/cq9/transaction/game/rollin', methods=['POST'])
def cq9_rollin():
    if check_token():
        if db_check_mtcode():
            error_code = '2009'
            balance = 0
        else:
            # if db_getuser_username(request.form['account']) is not None:
            balance = db_rollin()
            if balance > 0:
                error_code = '0'
            else:
                error_code = '1003'
        model = {
            "data": {
                "balance": round(balance, 4),
                "currency": "USD"
            },
            "status": {
                "code": error_code,
                "message": "Success",
                "datetime": get_timestamp()
            }
        }
        return jsonify(model)


@cq9_api.route('/cq9/transaction/game/takeall', methods=['POST'])
def cq9_takeall():
    if check_token() and db_check_mtcode():
        if db_getuser_username(request.form['account']) is not None:
            balance = db_takeall()

            model = {
                "data": {
                    "amount": round(balance, 4),
                    "balance": 0,
                    "currency": "USD"
                },
                "status": {
                    "code": '0',
                    "message": "Success",
                    "datetime": get_timestamp()
                }
            }
            return jsonify(model)


@cq9_api.route('/cq9/transaction/game/refund', methods=['POST'])
def cq9_refund():
    if check_token() and db_check_mtcode():
        # make sure bet exists
        if db_get_bet(request.form['mtcode']) is not None:
            balance = db_refund()
            if balance > 0:
                error_code = '0'
            else:
                error_code = '1003'
            model = {
                "data": {
                    "balance": round(balance, 4),
                    "currency": "USD"
                },
                "status": {
                    "code": error_code,
                    "message": "Success",
                    "datetime": get_timestamp()
                }
            }
            return jsonify(model)
