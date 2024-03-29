from datetime import datetime

import flask
import pytz
from dataclasses import dataclass
from flask import session
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy
from pytz import unicode
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import ARRAY
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
class OAuthEntry(db.Model):
    __tablename__ = 'oauth'
    user_id = db.Column(db.String(8), primary_key=True)
    oauth_token = db.Column(db.String(55))
    oauth_token_secret = db.Column(db.String(50))

    def __init__(self):
        user_id = session['_user_id']


class LoginEntry(db.Model):
    __tablename__ = 'login'
    log_time = db.Column(db.DateTime, default=datetime.now(tz=pytz.timezone('Asia/Shanghai')))
    # sid = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200))
    # count = db.Column(db.String(10), primary_key=True)
    count = db.Column(db.Numeric(10), primary_key=True)

    def __init__(self, email=''):
        # if len(sid) == 0:
        #     # session id format ####-####
        #     sid = str(self.query.count() + 1).zfill(8)
        #     # self.sid = '-'.join([sid[:4], sid[4:]])
        #     self.sid = sid
        # else:
        #     self.sid = sid
        self.email = email


class UserEntry(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(8), primary_key=True)
    email = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(16), primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now(tz=pytz.timezone('Asia/Shanghai')))
    password = db.Column(db.String(100))
    balance_eth = db.Column(db.Float, default=0)
    balance_usdt = db.Column(db.Float, default=0)
    referral = db.Column(db.String(16))
    active = db.Column(db.Numeric(1), default=0)
    admin = db.Column(db.Numeric(1), default=0)
    logged_in = db.Column(db.Numeric(1), default=0)
    currency = db.Column(db.String(10), default='USDT')
    lang = db.Column(db.String(10), default='en')

    snb_totalbet = db.Column(db.Float, default=0)
    snb_phone = db.Column(db.Numeric(1))
    snb_phone_number = db.Column(db.String(16))
    snb_phone_otp = db.Column(db.String(4))
    snb_phone_time = db.Column(db.DateTime)

    snb_twitter = db.Column(db.Numeric(1))
    snb_twitter_url = db.Column(db.String(255))
    snb_discord = db.Column(db.Numeric(1), default=0)
    snb_easter = db.Column(db.Numeric(1), default=0)

    oauth_token = db.Column(db.String(55))
    oauth_token_secret = db.Column(db.String(50))
    twt_user_id = db.Column(db.String(22))

    def __init__(self, user_id='', email='', username='', password='', referral=''):
        self.email = email
        self.user_id = user_id
        if len(user_id) == 0:
            self.user_id = self.get_id()
        self.password = password
        self.referral = referral
        self.username = username

    def as_dict(self):
        return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}

    def is_active(self):
        if self.query.filter_by(email=self.email).first_or_404().active:
            return True
        else:
            return False
        # return self.active

    def get_lang(self):
        # return self.query.filter_by(email=self.email).first_or_404().lang
        return self.lang

    def is_admin(self):
        if self.query.filter_by(email=self.email).first_or_404().admin:
            return True
        else:
            return False
        # return self.admin

    def get_id(self):
        if self.user_id is None:
            self.user_id = self.query.filter_by(email=self.email).first_or_404().user_id
        return self.user_id

    def is_authenticated(self):
        # check user exists
        # query = self.query.filter_by(email=self.email).first_or_404()
        # if query is not None:
        #     # return logged_in state
        #     return query.logged_in
        # else:
        #     return False
        return self.logged_in

    def serialize(self):
        return {"user_id": self.get_id(),
                "email": self.email,
                "username": self.username,
                "created": self.created,
                "password": self.password,
                "referral": self.referral,
                "active": self.active,
                # "is_anonymous": self.is_anonymous,
                "logged_in": self.logged_in}

    def add_balance(self, amount, currency):
        if currency == 'eth':
            self.balance_eth += round(amount, 2)
        elif currency == 'usdt':
            self.balance_usdt += round(amount, 2)

        db.session.add(self)
        db.session.commit()

    def minus_balance(self, amount, currency):
        if currency == 'eth':
            # if amount > self.balance_eth:
            #     return flask.abort(400)
            self.balance_eth -= round(amount, 2)
        elif currency == 'usdt':
            # if amount > self.balance_usdt:
            #     return flask.abort(400)
            self.balance_usdt -= round(amount, 2)

        db.session.add(self)
        db.session.commit()


