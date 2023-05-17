import json
import sched
import time

import requests
from flask import Blueprint, request, session, jsonify

from db_access import db_create_deposit, db_verify_deposit_status, db_add_balance
from utils import translations

wallet = Blueprint('wallet', __name__)


def verify_transaction_loop(page):
    if request.json['chain'] == 'erc20':
        request_url = 'https://api.etherscan.io/api?module=account&action=txlist&address=0x6E38B4dc98854E5CA41db2F9AfaCE7F7656ab33B&startblock=0&endblock=99999999&page=' + str(
            page) + '&offset=300&sort=asc&apikey=PUXKJQAECKT16NJFHJTEB6UVYSKH7F2Z8Q'
    elif request.json['chain'] == 'goerli':
        request_url = 'https://api-goerli.etherscan.io/api?module=account&action=txlist&address=0x6E38B4dc98854E5CA41db2F9AfaCE7F7656ab33B&startblock=0&endblock=99999999&page=' + str(
            page) + '&offset=300&sort=asc&apikey=PUXKJQAECKT16NJFHJTEB6UVYSKH7F2Z8Q'
    elif request.json['chain'] == 'bep20test':
        request_url = 'https://api-testnet.bscscan.com/api?module=account&action=txlist&address=0x6E38B4dc98854E5CA41db2F9AfaCE7F7656ab33B&startblock=0&endblock=99999999&page=' + str(
            page) + '&offset=300&sort=asc&apikey=49ECAJH85URFXKPMF55CFRYYGG68EP5TTS'
    elif request.json['chain'] == 'bep20':
        request_url = 'https://api.bscscan.com/api?module=account&action=txlist&address=0x6E38B4dc98854E5CA41db2F9AfaCE7F7656ab33B&startblock=0&endblock=99999999&page=' + str(
            page) + '&offset=300&sort=asc&apikey=49ECAJH85URFXKPMF55CFRYYGG68EP5TTS'

    response = requests.get(request_url)
    data = json.loads(response.text)
    amount = ''
    # check for the txHash
    for transaction in data['result']:
        if transaction['hash'] == request.json['txHash']:
            amount = transaction['value']

    # amount only non-blank if txHash found
    if len(amount) > 0:
        # save to deposits db
        db_verify_deposit_status(request.json['txHash'])
        return amount
    else:
        return 0


@wallet.route('/verify_transaction', methods=['POST'])
# @login_required
def verify_transaction():
    run = True
    count = 0
    start_time = time.time()
    # check if deposit exists
    email = session['email']
    # email = 'lele@gmeow.com'

    # db_create_deposit(session['email'], request.json)
    db_create_deposit(email, request.json)

    while run:
        if count < 6:
            count += 1
            print("count: " + str(count))
            amount = verify_transaction_loop(count)
            if amount > 0:
                # update user db
                db_add_balance(email, amount, request.json['currency'])
                return amount
            time.sleep(10.0 - ((time.time() - start_time) % 10.0))

    return jsonify(amount=amount)
