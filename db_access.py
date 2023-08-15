import json

from flask import request
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

# from constants import TWO_DIGIT_CURRENCIES
from db_classes import *
from utils import get_timestamp


# def db_set_deposit_status_complete(deposit_data):
#     query = DepositEntry().query.filter_by(txHash=deposit_data['txHash']).first()
#     query.status = 'complete'
#     db.session.add(query)
#     db.session.commit()
#
#
# def db_create_deposit(email, details):
#     entry = DepositEntry(email, details['amount'], details['currency'], details['chain'],
#                          translations['txn:pending'][session['lang']], details['fromAddress'],
#                          details['txHash'])
#     entry.count = str(int(DepositEntry().query.order_by(desc('count')).first().count) + 1).zfill(8)
#     db.session.add(entry)
#     db.session.commit()


def db_search_user(search_term):
    email_query = UserEntry().query.from_statement(
        text("SELECT * FROM users WHERE email LIKE '%' || LOWER('" + search_term + "') || '%' "))
    username_query = UserEntry().query.from_statement(
        text("SELECT * FROM users WHERE username LIKE '%' || LOWER('" + search_term + "') || '%' "))
    # output = []
    resulting_list = list(email_query)
    resulting_list.extend(x for x in username_query if x not in resulting_list)

    return resulting_list


def db_getuser_email(email):
    query = UserEntry().query.filter_by(email=email).first()
    return query


def db_getuser_username(username):
    query = UserEntry().query.filter_by(username=username).first()
    return query


def db_add_balance(email, amount, currency):
    query = UserEntry().query.filter_by(email=email).first()
    if currency == 'eth':
        query.balance_eth += amount
    elif currency == 'usdt':
        query.balance_usdt += amount

    db.session.add(query)
    db.session.commit()


# def db_get_bet(mtcode):
#     query = BetEntry().query.filter_by(mtcode=mtcode).first()
#     return query


def db_refund_exists():
    query = RefundEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # true if exists
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
    if UserEntry().query.count():
        user_id = str(int(UserEntry().query.order_by(desc('user_id')).first().user_id) + 1).zfill(8)
    else:
        user_id = '00000001'

    # user_id = '-'.join([raw_str[:4], raw_str[4:]])
    dataclass_user = UserEntry(user_id,
                               register_form.data['email'],
                               register_form.data['username'],
                               generate_password_hash(register_form.data['password'], method='sha256'),
                               register_form.data['referral'])
    dataclass_user.lang = session['lang']
    db.session.add(dataclass_user)
    db.session.commit()
    return True


def db_set_password(email, password):
    dataclass_login = UserEntry()

    user = dataclass_login.query.filter_by(email=email).first()
    if user is None:
        return False
    else:
        user.password = generate_password_hash(password, method='sha256')
        db.session.commit()
        return user


def db_set_language():
    dataclass_login = UserEntry()
    if '_user_id' in session:
        user = dataclass_login.query.filter_by(user_id=session['_user_id']).first()
        if user is not None:
            user.lang = session['lang']
            db.session.commit()
            return


def db_get_user():
    return UserEntry().query.filter_by(user_id=session['_user_id']).first()


def db_get_balance():
    return UserEntry().query.filter_by(user_id=session['_user_id']).first().balance_usdt


def db_get_deposit(txHash):
    return TxnEntry().query.filter_by(txHash=txHash).first()


def db_get_user_from_id(user_id):
    return UserEntry().query.filter_by(user_id=user_id).first()


# def db_set_public_address(public_address):
#     user = UserEntry().query.filter_by(user_id=session['_user_id']).first()
#     if user is None:
#         return False
#     else:
#         user.publicAddress = public_address
#         db.session.commit()
#         return user


def db_new_login(login_form):
    dataclass_user = UserEntry().query.filter_by(email=login_form.email.data).first()
    dataclass_user.logged_in = True
    dataclass_login = LoginEntry(login_form.email.data)

    if LoginEntry().query.count():
        dataclass_login.count = str(int(LoginEntry().query.order_by(desc('count')).first().count) + 1).zfill(8)
    else:
        dataclass_login.count = '00000001'

    db.session.add(dataclass_login)
    db.session.commit()

    return dataclass_login


