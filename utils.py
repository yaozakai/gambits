import csv
import functools
import json
import re
import datetime
from os import listdir
from os.path import isfile, join

import requests
from flask import jsonify, request, redirect, url_for, session
from urllib.parse import urlparse, urljoin

from db_classes import UserEntry, db
from email_confirmation import confirm_token

url = 'https://api.cqgame.games/'
icon_path = 'static/icons/cq9'
authKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiI2M2VjZTczODM1ZTYyMzhjYzI2MTdlOTEiLCJhY2NvdW50IjoiZ2FtYml0c19zdyIsIm93bmVyIjoiNjNlY2U3MzgzNWU2MjM4Y2MyNjE3ZTkxIiwicGFyZW50Ijoic2VsZiIsImN1cnJlbmN5IjoiVVNEIiwianRpIjoiODIxMTIzMzE5IiwiaWF0IjoxNjc2NDcwMDcyLCJpc3MiOiJDeXByZXNzIiwic3ViIjoiU1NUb2tlbiJ9.mj1H6gOiA402u8DJhC9Go1CdFFSXab3OhDVagqhmWHE'


def check_token():
    return request.headers.get('Wtoken') == authKey


def get_timestamp(short=True):
    # sgtTimeDelta = datetime.timedelta(hours=-4)
    timezone_object = datetime.timezone(datetime.timedelta(hours=-4), name="UTC-4")
    # Specifying a datetime along with Singapore
    # timezone object
    datetime_object = datetime.datetime.now(timezone_object)
    # Calling the astimezone() function over the above
    # specified Singapore timezone
    # time_stamp = datetime_object.astimezone(timezone_object)
    if short:
        # return datetime_object.strftime("%Y-%m-%dT%H:%M:%S-04:00")
        return datetime_object.isoformat(timespec='seconds')
    else:
        return datetime_object.isoformat()


def my_login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)

    return secure_function


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def email_valid(s):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, s):
        return True
    return False


def username_valid(s):
    regex = '^\w+$'
    if re.fullmatch(regex, s):
        return True
    return False


def validate_password(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        # 1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    errors = []
    # calculating the length
    length_error = len(password) < 8
    if length_error:
        errors.append("Password must be 8 characters or more")

    # searching for digits
    digit_error = re.search(r"\d", password) is None
    if digit_error:
        if len(errors):
            errors.append("<br>Password missing numerical digit (0-9)")
        else:
            errors.append("Password missing numerical digit (0-9)")

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None
    if uppercase_error:
        if len(errors):
            errors.append("<br>Password missing uppercase digit (A-Z)")
        else:
            errors.append("Password missing uppercase digit (A-Z)")

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None
    if lowercase_error:
        if len(errors):
            errors.append("<br>Password missing lowercase digit (a-z)")
        else:
            errors.append("Password missing lowercase digit (a-z)")

    # searching for symbols
    # symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error)

    return errors


def send_json(status='', sid='', uuid='', balance=''):
    dump = {}
    if status:
        dump["status"] = status
    if sid:
        dump["sid"] = sid
    if balance:
        dump["balance"] = float(balance)
        dump["bonus"] = 0.0
    if uuid:
        dump["uuid"] = uuid
    return jsonify(dump)


def reload_game_titles():
    titles = {}
    # reader = csv.DictReader(open('static/csv/evo_game_list.csv', mode='r', encoding='utf-8-sig'))
    myobj = {'Authorization': authKey, 'Content-Type': 'application/json; charset=UTF-8'}
    x = requests.get(url + 'gameboy/game/list/cq9', headers=myobj)

    return x.json()['data']


def reload_icon_placement():
    print('reloading csv:' + icon_path)
    icon_files = [f for f in listdir(icon_path) if isfile(join(icon_path, f)) and not f.endswith('.DS_Store')]
    reader = csv.DictReader(open('static/csv/icon_placement.csv', mode='r', encoding='utf-8-sig'))
    placement = {name: [] for name in reader.fieldnames}
    for row in reader:
        for header_name in reader.fieldnames:
            if len(row[header_name]) > 0:
                placement_name = row[header_name]
                for icon in icon_files:
                    if icon.split('_')[0] == placement_name:
                        placement[header_name].append(icon)

                    # [string for string in icon_files if row[header_name] in string]
                # if len(icon_filename) > 0:
                #     placement[header_name].append(icon_filename[0])
    return placement


def load_crypto_prices():
    URL = "https://api.binance.com/api/v3/ticker/price?symbol="
    keys = ['BTCUSDT', 'SOLUSDT', 'ETHUSDT', 'ADAUSDT']

    for key in keys:
        API_URL = URL + key
        # requesting data from url
        data = requests.get(API_URL)
        global price_array
        price_array.append(json.loads(data.text))

    print('done: load_crypto_prices')
    return price_array


def verify_user(token):
    notification_json = {
        "notification_title": 'Account verification',
        "notification": ''
    }
    notification_title = 'Account verification'
    email = confirm_token(token)
    if email:
        user = UserEntry().query.filter_by(email=email).first_or_404()
        if user.is_active():
            notification_json['notification'] = 'Account already verified. Please login'
            notification = 'Account already verified. Please login'
            # return redirect(url_for('home', data=jsonify(notification_json)), code=307)
        else:
            user.active = True
            db.session.commit()
            notification_json['notification'] = 'Account has been verified! Please login'
            notification = 'Account has been verified! Please login'
            # return redirect(url_for('home', data=jsonify(notification_json)), code=307)
    else:
        notification_json['notification'] = 'The confirmation link is invalid or has expired'
        notification = 'The confirmation link is invalid or has expired'
        # return redirect(url_for('home', data=jsonify(notification_json)), code=307)

    return notification_json
