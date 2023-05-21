import json
import sched
import time

import requests
from flask import Blueprint, request, session, jsonify

from constants import BANK_ADDRESS, ETHERSCAN_API_KEY, BSNSCAN_API_KEY

# from flask_login import login_required

# from db_access import db_create_deposit, db_set_deposit_status_complete, db_add_balance
# from utils import translations

wallet = Blueprint('wallet', __name__)


def verify_transaction_loop(deposit):
    if request.json['chain'] == 'erc20':
        request_url = 'https://api.etherscan.io/api?module=account&action=txlist&address=' + BANK_ADDRESS + '&startblock=0&endblock=99999999&page=1&offset=200&sort=desc&apikey=' + ETHERSCAN_API_KEY
    elif request.json['chain'] == 'goerli':
        request_url = 'https://api-goerli.etherscan.io/api?module=account&action=txlist&address=' + BANK_ADDRESS + '&startblock=0&endblock=99999999&page=1&offset=200&sort=desc&apikey=' + ETHERSCAN_API_KEY
    elif request.json['chain'] == 'bep20test':
        request_url = 'https://api-testnet.bscscan.com/api?module=account&action=txlist&address=' + BANK_ADDRESS + '&startblock=0&endblock=99999999&page=1&offset=200&sort=desc&apikey=' + BSNSCAN_API_KEY
    elif request.json['chain'] == 'bep20':
        request_url = 'https://api.bscscan.com/api?module=account&action=txlist&address=' + BANK_ADDRESS + '&startblock=0&endblock=99999999&page=1&offset=200&sort=desc&apikey=' + BSNSCAN_API_KEY

    response = requests.get(request_url)
    data = json.loads(response.text)
    amount = 0
    # check response for the txHash
    for transaction in data['result']:
        if transaction['hash'] == request.json['txHash']:
            if request.json['chain'] == 'erc20' or request.json['chain'] == 'goerli':
                if deposit.currency == 'eth':
                    amount = float(transaction['value']) / (10 ** 18)
            # elif request.json['chain'] == 'bep20test':
            # elif request.json['chain'] == 'bep20':
            # amount = deposit.amount
            # amount = transaction['value']

    # amount only non-blank if txHash found
    if amount > 0:
        # save to deposits db
        deposit.mark_complete()
        # db_set_deposit_status_complete(request.json)
        return amount
    else:
        deposit.mark_failed()
        return 0


# @wallet.route('/verify_transaction', methods=['POST'])
# @login_required
# def verify_transaction():
#     run = True
#     count = 0
#     start_time = time.time()
#     # check if deposit exists
#     email = session['email']
#     # email = 'lele@gmeow.com'
#
#     # db_create_deposit(session['email'], request.json)
#     db_create_deposit(email, request.json)
#
#     while run:
#         if count < 6:
#             count += 1
#             print("count: " + str(count))
#             amount = verify_transaction_loop(count)
#             if amount > 0:
#                 # update user db
#                 db_add_balance(email, amount, request.json['currency'])
#                 return amount
#             time.sleep(10.0 - ((time.time() - start_time) % 10.0))
#
#     return jsonify(amount=amount)
