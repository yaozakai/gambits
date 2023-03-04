import json

from flask import request
from werkzeug.security import check_password_hash, generate_password_hash

from db_classes import *


def db_getuser_email(email):
    query = UserEntry().query.filter_by(email=email).first()
    if query is None:
        return None
    else:
        return query


def db_getuser_username(username):
    query = UserEntry().query.filter_by(username=username).first()
    if query is None:
        return None
    else:
        return query


def db_user_verification(email, password):
    dataclass = UserEntry('', email)
    user = dataclass.query.filter_by(email=email).first()
    # testPass = generate_password_hash(password, method='sha256')
    # tes = check_password_hash(user.password[1:-1], password)
    if user and check_password_hash(user.password, password):
        return user
    else:
        return None


def db_new_user(register_form):
    # create a session id
    raw_str = str(UserEntry().query.count() + 1).zfill(8)
    user_id = '-'.join([raw_str[:4], raw_str[4:]])
    dataclass_user = UserEntry(user_id,
                               register_form.data['email'],
                               register_form.data['username'],
                               generate_password_hash(register_form.data['password'], method='sha256'),
                               register_form.data['referral'])
    db.session.add(dataclass_user)
    db.session.commit()
    return True


def db_get_user(user_id):
    dataclass_login = UserEntry()
    user = dataclass_login.query.filter_by(user_id=user_id).first()
    return user


def db_new_login(login_form):
    # dataclass_sid = SidEntry()
    # dataclass_login = LoginEntry()
    dataclass_user = UserEntry().query.filter_by(email=login_form.email.data).first()
    dataclass_user.logged_in = True
    # dataclass_login = LoginEntry('{' + str(sid) + '}') # , '{' + dataclass_login + '}', '{' + NFT_ID + '}')
    dataclass_login = LoginEntry('', login_form.email.data)
    db.session.add(dataclass_login)
    db.session.commit()

    return dataclass_login


def db_search_userid(userid):
    dataclass = UserEntry()
    return dataclass.query.filter_by(user_id=userid).all()


def db_bet():
    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    balance = float(user.balance)
    bet = float(request.form['amount'])

    new_balance = balance - bet
    if new_balance > 0:
        user.balance = new_balance

        error_code = '0'
        # write to bet db
        bet = BetEntry(
            request.form['account'],
            request.form['amount'],
            request.form['eventTime'],
            request.form['gamecode'],
            request.form['gamehall'],
            request.form['mtcode'],
            request.form['platform'],
            request.form['roundid'],
            request.form['session']
        )
        db.session.add(bet)
        db.session.commit()

    return new_balance


def db_update_balance():
    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    balance = float(user.balance)

    amount = float(json.loads(request.form['data'])[0]['amount'])
    if amount >= 0:
        new_balance = balance + amount
        user.balance = new_balance
        db.session.commit()

    return new_balance
