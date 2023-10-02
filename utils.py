import asyncio
import base64
import csv
import json
import re
import datetime
import socket
import time
import urllib

import flask

import requests
from os import listdir
from os.path import isfile, join
from flask import jsonify, request, session

import chinese_converter

from urllib.parse import urlparse, urljoin

from config import CQ9_AGENT_KEY
from constants import CQ9_KEY, CQ9_AGENT_KEY_LOCAL
from db_classes import UserEntry, db
from email_confirmation import confirm_token

icon_placement = []
game_titles = []
translations = {}

url = 'https://api.cqgame.games/'
root_path = 'static'
robotext = ''


def debug_out(output):
    if socket.gethostname() == 'The-Only-Real-MacBook-Pro.local':
        print(time.strftime("%H:%M:%S", time.localtime()) + ':' + output)


def check_token():
    return request.headers.get('Wtoken') == CQ9_AGENT_KEY


def get_timezone():
    timezone_object = datetime.timezone(datetime.timedelta(hours=-4), name="UTC-4")
    return timezone_object


def get_timestamp(short=True, isoformat=True):
    # sgtTimeDelta = datetime.timedelta(hours=-4)
    timezone_object = datetime.timezone(datetime.timedelta(hours=-4), name="UTC-4")
    # Specifying a datetime along with Singapore
    # timezone object
    datetime_object = datetime.datetime.now(timezone_object)

    if isoformat:
        if short:
            # return datetime_object.strftime("%Y-%m-%dT%H:%M:%S-04:00")
            return datetime_object.isoformat(timespec='seconds')
        else:
            # this will return microseconds
            return datetime_object.isoformat()
    else:
        return datetime_object


def get_eod_timestamp():
    timezone_object = datetime.timezone(datetime.timedelta(hours=-4), name="UTC-4")
    datetime_object = datetime.datetime.now(timezone_object)
    return datetime_object.isoformat(timespec='seconds')


def get_bod_timestamp():
    timezone_object = datetime.timezone(datetime.timedelta(hours=-4), name="UTC-4")
    datetime_object = datetime.datetime.now(timezone_object).replace(hour=0, minute=0)
    return datetime_object.isoformat(timespec='seconds')


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


def validate_password(password, lang):
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
        errors.append(translations['password must be 8 chars'][lang])

    # searching for digits
    digit_error = re.search(r"\d", password) is None
    if digit_error:
        if len(errors):
            errors.append("<br>" + translations['password missing number'][lang])
        else:
            errors.append(translations['password missing number'][lang])

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None
    if uppercase_error:
        if len(errors):
            errors.append("<br>" + translations['password missing uppercase digit'][lang])
        else:
            errors.append(translations['password missing uppercase digit'][lang])

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None
    if lowercase_error:
        if len(errors):
            errors.append("<br>" + translations['password missing lowercase'][lang])
        else:
            errors.append(translations['password missing lowercase'][lang])

    # searching for symbols
    # symbol_error = re.search_user_page(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    # password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error)

    return errors


def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')


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


def reload_translations():
    debug_out('reload_translations')
    reader = csv.DictReader(open('static/csv/translations.csv', mode='r', encoding='utf-8-sig'))
    global translations
    for row in reader:
        if row['name'].split(':')[0] == 'urlencode':
            for lang in row:
                if lang != 'name':
                    row[lang] = urllib.parse.quote(row[lang], safe='')
        # trad = {'name': chinese_converter.to_traditional(row['zh-cn']), 'lang': 'zh-tw'}
        # row['zh-tw'] = chinese_converter.to_traditional(row['zh-cn'])
        translations[row['name']] = row


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


def activate_account(token, lang):
    notification_json = {
        "notification_title": translations['account verification'][lang],
        "notification": ''
    }
    email = confirm_token(token)
    # email = 'walt.yaoza@gmail.com'
    if email:
        user = UserEntry().query.filter_by(email=email).first_or_404()
        notification_json['notification'] = translations['account already verified'][lang]
        if not user.is_active():
            user.active = True
            db.session.commit()
    else:
        notification_json['notification'] = translations['confirmation link'][lang]

    return notification_json


