from datetime import timedelta, timezone

import requests
from flask import Blueprint, jsonify

import utils
from utils import get_timezone
from db_access import *
from utils import get_timestamp, check_token, authKey, url

cq9_api = Blueprint('cq9_api', __name__, template_folder='templates')


def player_report_today(username, date):
    if type(date) != str:
        start_time = date - timedelta(days=1)
        start_time = start_time.isoformat()
        end_time = date.isoformat()
    else:
        tz = get_timezone()
        end_time = datetime.strptime(date, "%Y-%m-%d").replace(hour=23, minute=59, tzinfo=tz)
        start_time = end_time.replace(hour=0, minute=0, tzinfo=tz)
        start_time = start_time.isoformat()
        end_time = end_time.isoformat()

    header = {'Authorization': authKey, 'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        # 'starttime': get_bod_timestamp(),
        'starttime': start_time,
        # 'endtime': get_eod_timestamp(),
        'endtime': end_time,
        'page': 1,
        'account': username,
        'pagesize': 30
    }
    x = requests.get(url + 'gameboy/order/view', headers=header, params=body)
    report_data = json.loads(x.text)['data']

    if report_data is not None:
        # replace gamecode with gamename
        for row in report_data['Data']:
            for game in utils.game_titles:
                if game['gamecode'] == row['gamecode']:
                    row['gamecode'] = game['gamename']

    return report_data


def game_launch(username, gamecode):
    header = {'Authorization': authKey, 'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'account': username, 'gamehall': 'cq9', 'gameplat': 'WEB',
        'gamecode': gamecode, 'lang': 'en'
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
    if check_token() and not db_check_mtcode_bet():
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
    if check_token() and db_check_roundid():
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
    if check_token():
        # if db_getuser_username(request.form['account']) is not None:
        balance = db_rollout()
        if balance >= 0:
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
        if db_check_mtcode_rollin():
            error_code = '2009'
            balance = 0
            message = 'Transaction already processed'
        else:
            # if db_getuser_username(request.form['account']) is not None:
            balance = db_rollin()
            message = 'Success'
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
                "message": message,
                "datetime": get_timestamp()
            }
        }
        return jsonify(model)


@cq9_api.route('/cq9/transaction/game/takeall', methods=['POST'])
def cq9_takeall():
    if check_token() and db_check_mtcode_bet():
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
    if check_token() and db_check_mtcode() and not db_refund_exists():
        # make sure bet exists
        # if db_get_bet(request.form['mtcode']) is not None:
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
