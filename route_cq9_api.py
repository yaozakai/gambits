from datetime import timedelta

import requests
from flask import Blueprint, jsonify

import utils
from constants import CQ9_KEY
from utils import get_timezone
from db_access import *
from utils import get_timestamp, check_token, url

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

    header = {'Authorization': CQ9_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
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
    header = {'Authorization': CQ9_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'account': username, 'gamehall': 'cq9', 'gameplat': 'WEB',
        'gamecode': gamecode, 'lang': session['lang']
    }
    x = requests.post(url + 'gameboy/player/sw/gamelink', headers=header, data=body)

    try:
        launch_url = json.loads(x.text)['data']['url']
    except:
        launch_url = ''
    return launch_url


@cq9_api.route('/cq9/player/check/<username>', methods=['GET', 'POST'])
def cq9_check(username):
    error_code = '0'
    time_stamp = get_timestamp()
    user_exists = False

    if check_token():
        if db_getuser_username(username) is None:
            error_code = '2'
        else:
            user_exists = True
    else:
        error_code = '3'

    model = {
          "data": user_exists,
          "status": {
            "code": error_code,
            "message": "Success",
            "datetime": time_stamp
          }
        }

    return jsonify(model)


@cq9_api.route('/cq9/transaction/balance/<username>', methods=['GET', 'POST'])
def cq9_balance(username):
    error_code = '0'
    time_stamp = get_timestamp(False)
    user = db_getuser_username(username)

    if check_token():
        if user is None:
            error_code = '2'
        else:
            pass
    else:
        error_code = '3'

    model = {
        "data": {
            "balance": float(user.balance_usdt),
            "currency": "USDT"
        },
        "status": {
            "code": error_code,
            "message": "Success",
            "datetime": time_stamp
        }
    }

    return jsonify(model)


@cq9_api.route('/cq9/transaction/game/bet', methods=['POST'])
def cq9_bet():
    error_code = '0'
    # time_stamp = get_timestamp(False)
    # user = db_getuser_username(username)
    if float(request.form['amount']) < 0:
        error_code = '1003'
    else:
        if check_token():
            if db_check_mtcode_bet():
                error_code = '9'
            else:
                pass
        else:
            error_code = '3'

    # new_balance will be -1 if rejected
    new_balance = db_bet()
    if not new_balance['valid']:
        error_code = '1005'

    model = {
        "data": {
            "balance": new_balance['balance'],
            "currency": "USDT"
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
    error_code = '0'
    balance = 0

    if check_token():
        # bets = BetEntry().query.filter_by(roundid=request.form['roundid'])
        # db_check_roundid()
        balance = db_endround()
    else:
        error_code = '3'

        # and db_check_roundid():


        # if db_getuser_username(request.form['account']) is not None:

    model = {
        "data": {
            "balance": f'{balance:.2f}',
            "currency": "USDT"
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
    error_code = '0'
    # time_stamp = get_timestamp(False)
    # user = db_getuser_username(username)
    if float(request.form['amount']) < 0:
        error_code = '1003'
    else:
        if check_token():
            entry_exists = RolloutEntry().check_mtcode(request.form['mtcode'])
            if entry_exists:
                error_code = '9'
            else:
                pass
        else:
            error_code = '3'

    # new_balance will be -1 if rejected
    new_balance = db_rollout()
    if not new_balance['valid']:
        error_code = '1005'

    model = {
        "data": {
            "balance": new_balance['balance'],
            "currency": "USDT"
        },
        "status": {
            "code": error_code,
            "message": "Success",
            "datetime": get_timestamp()
        }
    }
    return jsonify(model)
# def cq9_rollout():
#     if check_token():
#         # if db_getuser_username(request.form['account']) is not None:
#         balance = db_rollout()
#         if balance >= 0:
#             error_code = '0'
#         else:
#             error_code = '1003'
#         model = {
#             "data": {
#                 "balance": f'{balance:.2f}',
#                 "currency": "USDT"
#             },
#             "status": {
#                 "code": error_code,
#                 "message": "Success",
#                 "datetime": get_timestamp()
#             }
#         }
#         return jsonify(model)


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
                "balance": balance,
                "currency": "USDT"
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
                    "amount": f'{balance:.2f}',
                    "balance": 0,
                    "currency": "USDT"
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
    balance = 0
    error_code = '0'
    if check_token():
        txn = db_refund_find_txn()

        if db_refund_exists():
            error_code = '9'
        else:
            if txn is None:
                # missing the bet/rollout that matches this refund request
                error_code = '1014'
            else:
                balance = db_refund(txn)
    else:
        error_code = '3'

    model = {
        "data": {
            "balance": balance,
            "currency": "USDT"
        },
        "status": {
            "code": error_code,
            "message": "Success",
            "datetime": get_timestamp()
        }
    }
    return jsonify(model)