# def refresh_page(notification_title, notification, reset_pass_popup):
#     login_form = {}
#     register_form = {}
#     if 'logged_in' not in session:
#         csrf_token = csrf.generate_csrf()
#         session['csrf'] = csrf_token
#         login_form = LoginForm()
#         login_form.csrf_token.data = csrf_token
#         register_form = RegisterForm()
#         register_form.csrf_token.data = csrf_token
#         if 'lang' or 'country' not in session:
#             # find user's location, defaults to English
#             set_session_geo_lang()
#         set_flag_from_lang()
#
#         # set stage in jinja
#         session['env'] = environ['env']
#
#         if 'ref' in request.args:
#             session['ref'] = request.args['ref']
#
#         if 'page' in session:
#             if session['page'] == 'gallery':
#                 return render_template('page-gallery-wrap.html', icon_placement=icon_placement,
#                                        game_titles=game_titles,
#                                        root_path='', login_form=login_form, register_form=register_form,
#                                        RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=False,
#                                        notification='', notification_title='', reset_pass=False,
#                                        lang=session['lang'], translations=translations)
#             else:
#                 if len(request.data) > 0:
#                     report_date = json.loads(request.data)['reportDate']
#
#                 else:
#                     report_date = str(datetime.datetime.now()).split(' ')[0]
#
#                 if session['page'] == 'txnHistory':
#                     queries = TxnEntry().query.filter_by(user_id=session['_user_id'])
#                     rec = []
#                     for query in queries:
#                         if pytz.UTC.localize(query.created) < pytz.UTC.localize(datetime.datetime.now()):
#                             rec.insert(0, query.serialize())
#                     rec.sort(key=itemgetter('created'), reverse=True)
#                     return render_template('page-txnHistory-wrap.html', rec=rec, report_date=report_date,
#                                            translations=translations)
#                 elif session['page'] == 'gameHistory':
#                     rec = player_report_today(db_get_user().username, report_date)
#                     # report_date = report_date.strftime('%Y-%m-%d')
#                     if rec is None:
#                         return render_template('page-gamehistory-wrap.html', rec=[], translations=translations,
#                                                report_date=report_date, lang=session['lang'])
#                     else:
#                         return render_template('page-gamehistory-wrap.html', rec=rec['Data'],
#                                                translations=translations,
#                                                report_date=report_date, lang=session['lang'])
#                 elif session['page'] == 'pendingWithdraw':
#                     return setup_pendingWithdraw_template(True)
#                 elif session['page'] == 'search_user_page':
#                     return setup_search_template()
#
#     session['page'] = 'gallery'
#     return render_template('page-gallery-wrap.html', icon_placement=icon_placement,
#                            game_titles=game_titles,
#                            root_path='', login_form=login_form, register_form=register_form,
#                            RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=False,
#                            notification='', notification_title='', reset_pass=False,
#                            lang=session['lang'], translations=translations)

