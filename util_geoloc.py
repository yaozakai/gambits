import requests
from flask import session


def get_country_code():
    try:
        # get ip
        response = requests.get('https://api64.ipify.org?format=json', timeout=1).json()
    except requests.exceptions.Timeout:
        # default country
        return 'GB'

    ip_address = response["ip"]

    response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=1).json()
    return response.get("country_code")

    # response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=1).json()
    # return response.get("countryCode")


def set_session_geo_lang():

    session['country'] = get_country_code()

    # debug_out('geolocation:' + session['country'])

    if session['country'] == 'TW':
        session['lang'] = 'zh-tw'
        # session['flag'] = session['country'].lower()
    elif session['country'] == 'CN':
        # session['flag'] = session['country'].lower()
        session['lang'] = 'zh-cn'
    elif session['country'] == 'JP':
        # session['flag'] = session['country'].lower()
        session['lang'] = 'ja'
    elif session['country'] == 'ID':
        # session['flag'] = session['country'].lower()
        session['lang'] = 'id'
    elif session['country'] == 'KO':
        # session['flag'] = session['country'].lower()
        session['lang'] = 'ko'
    elif session['country'] == 'VN':
        # session['flag'] = session['country'].lower()
        session['lang'] = 'vn'
    elif session['country'] == 'BR' or session['country'] == 'PT' or session['country'] == 'CV' or \
            session['country'] == 'AO' or session['country'] == 'MZ' or session['country'] == 'GW' or \
            session['country'] == 'TP':
        session['lang'] = 'br'
        # session['flag'] = 'br'
    elif session['country'] == 'ES' or session['country'] == 'AR' or session['country'] == 'MX' or \
            session['country'] == 'CO' or session['country'] == 'PE' or session['country'] == 'CL' or \
            session['country'] == 'VE' or session['country'] == 'GT' or session['country'] == 'EC' or \
            session['country'] == 'BO' or session['country'] == 'CU' or session['country'] == 'DM' or \
            session['country'] == 'DO' or session['country'] == 'PY' or session['country'] == 'SV' or \
            session['country'] == 'NI' or session['country'] == 'CR' or session['country'] == 'PA' or \
            session['country'] == 'UY' or session['country'] == 'PR':
        session['lang'] = 'es'
        # session['flag'] = 'es'
    else:
        session['lang'] = 'en'
        session['country'] = 'GB'