def db_search_userid(userid):
    dataclass = UserEntry()
    return dataclass.query.filter_by(user_id=userid).first()


def db_refund_find_txn():
    trans_type = request.form['mtcode'].split('-')[1]
    if trans_type == 'bet':
        entry = BetEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    elif trans_type == 'rollout':
        entry = RolloutEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # true if exists
    return entry


def db_check_mtcode_bet():
    bet = BetEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # true if exists
    return bet is not None


def db_check_mtcode_rollin():
    rollin = RollinEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # true if exists
    return rollin is not None


def db_check_roundid():
    bets = BetEntry().query.filter_by(roundid=request.form['roundid'])
    bets_settle = json.loads(request.form['data'])
    for bet in bets:
        pass
    # true if exists
    return bet is not None


def db_refund(entry):
    # trans_type = request.form['mtcode'].split('-')[1]
    # if trans_type == 'bet':
    #     entry = BetEntry().query.filter_by(mtcode=request.form['mtcode']).first()
    # elif trans_type == 'rollout':
    #     entry = RolloutEntry().query.filter_by(mtcode=request.form['mtcode']).first()

    # settle the bet to balance
    user = UserEntry().query.filter_by(username=entry.username).first()

    # settle the bet to balance
    user.balance_usdt += round(float(entry.amount), 2)

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

    # bet_return = {'balance': balance, 'valid': bet < balance}

    return user.balance_usdt


def db_bet():
    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    # balance = user.balance_usdt
    # bet = float(request.form['amount'])
    bet = float(request.form['amount'])
    valid = False

    if bet < user.balance_usdt:
        valid = True
        user.balance_usdt -= bet

        if 'platform' in request.form:
            platform = request.form['platform']
        else:
            platform = ''
        # if 'session' in request.form:
        #     session = request.form['session']
        # else:
        #     session = ''

        # if user.currency in TWO_DIGIT_CURRENCIES:
        #     user.balance_usdt = format(balance, '.2f')
        # else:
        #     user.balance_usdt = format(balance, '.0Df')

        # write to bet db
        entry = BetEntry(
            request.form['account'],
            request.form['amount'],
            request.form['eventTime'],
            request.form['gamecode'],
            request.form['gamehall'],
            request.form['mtcode'],
            platform,
            request.form['roundid'],
            # session
        )
        db.session.add(entry)
        db.session.commit()

    bet_return = {'balance': user.balance_usdt, 'valid': valid}

    return bet_return


def db_takeall():
    user = UserEntry().query.filter_by(username=request.form['account']).first()
    # settle the bet to balance
    balance = user.balance_usdt
    user.balance_usdt = 0

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
        # bet = Number.parseFloat(request.form['amount'])
        # new_balance = Number.parseFloat((balance - bet).toFixed(10))
        # user.balance = Number.parseFloat((user.balance + result['amount']).toFixed(10))
        bet = BetEntry().query.filter_by(mtcode=result['mtcode']).first()
        bet.settled = True

        user.balance_usdt += round(float(result['amount']), 2)

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
        jackpotcontribution = ''

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

    return user.balance_usdt


# db to cq9
def db_rollout():
    user = UserEntry().query.filter_by(username=request.form['account']).first()

    # new_balance = Number.parseFloat(user.balance - float(request.form['amount']).toFixed(10))
    new_balance = user.balance_usdt - round(float(request.form['amount']), 2)
    valid = False

    if new_balance >= 0:
        valid = True
        user.balance_usdt = new_balance
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

    bet_return = {'balance': user.balance_usdt, 'valid': valid}

    return bet_return


# cq9 to db
def db_rollin():
    # update the user
    user = UserEntry().query.filter_by(username=request.form['account']).first()

    # user.balance = Number.parseFloat(user.balance + float(request.form['amount']).toFixed(10))
    user.balance_usdt += float(request.form['amount'])
    # if user.currency in TWO_DIGIT_CURRENCIES:
        # user.balance = format(user.balance, '.2f')

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

    return user.balance_usdt
