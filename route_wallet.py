import json

import requests
from flask import Blueprint, request

wallet = Blueprint('wallet', __name__)


@wallet.route('/verify_transaction', methods=['POST'])
# @login_required
def verify_transaction():
    if request.json['chain'] == 'erc20':
        request_url = 'https://api.etherscan.io/api?module=account&action=txlist&address=0x7d5eb381B479a663aC09CcDCbd38b298CE304608&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey=PUXKJQAECKT16NJFHJTEB6UVYSKH7F2Z8Q'
    elif request.json['chain'] == 'goerli':
        request_url = 'https://api-goerli.etherscan.io/api?module=account&action=txlist&address=0x7d5eb381B479a663aC09CcDCbd38b298CE304608&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey=PUXKJQAECKT16NJFHJTEB6UVYSKH7F2Z8Q'
    elif request.json['chain'] == 'bep20test':
        request_url = 'https://api-testnet.bscscan.com/api?module=account&action=txlist&address=0x7d5eb381B479a663aC09CcDCbd38b298CE304608&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey=49ECAJH85URFXKPMF55CFRYYGG68EP5TTS'
    elif request.json['chain'] == 'bep20':
        request_url = 'https://api.bscscan.com/api?module=account&action=txlist&address=0x7d5eb381B479a663aC09CcDCbd38b298CE304608&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey=49ECAJH85URFXKPMF55CFRYYGG68EP5TTS'

    response = requests.get(request_url)
    data = json.loads(response.text)
# check for the txHash
    for transaction in data['result']:
        if transaction['hash'] == request.json['txHash']:
            return transaction['value']
        