import json

from flask import request
from werkzeug.security import check_password_hash, generate_password_hash

from db_classes import *
from utils import get_timestamp


def db_getuser_email(email):
    query = UserEntry().query.filter_by(email=email).first()
    if query is None:
        return None
    else:
        return query


def db_getuser_username(username):
    query = UserEntry().query.filter_by(username=username).first()
    return query


def db_get_bet(mtcode):
    query = BetEntry().query.filter_by(mtcode=mtcode).first()
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


def db_check_mtcode():
    bet = BetEntry().query.filter_by(mtcode=request.form['mtcode'])
    return bet is not None


def db_refund():
    bet = BetEntry().query.filter_by(mtcode=request.form['mtcode'])
    # settle the bet to balance
    amount = float(bet.amount)
    user = UserEntry().query.filter_by(username=bet.username)
    # settle the bet to balance
    balance = float(user.balance)
    user.balance += amount

    # write to bet db
    refund = RefundEntry(
        bet.username,
        bet.amount,
        get_timestamp(),
        bet.gamecode,
        bet.gamehall,
        bet.mtcode,
        bet.platform,
        bet.roundid,
        bet.session
    )
    db.session.add(refund)
    db.session.commit()

    return float(user.balance)


def db_bet():

    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    balance = float(user.balance)
    bet = float(request.form['amount'])

    new_balance = balance - bet
    if new_balance > 0:
        user.balance = new_balance
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


def db_rollout():

    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    balance = float(user.balance)
    bet = float(request.form['amount'])

    new_balance = balance - bet
    if new_balance > 0:
        user.balance = new_balance
        # write to bet db
        bet = RolloutEntry(
            request.form['account'],
            request.form['amount'],
            request.form['eventTime'],
            request.form['gamecode'],
            request.form['gamehall'],
            request.form['mtcode'],
            request.form['roundid'],
            request.form['session']
        )
        db.session.add(bet)
        db.session.commit()

    return new_balance


def db_endround():
    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    balance = float(user.balance)

    amount = float(json.loads(request.form['data'])[0]['amount'])
    if amount >= 0:
        new_balance = balance + amount
        user.balance = new_balance
        data = json.loads(request.form['data'])
        for result in data:
            # write to EndRound db
            endround = EndroundEntry(
                request.form['account'],
                request.form['createTime'],
                request.form['gamecode'],
                request.form['gamehall'],
                request.form['freegame'],
                request.form['jackpot'],
                request.form['jackpotcontribution'],
                request.form['bonus'],
                request.form['luckydraw'],
                request.form['roundid'],
                request.form['data'],
                request.form['freeticket']
            )
            db.session.add(endround)
        db.session.commit()

    return new_balance


def db_rollin():
    # update the user
    user = UserEntry().query.filter_by(username=request.form['account']).first()

    user.balance += request.form['amount']

    # write to EndRound db
    rollin = RollinEntry(
        request.form['account'],
        request.form['eventTime'],
        request.form['gamehall'],
        request.form['gamecode'],
        request.form['roundid'],
        request.form['validbet'],
        request.form['bet'],
        request.form['win'],
        request.form['roomfee'],
        request.form['amount'],
        request.form['mtcode'],
        request.form['createTime'],
        request.form['rake'],
        request.form['gametype']
    )
    db.session.add(rollin)
    db.session.commit()

    return float(user.balance)
