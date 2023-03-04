from datetime import datetime

import pytz
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy
from config import app

with app.app_context():
    db = SQLAlchemy(app)
    db.create_all()
    db.session.commit()


# def db_get_balance(userid):
#     dataclass = UserEntry()
#     if dataclass.query.filter_by(user_id=userid).all():
#         return dataclass.query.filter_by(user_id=userid).all()[0].balance


# incoming bet request handler CQ9


##################################################################################################################

class TransEntry(db.Model):
    __tablename__ = 'transactions'
    time = db.Column(db.DateTime, nullable=False)
    account = db.Column(db.String(36), nullable=False)
    game_hall = db.Column(db.String(36), nullable=False)
    game_code = db.Column(db.String(36), nullable=False)
    round_id = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    mtcode = db.Column(db.String(70), nullable=False, primary_key=True)

    def __init__(self, account='', mtcode='', amount=0, round_id='', game_code='', game_hall='', time=''):
        self.time = time
        self.account = account
        self.mtcode = mtcode
        self.amount = amount
        self.round_id = round_id
        self.game_code = game_code
        self.game_hall = game_hall


class SidEntry(db.Model):
    __tablename__ = 'sessions'
    sid = db.Column(db.Integer, nullable=False, primary_key=True)
    uuid = db.Column(db.String(50), nullable=False)
    userID = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, userID='', sid=0, uuid=''):
        self.sid = sid
        self.uuid = uuid
        self.userID = userID


class LoginEntry(db.Model):
    __tablename__ = 'login'
    created = db.Column(db.DateTime, default=datetime.now(tz=pytz.timezone('Asia/Shanghai')))
    sid = db.Column(db.String(100), nullable=False, primary_key=True)
    email = db.Column(db.String(100), primary_key=True)

    def __init__(self, sid='', email=''):
        if len(sid) == 0:
            # session id format ####-####
            sid = str(self.query.count() + 1).zfill(8)
            self.sid = '-'.join([sid[:4], sid[4:]])
        else:
            self.sid = sid
        self.email = email


class UserEntry(UserMixin, db.Model):
    __tablename__ = 'users'
    # sid = db_sid.Column(db_sid.String(50), nullable=False, primary_key=True, unique=True)
    # id = db.Column(db.String(50), primary_key=True)
    # uuid = the_db.Column(the_db.String(50))
    user_id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(50), primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now(tz=pytz.timezone('Asia/Shanghai')))
    password = db.Column(db.String(255))
    balance = db.Column(db.String(50), default='0')
    referral = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=False)
    logged_in = db.Column(db.Boolean, default=False)
    is_anonymous = False
    currency = db.Column(db.String(10), default='USD')
    # page = ''

    def __init__(self, user_id='', email='', username='', password='', referral=''):
        self.email = email
        self.user_id = user_id
        if len(user_id) == 0:
            self.user_id = self.get_id()
        self.password = password
        self.referral = referral
        self.username = username

    def is_active(self):
        if self.query.filter_by(email=self.email).first_or_404().active:
            return True
        else:
            return False

    def get_id(self):
        if self.user_id is None:
            self.user_id = self.query.filter_by(email=self.email).first_or_404().user_id
        return self.user_id

    def is_authenticated(self):
        # check user exists
        query = self.query.filter_by(email=self.email).first_or_404()
        if query is not None:
            # return logged_in state
            return query.logged_in
        else:
            return False

    def serialize(self):
        return {"user_id": self.get_id(),
                "email": self.email,
                "username": self.username,
                "created": self.created,
                "password": self.password,
                "referral": self.referral,
                "active": self.active,
                "is_anonymous": self.is_anonymous,
                "logged_in": self.logged_in}


class WalletEntry(db.Model):
    __tablename__ = 'wallets'
    # login_time = db.Column(db.DateTime, default=datetime.now(tz=pytz.utc))
    wallet_ID = db.Column(db.String(50), nullable=False, primary_key=True)
    NFT_ID = db.Column(db.String(50), nullable=False)
    solana = db.Column(db.Integer, nullable=False)
    ethereum = db.Column(db.Integer, nullable=False)
    cardano = db.Column(db.Integer, nullable=False)
    bitcoin = db.Column(db.Integer, nullable=False)
    tether = db.Column(db.Integer, nullable=False)

    def __init__(self, sid='', wallet_ID='', NFT_ID='', solana=0, ethereum=0, cardano=0, bitcoin=0, tether=0):
        self.sid = sid
        self.NFT_ID = NFT_ID
        self.wallet_ID = wallet_ID
        self.solana = solana
        self.ethereum = ethereum
        self.cardano = cardano
        self.bitcoin = bitcoin
        self.tether = tether


class HistoryEntry(db.Model):
    __tablename__ = 'history'
    round = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.String(20))
    win = db.Column(db.String(20))
    bet = db.Column(db.String(20))
    bettime = db.Column(db.String(20))


class BetEntry(db.Model):
    __tablename__ = 'bets'
    username = db.Column(db.String(50), primary_key=True)
    amount = db.Column(db.String(20))
    time = db.Column(db.DateTime)
    game_code = db.Column(db.String(20))
    game_hall = db.Column(db.String(20))
    mtcode = db.Column(db.String(60))
    platform = db.Column(db.String(20))
    round_id = db.Column(db.String(60))
    session = db.Column(db.String(60))

    def __init__(self, username='', amount='', time='', game_code='', game_hall='', mtcode='', platform='', round_id='', session='', ):
        self.username = username
        self.amount = amount
        self.time = time
        self.game_code = game_code
        self.game_hall = game_hall
        self.mtcode = mtcode
        self.platform = platform
        self.round_id = round_id
        self.session = session