class BetEntry(db.Model):
    __tablename__ = 'bets'
    username = db.Column(db.String(16))
    amount = db.Column(db.Numeric(36))
    time = db.Column(db.DateTime)
    gamecode = db.Column(db.String(36))
    gamehall = db.Column(db.String(36))
    mtcode = db.Column(db.String(70), primary_key=True)
    platform = db.Column(db.String(20))
    roundid = db.Column(db.String(60))
    # settled = db.Column(db.Numeric(1), default=0)

    # session = db.Column(db.String(60))

    def __init__(self, username='', amount=0, time='', gamecode='', gamehall='', mtcode='', platform='',
                 roundid='', ):
        self.username = username
        self.amount = amount
        self.time = time
        self.gamecode = gamecode
        self.gamehall = gamehall
        self.mtcode = mtcode
        self.platform = platform
        self.roundid = roundid
        # self.session = session

    # def __init__(self, mtcode=''):
    #     if mtcode:
    #         copy = self.query.filter_by(mtcode=mtcode).first()
    #         self.username = copy.username
    #         self.amount = copy.amount
    #         self.time = copy.time
    #         self.gamecode = copy.gamecode
    #         self.gamehall = copy.gamehall
    #         self.mtcode = copy.mtcode
    #         self.platform = copy.platform
    #         self.roundid = copy.roundid
    #         self.session = copy.session

    def mtcode_exists(self, mtcode):
        self.query.filter_by(mtcode=mtcode).first()


class TakeallEntry(db.Model):
    __tablename__ = 'takealls'
    username = db.Column(db.String(16))
    time = db.Column(db.DateTime)
    gamecode = db.Column(db.String(36))
    gamehall = db.Column(db.String(36))
    mtcode = db.Column(db.String(70), primary_key=True)
    roundid = db.Column(db.String(60))
    session = db.Column(db.String(60))

    def __init__(self, username='', time='', gamecode='', gamehall='', mtcode='',
                 roundid='', session='' ):
        self.username = username
        self.time = time
        self.gamecode = gamecode
        self.gamehall = gamehall
        self.mtcode = mtcode
        self.roundid = roundid
        self.session = session


class EndroundEntry(db.Model):
    __tablename__ = 'endrounds'
    username = db.Column(db.String(16))
    gamehall = db.Column(db.String(36))
    gamecode = db.Column(db.String(36))
    roundid = db.Column(db.String(50), primary_key=True)
    data = db.Column(db.String(158))
    time = db.Column(db.DateTime)
    freegame = db.Column(db.Integer)
    bonus = db.Column(db.Integer)
    luckydraw = db.Column(db.Integer)
    jackpot = db.Column(db.Integer)
    jackpotcontribution = db.Column(db.Integer)
    freeticket = db.Column(db.Boolean, default=False)

    def __init__(self, username='', time='', gamecode='', gamehall='', freegame=0, jackpot=0,
                 jackpotcontribution='', bonus=0, luckydraw=False, roundid='', data='', freeticket=False):
        self.username = username
        self.gamehall = gamehall
        self.gamecode = gamecode
        self.roundid = roundid
        self.data = data
        self.time = time
        self.freegame = freegame
        self.bonus = bonus
        self.luckydraw = luckydraw
        self.jackpot = jackpot
        self.jackpotcontribution = jackpotcontribution
        self.freeticket = freeticket


class RefundEntry(db.Model):
    __tablename__ = 'refunds'
    username = db.Column(db.String(16))
    amount = db.Column(db.Numeric(36))
    time = db.Column(db.DateTime)
    gamecode = db.Column(db.String(36))
    gamehall = db.Column(db.String(36))
    mtcode = db.Column(db.String(70), primary_key=True)
    roundid = db.Column(db.String(60))
    # session = db.Column(db.String(60))

    def __init__(self, username='', amount=0, time='', gamecode='', gamehall='', mtcode='',
                 roundid=''):
        self.username = username
        self.amount = amount
        self.time = time
        self.gamecode = gamecode
        self.gamehall = gamehall
        self.mtcode = mtcode
        self.roundid = roundid
        # self.session = session


