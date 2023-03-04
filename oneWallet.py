from flask import request
from db_classes import db_trans_db_exist, db_trans_settled_by_cancel, db_trans_settled, db_trans_exist, db_new_trans_dbcr, \
    db_new_user_dbcr
from utils import send_json


def valid_cancel(userid='', uuid=''):
    request_data = request.get_json(force=True)
    # check if bet exists (match id and if settled = false)
    if not db_trans_exist('Debit', request_data['transaction']['id']):
        return send_json('BET_DOES_NOT_EXIST')
    # check if the debit has been settled
    if db_trans_settled_by_cancel(request_data['transaction']['id']):
        return send_json('BET_ALREADY_SETTLED')
    else:
        # write to user db
        balance = db_new_user_dbcr(True, userid, request_data)
        # write to transaction db
        db_new_trans_dbcr('Cancel', userid, request_data, uuid)
        return send_json("OK", False, uuid, '{:.2f}'.format(balance))


def valid_credit(userid='', uuid=''):
    request_data = request.get_json(force=True)
    # check if the debit has been settled
    if db_trans_settled('Debit', request_data['transaction']['refId']):
        return send_json('BET_ALREADY_SETTLED')
    else:
        # write to user db
        balance = db_new_user_dbcr(True, userid, request_data)
        # write to transaction db
        db_new_trans_dbcr('Credit', userid, request_data, uuid)
        return send_json("OK", False, uuid, '{:.2f}'.format(balance))


def valid_debit(userid='', uuid=''):
    request_data = request.get_json(force=True)
    # check if a debit already exists
    if db_trans_db_exist(request_data['transaction']):
        return send_json('BET_ALREADY_EXIST')
    else:
        # db cr from user db and check for insufficient funds
        balance = db_new_user_dbcr(False, userid, request_data)
        if balance >= 0:
            # write to transaction db
            db_new_trans_dbcr('Debit', userid, request_data, uuid)
            return send_json("OK", False, uuid, '{:.2f}'.format(balance))
        else:
            return send_json('INSUFFICIENT_FUNDS')