# def set_session_geo_lang(ip_address):
#     # if socket.gethostname() == 'srv.gambits.vip':
#     #     address = ip_address
#     # else:
#     #     address = ip_address
#         # address = input('Enter the IP:')
#     request_url = 'https://geolocation-db.com/jsonp/' + ip_address
#     response = requests.get(request_url)
#     result = response.content.decode()
#     result = result.split("(")[1].strip(")")
#     result = json.loads(result)
#
#     if 'country_code' in result:
#         session['country'] = result['country_code']
#     else:
#         session['country'] = 'GB'
#
#     debug_out('geolocation:' + result['country_code'])
#
#     if result['country_code'] == 'TW':
#         session['lang'] = 'zh-tw'
#         # session['flag'] = result['country_code'].lower()
#     elif result['country_code'] == 'CN':
#         # session['flag'] = result['country_code'].lower()
#         session['lang'] = 'zh-cn'
#     elif result['country_code'] == 'JP':
#         # session['flag'] = result['country_code'].lower()
#         session['lang'] = 'ja'
#     elif result['country_code'] == 'ID':
#         # session['flag'] = result['country_code'].lower()
#         session['lang'] = 'id'
#     elif result['country_code'] == 'KO':
#         # session['flag'] = result['country_code'].lower()
#         session['lang'] = 'ko'
#     elif result['country_code'] == 'VN':
#         # session['flag'] = result['country_code'].lower()
#         session['lang'] = 'vn'
#     elif result['country_code'] == 'BR' or result['country_code'] == 'PT' or result['country_code'] == 'CV' or \
#             result['country_code'] == 'AO' or result['country_code'] == 'MZ' or result['country_code'] == 'GW' or \
#             result['country_code'] == 'TP':
#         session['lang'] = 'br'
#         # session['flag'] = 'br'
#     elif result['country_code'] == 'ES' or result['country_code'] == 'AR' or result['country_code'] == 'MX' or \
#             result['country_code'] == 'CO' or result['country_code'] == 'PE' or result['country_code'] == 'CL' or \
#             result['country_code'] == 'VE' or result['country_code'] == 'GT' or result['country_code'] == 'EC' or \
#             result['country_code'] == 'BO' or result['country_code'] == 'CU' or result['country_code'] == 'DM' or \
#             result['country_code'] == 'DO' or result['country_code'] == 'PY' or result['country_code'] == 'SV' or \
#             result['country_code'] == 'NI' or result['country_code'] == 'CR' or result['country_code'] == 'PA' or \
#             result['country_code'] == 'UY' or result['country_code'] == 'PR':
#         session['lang'] = 'es'
#         # session['flag'] = 'es'
#     else:
#         session['lang'] = 'en'
#         if result['country_code'] == 'Not found':
#             session['country'] = 'GB'
def save_game_list(game_title_list):

    file = open('static/csv/game_list.csv', 'w', encoding='utf-8-sig')
    game_list = csv.writer(file)

    # header
    row = []
    lang_header = ['en', 'zh-tw', 'zh-cn', 'ko', 'ja', 'th', 'vn', 'id', 'pt-br', 'es']
    for header_name in game_title_list[0]:
        if header_name != 'nameset':
            row.append(header_name)
    # for lang in lang_header:
    #     row.append(lang)

    row.extend(lang_header)
    game_list.writerow(row)

    for game_title in game_title_list:
        # translate simplified to traditional chinese
        for title in game_title['nameset']:
            if title['lang'] == 'zh-cn':
                trad = {'name': chinese_converter.to_traditional(title['name']), 'lang': 'zh-tw'}
                game_title['nameset'].append(trad)
                break

        # write to csv
        row = []
        for field in game_title:
            if field == 'nameset':
                # search_user_page and iterate through supported languages for matches
                for lang in lang_header:
                    for lang_entry in game_title[field]:
                        if lang_entry['lang'] == lang:
                            row.append(lang_entry['name'])
                            lang_found = True
                    if not lang_found:
                        row.append('')

            else:
                row.append(game_title[field])

        game_list.writerow(row)
    file.close()


def get_game_list(online=True):

    if online:
        print('reload_game_titles: ONLINE')

        myobj = {'Authorization': CQ9_KEY, 'Content-Type': 'application/json; charset=UTF-8'}
        x = requests.get(url + 'gameboy/game/list/cq9', headers=myobj)
        # global game_titles
        print('CQ9 return:' + str(x.status_code))

        if x.status_code == 200:
            game_title_list = x.json()['data']
            return game_title_list
        else:
            flask.abort(69)
    # else:
    #     print('reload_game_titles: LOCAL')


def reload_game_titles():
    global game_titles
    # game_titles = await get_game_list()
    game_titles = get_game_list()

    save_game_list(game_titles)

    # return game_titles


def reload_icon_placement():
    icon_path_local = root_path + '/icons/cq9'
    print('Loading files from:' + icon_path_local)
    icon_files = [f for f in listdir(icon_path_local) if
                  isfile(join(icon_path_local, f)) and not f.endswith('.DS_Store')]
    print('Loading icon_placement.csv')
    reader = csv.DictReader(open('static/csv/icon_placement.csv', mode='r', encoding='utf-8-sig'))
    placement = {name: [] for name in reader.fieldnames}
    for row in reader:
        for header_name in reader.fieldnames:
            if len(row[header_name]) > 0:
                placement_name = row[header_name]
                icon_found = False
                for icon in icon_files:
                    if icon.split('_')[0] == placement_name:
                        icon_found = True
                        placement[header_name].append(icon)
                        break
                if not icon_found:
                    print('   icon_placement.csv: gamecode -' + placement_name + '- not found')

                    # [string for string in icon_files if row[header_name] in string]
                # if len(icon_filename) > 0:
                #     placement[header_name].append(icon_filename[0])
    global icon_placement

    icon_placement = placement
    session['icon_placement'] = icon_placement
    return icon_placement


def load_robots_txt():
    file = open('static/robots/robots.txt', 'r')
    global robotext
    robotext = file.read()