class RolloutEntry(db.Model):
    __tablename__ = 'rollouts'
    username = db.Column(db.String(16))
    amount = db.Column(db.Numeric(36))
    time = db.Column(db.DateTime)
    gamecode = db.Column(db.String(36))
    gamehall = db.Column(db.String(36))
    mtcode = db.Column(db.String(70), primary_key=True)
    roundid = db.Column(db.String(60))
    session = db.Column(db.String(60))

    def __init__(self, username='', amount=0, time='', gamecode='', gamehall='', mtcode='',
                 roundid='', session='', ):
        self.username = username
        self.amount = amount
        self.time = time
        self.gamecode = gamecode
        self.gamehall = gamehall
        self.mtcode = mtcode
        self.roundid = roundid
        self.session = session

    def check_mtcode(self, mtcode):
        entry = self.query.filter_by(mtcode=mtcode).first()
        return entry is not None


class RollinEntry(db.Model):
    __tablename__ = 'rollins'
    username = db.Column(db.String(16))
    event_time = db.Column(db.DateTime)
    gamehall = db.Column(db.String(36))
    gamecode = db.Column(db.String(36))
    roundid = db.Column(db.String(50))
    validbet = db.Column(db.String(36))
    bet = db.Column(db.String(36))
    win = db.Column(db.String(36))
    roomfee = db.Column(db.String(36))
    amount = db.Column(db.Numeric(36))
    mtcode = db.Column(db.String(70), primary_key=True)
    create_time = db.Column(db.DateTime)
    rake = db.Column(db.String(36))
    gametype = db.Column(db.String(36))

    def __init__(self, username='', event_time='', gamehall='', gamecode='', roundid='', validbet='',
        bet='', win='', roomfee='', amount=0, mtcode='', create_time='', rake='', gametype=''):
        self.username = username
        self.event_time = event_time
        self.gamehall = gamehall
        self.gamecode = gamecode
        self.roundid = roundid
        self.validbet = validbet
        self.bet = bet
        self.win = win
        self.roomfee = roomfee
        self.amount = amount
        self.mtcode = mtcode
        self.create_time = create_time
        self.rake = rake
        self.gametype = gametype


@dataclass
class TxnEntry(db.Model):
    __tablename__ = 'txns'
    type: str
    email: str
    user_id: str
    created: datetime
    amount: float
    currency: str
    blockchain: str
    status: str
    fromAddress: str
    txHash: str

    type = db.Column(db.String(20))
    email = db.Column(db.String(100))
    user_id = db.Column(db.String(10), primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now(tz=pytz.timezone('Asia/Shanghai')))
    amount = db.Column(db.Numeric(36))
    currency = db.Column(db.String(10))
    blockchain = db.Column(db.String(50))
    status = db.Column(db.String(255))
    fromAddress = db.Column(db.String(100))
    txHash = db.Column(db.String(100), primary_key=True)

    def __init__(self, txn_type='', email='', user_id='', amount='', currency='', blockchain='', status='', fromAddress='', txHash=''):
        self.type = txn_type
        self.email = email
        self.user_id = user_id
        self.amount = amount
        self.currency = currency
        self.blockchain = blockchain
        self.status = status
        self.fromAddress = fromAddress
        self.txHash = txHash
        # self.created = datetime.now(tz=pytz.timezone('Asia/Shanghai'))

    def as_dict(self):
        return {c.name: unicode(getattr(self, c.name)) for c in self.__table__.columns}

    def commit(self):
        db.session.add(self)
        db.session.commit()

    def mark_complete(self, txn_hash=''):
        if len(txn_hash) > 0:
            self.txHash = txn_hash
        self.status = 'Complete'
        db.session.add(self)
        db.session.commit()

    def mark_failed(self):
        self.status = 'Failed'
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {"type": self.type,
                "email": self.email,
                "user_id": self.user_id,
                "created": datetime.strftime(self.created, '%Y-%m-%d %H:%M:%S'),
                "amount": self.amount,
                "currency": self.currency,
                "blockchain": self.blockchain,
                "status": self.status,
                "fromAddress": self.fromAddress,
                "txHash": self.txHash}
