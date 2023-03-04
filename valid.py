from db_classes import db_check_userid_with_sid
from db_access import db_search_userid
from utils import send_json
from flask import request


def valid_token_id(valid=True):
    if valid:
        if 'authToken' in request.args and request.args['authToken'] == 's3cr3tV4lu3':
            return True
        else:
            return False
    else:
        return send_json('INVALID_TOKEN_ID')


def valid_user(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        if 'userId' in request_data:
            return request_data['userId']
        else:
            return False

    else:
        return send_json('INVALID_PARAMETER')


def match_userid_sid(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        if db_search_userid(request_data['userId']):
            return request_data['userId']
        else:
            return False
    else:
        return send_json('INVALID_PARAMETER')


def valid_check_user(userid, uuid):
    request_data = request.get_json(force=True)

    if db_check_userid_with_sid(userid, request_data['sid']):
        return send_json("OK", request_data['sid'], uuid)
    else:
        return send_json('INVALID_PARAMETER')


def valid_uuid(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        if 'uuid' in request_data:
            return request_data['uuid']
        else:
            return False

    else:
        return send_json('INVALID_PARAMETER')


def valid_sid(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        return 'sid' in request_data
    else:
        return send_json('INVALID_SID')


def valid_channel(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        return 'channel' in request_data and 'type' in request_data['channel']

    else:
        return send_json('INVALID_PARAMETER')


def valid_game(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        return 'game' in request_data

    else:
        return send_json('INVALID_PARAMETER')


def valid_currency(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        return 'currency' in request_data
    else:
        return send_json('INVALID_PARAMETER')


def valid_transaction(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        return 'transaction' in request_data

    else:
        return send_json('INVALID_PARAMETER')


def valid_amount(valid=True):
    if valid:
        request_data = request.get_json(force=True)

        return 'amount' in request_data['transaction']

    else:
        return send_json('INVALID_PARAMETER')