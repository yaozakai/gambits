import json

from flask import request
from sqlalchemy import desc, literal, column, text
from werkzeug.security import check_password_hash, generate_password_hash

from db_classes import *
from utils import get_timestamp


def db_search_user(search_term):
    # search_term = "%{}%".format(search_term)
    # quak = UserEntry()
    query = UserEntry().query.from_statement(text("SELECT * FROM users WHERE email LIKE '%' || LOWER('za') || '%' ")).all()
    # query = UserEntry().query.filter_by(email=search_term)

    return query


def db_getuser_email(email):
    query = UserEntry().query.filter_by(email=email).first()
    return query


def db_getuser_username(username):
    query = UserEntry().query.filter_by(username=username).first()
    return query


def db_get_bet(mtcode):
    query = BetEntry().query.filter_by(mtcode=mtcode).first()
    return query


def db_refund_exists():
    query = RefundEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    return query is not None


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
    # user_id = str(UserEntry().query.count() + 1).zfill(8)
    user_id = str(int(UserEntry().query.order_by(desc('user_id')).first().user_id) + 1).zfill(8)

    # user_id = '-'.join([raw_str[:4], raw_str[4:]])
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


def db_set_password(email, password):
    dataclass_login = UserEntry()
    user = dataclass_login.query.filter_by(email=email).first()
    user.password = generate_password_hash(password, method='sha256')
    db.session.commit()
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
    return dataclass.query.filter_by(user_id=userid).first()


def db_check_mtcode():
    trans_type = request.form['mtcode'].split('-')[1]
    if trans_type == 'bet':
        entry = BetEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    elif trans_type == 'rollout':
        entry = RolloutEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # true if exists
    return entry is not None


def db_check_mtcode_bet():
    bet = BetEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # true if exists
    return bet is not None


def db_check_mtcode_rollin():
    rollin = RollinEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # true if exists
    return rollin is not None


def db_check_roundid():
    bet = BetEntry().query.filter_by(roundid=request.form['roundid']).first()
    # true if exists
    return bet is not None


def db_refund():
    trans_type = request.form['mtcode'].split('-')[1]
    if trans_type == 'bet':
        entry = BetEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    elif trans_type == 'rollout':
        entry = RolloutEntry().query.filter_by(mtcode=request.form['mtcode']).first()

    # settle the bet to balance
    user = UserEntry().query.filter_by(username=entry.username).first()
    # settle the bet to balance
    user.balance = float(user.balance) + float(entry.amount)

    # write to bet db
    refund = RefundEntry(
        entry.username,
        entry.amount,
        get_timestamp(),
        entry.gamecode,
        entry.gamehall,
        entry.mtcode,
        entry.roundid,
        entry.session
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
        if 'platform' in request.form:
            platform = request.form['platform']
        else:
            platform = ''
        if 'session' in request.form:
            session = request.form['session']
        else:
            session = ''

        user.balance = new_balance
        # write to bet db
        bet = BetEntry(
            request.form['account'],
            request.form['amount'],
            request.form['eventTime'],
            request.form['gamecode'],
            request.form['gamehall'],
            request.form['mtcode'],
            platform,
            request.form['roundid'],
            session
        )
        db.session.add(bet)
        db.session.commit()

    return new_balance


def db_takeall():

    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    balance = user.balance
    user.balance = 0

    # write to bet db
    takeAll = TakeallEntry(
        request.form['account'],
        request.form['eventTime'],
        request.form['gamecode'],
        request.form['gamehall'],
        request.form['mtcode'],
        request.form['roundid'],
        request.form['session']
    )
    db.session.add(takeAll)
    db.session.commit()

    return balance


def db_endround():
    user = UserEntry().query.filter_by(username=request.form['account']).first()

    data = json.loads(request.form['data'])
    for result in data:
        user.balance = float(user.balance) + result['amount']

    # filter out the optional parameters
    if 'freegame' in request.form:
        freegame = request.form['freegame']
    else:
        freegame = 0

    if 'jackpot' in request.form:
        jackpot = request.form['jackpot']
    else:
        jackpot = 0

    if 'jackpotcontribution' in request.form:
        jackpotcontribution = request.form['jackpotcontribution']
    else:
        jackpotcontribution = []

    if 'bonus' in request.form:
        bonus = request.form['bonus']
    else:
        bonus = 0

    if 'luckydraw' in request.form:
        luckydraw = request.form['luckydraw']
    else:
        luckydraw = 0

    if 'freeticket' in request.form:
        freeticket = request.form['freeticket']
    else:
        freeticket = 0

    # write to EndRound db
    endround = EndroundEntry(
        request.form['account'],
        request.form['createTime'],
        request.form['gamecode'],
        request.form['gamehall'],
        freegame,
        jackpot,
        jackpotcontribution,
        bonus,
        luckydraw,
        request.form['roundid'],
        request.form['data'],
        freeticket
    )
    db.session.add(endround)
    db.session.commit()

    return float(user.balance)


# db to cq9
def db_rollout():

    user = UserEntry().query.filter_by(username=request.form['account']).first()

    new_balance = float(user.balance) - float(request.form['amount'])
    if new_balance >= 0:
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


# cq9 to db
def db_rollin():
    # update the user
    user = UserEntry().query.filter_by(username=request.form['account']).first()

    user.balance = float(user.balance) + float(request.form['amount'])

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
