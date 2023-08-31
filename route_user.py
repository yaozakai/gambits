import math
import random
import urllib

import oauth2 as oauth

from flask import Blueprint, json, redirect, url_for
from flask_login import login_user, login_required

from constants import SMS_SEVENIO_KEY, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET
from db_access import *
from email_confirmation import create_verify_email, create_reset_pass_email
from forms import verify_captcha, LoginForm, RegisterForm
from util_geoloc import set_session_geo_lang
from util_render_template import setup_home_template
from utils import *

# Create OAUTH client.
consumer = oauth.Consumer(key=TWITTER_CONSUMER_KEY, secret=TWITTER_CONSUMER_KEY_SECRET)
client = oauth.Client(consumer)

user = Blueprint('user', __name__)


def tweet_twitter():
    token = oauth.Token('1486009629792698369-q6Zv5ksJ3OCOi76XP7Q637Mpd9FWGf', '3OBx6AbCb1SyAZHqNPFrufS8ptqVAkzvgc8lHdTdY3B7j')
    # consumer = oauth.Consumer(consumer_key, consumer_secret)

    client = oauth.Client(consumer, token)

    data = {'status': 'hello world'}
    request_uri = 'https://api.twitter.com/1/statuses/update.json'

    resp, content = client.request(request_uri, 'POST', urllib.parse.urlencode(data))
    pass


@user.route('/login', methods=['POST'])
def login():
    # captcha_response = login_form.data['recaptcha']
    captcha_response = json.loads(request.data)['recaptcha']
    # verify captcha
    debug_out('login: verifying captcha')
    if verify_captcha(captcha_response):
        login_form = LoginForm()
        if login_form.validate_on_submit():
            email = login_form.email.data
            password = login_form.password.data
            # rememberme = login_form.rememberme.data

            next_request = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next_request):
                return flask.abort(400)

            # verify valid email
            if email_valid(email):
                # check user exists and then verify password
                debug_out('login: authenticating')
                user_db = db_user_verification(email, password)
                if user_db is not None:
                    if user_db.is_active():
                        # log the login
                        debug_out('login: update login db')
                        db_new_login(login_form)
                        session['logged_in'] = True

                        session['lang'] = user_db.get_lang()
                        # debug_out('login: flask login')
                        login_user(user_db, remember=login_form.rememberme.data)
                        output = user_db.serialize()
                        session['admin'] = user_db.is_admin()
                        # output['page'] = 'profile'
                        debug_out('login: done, reloading website, check ajax success output')

                        return jsonify(output)
                        # return render_template('page-gamehistory.html', page_call='profile')
                        # return redirect(next or url_for('profile'))
                    else:
                        return jsonify(error=translations['created not verified'][session['lang']],
                                       resend_email=email,
                                       link_text=translations['resend verification'][session['lang']])
                else:
                    return jsonify(error=translations['invalid email or password'][session['lang']])
            else:
                return jsonify(error=translations['invalid email format'][session['lang']])
        else:
            if len(login_form.email.errors):
                email_error = login_form.email.errors[0]
            else:
                email_error = ''
            if len(login_form.password.errors):
                password_error = login_form.password.errors[0]
            else:
                password_error = ''
            if email_error or password_error:
                return jsonify(error="", email_error=email_error, password_error=password_error)
            else:
                return jsonify(error=translations['reload:msg'][session['lang']])
    else:
        return jsonify({"error": translations['recaptcha not verified'][session['lang']]})
    # if LoginForm().validate_on_submit():
    #     return "the form has been submitted. Success!"


# @user.route('/lang/<lang>', methods=['GET'])
# def language(lang):
#     if len(lang) > 0:
#         session['lang'] = lang
#         if 'logged_in' in session and session['logged_in'] is True:
#             db_set_language()
#     else:
#         # set_session_geo_lang(request.remote_addr)
#         set_session_geo_lang()
#
#         set_flag_from_lang()
#     return redirect(url_for('home'))
#     # return setup_home_template()


@user.route('/forgot_pass', methods=['POST'])
def forgot_pass():
    # check if the email is a user
    email = json.loads(request.data)['email']
    if db_getuser_email(email) is not None:
        create_reset_pass_email(email, translations)

    return jsonify(notification_title=translations['check email'][session['lang']],
                   notification=translations['email sent to'][session['lang']])
    # return redirect(url_for('home', notification='Token expired, please try again',
    #                         notification_title='Reset Password'), code=307)


@user.route("/set_password", methods=['POST'])
def set_password():
    email = session.pop("email", None)
    password = json.loads(request.data)['password']
    if db_set_password(email, password) is not None:
        return jsonify(notification=translations['password has been updated'][session['lang']],
                       notification_title=translations['reset password'][session['lang']], reset_pass_popup=False)
    else:
        return setup_home_template(notification='Account not found',
                                   notification_title=translations['reset password'][session['lang']],
                                   reset_pass_popup=False)


@user.route('/resend', methods=['POST'])
@login_required
def resend():
    email = json.loads(request.data)['email'][0:-1]
    create_verify_email(email, translations)
    return jsonify(notification_title=translations['check email'][session['lang']],
                   notification=translations['email sent to'][session['lang']])


@user.route('/register', methods=['GET', 'POST'])
def register():
    # if 'lang' not in session:
    #     session['lang'] = 'zh-tw'

    # sharing the same captcha as login
    captcha_response = json.loads(request.data)['recaptcha']

    # verify captcha
    if verify_captcha(captcha_response):
        register_form = RegisterForm()
        email = register_form.email.data
        if email_valid(email):
            password_not_valid = validate_password(register_form.password.data, session['lang'])
            username = register_form.username.data
            if len(username) > 2:
                # CHANGE this to == 0 on production
                if len(password_not_valid) != 0:
                    # check email exists
                    user = db_getuser_email(email)
                    if user is None:
                        # check username exists
                        user = db_getuser_username(username)
                        if user is None:
                            # create the user
                            create_verify_email(email, translations)
                            db_new_user(register_form)
                            return jsonify(notification_title=translations['check email'][session['lang']],
                                           notification=translations['email sent to'][session['lang']])
                        else:
                            if user.is_active():
                                return jsonify(error=translations['account exists'][session['lang']])
                            else:
                                return jsonify(error=translations['account exists but not activated'][session['lang']],
                                               resend_email=email,
                                               link_text=translations['resend verification'][session['lang']])
                    else:
                        if user.is_active():
                            return jsonify(error=translations['account exists'][session['lang']])
                        else:
                            return jsonify(error=translations['account exists but not activated'][session['lang']],
                                           resend_email=email,
                                           link_text=translations['resend verification'][session['lang']])
                else:
                    return jsonify(error=password_not_valid)
            else:
                return jsonify(error=translations['username more than 2'][session['lang']])
        else:
            return jsonify(error=translations['invalid email format'][session['lang']])
    else:
        return jsonify(error=translations['recaptcha not verified'][session['lang']])


@user.route('/verifySMScode', methods=['GET', 'POST'])
@login_required
def verifySMScode():
    code = json.loads(request.data)['code']
    db_user = db_get_user()

    dataclass_phone = PhoneEntry().query.filter_by(phone=json.loads(request.data)['phone']).first()
    if dataclass_phone is not None:
        if dataclass_phone.verified:
            return jsonify(error=2)
        else:
            difference = datetime.datetime.now() - dataclass_phone.timestamp
            if difference.seconds > 900:
                return jsonify(error=4)
    else:
        return jsonify(error=3)

    if dataclass_phone.otp == code:

        db_user.snb_phone = json.loads(request.data)['phone']

        dataclass_phone.verified = True

        db.session.commit()
        return jsonify(error=0)
    else:
        return jsonify(error=1)


@user.route('/api/twt_oauth', methods=['GET', 'POST'])
# @login_required
def twt_oauth():
    if 'oauth_token' in request.args:
        # make sure oauth_token matches
        # db_user = db_get_user()
        # db_user.oauth_token = request.args['oauth_token']

        # match = UserEntry().query.filter_by(oauth_token=request.args['oauth_token']).first()
        if session['oauth_token'] == request.args['oauth_token']:
            if 'oauth_verifier' in request.args:
                # request_token = session['request_token']
                token = oauth.Token(
                    session['oauth_token'],
                    session['oauth_token_secret']
                )
                token.set_verifier(request.args['oauth_verifier'])
                oauth_client = oauth.Client(consumer, token)

                # Request token URL for Twitter.
                request_token_url = "https://api.twitter.com/oauth/access_token"

                headers = {
                         # 'Accept': '*/*',
                         # 'Connection': 'close',
                         # 'User-Agent':  'OAuth gem v0.4.4',
                         'Content-Type': 'application/x-www-form-urlencoded',
                         # 'Content-Length': '76',
                         # 'Host': 'api.twitter.com'
                         }
                resp, content = oauth_client.request(request_token_url, "POST", headers=headers)
                params = content.decode("utf-8")

                user = db_get_user()
                if user:
                    twitter_name = parseURLparam(params, 'screen_name')
                    user.oauth_token = parseURLparam(params, 'oauth_token')
                    user.oauth_token_secret = parseURLparam(params, 'oauth_token_secret')
                    user.twt_user_id = parseURLparam(params, 'user_id')
                    user.snb_twitter = twitter_name
                    db.session.commit()
                    session['notify'] = 'oauth'
                    session['twitter_name'] = twitter_name
                    return redirect(url_for('home'))
                else:
                    flask.abort(69)
                # return setup_home_template(notification=translations['snb:subtask:twt:success'][session['lang']],
                #                            notification_title=translations['snb:subtask:twt'][session['lang']])

    return redirect(url_for('home'))


def parseURLparam(big_str, small_str):
    index = big_str.find(small_str) + 1
    index += len(small_str)

    search_str = big_str[index:]
    amp = search_str.find('&')

    param = search_str[:amp]

    return param


@user.route('/connect_twitter', methods=['GET'])
@login_required
def connect_twitter():
    # Create your consumer with the proper key/secret.
    # consumer = oauth.Consumer(key=TWITTER_CONSUMER_KEY,
    #                           secret=TWITTER_CONSUMER_KEY_SECRET)

    # Request token URL for Twitter.
    request_token_url = "https://api.twitter.com/oauth/request_token"

    # Create our client.
    # client = oauth.Client(consumer)

    # The OAuth Client request works just like httplib2 for the most part.
    resp, content = client.request(request_token_url, "GET")

    # Save auth_token
    params = content.decode("utf-8")
    # auth_token = parseURLparam(params, 'auth_token')
    if parseURLparam(params, 'oauth_callback_confirmed'):
        session['oauth_token'] = parseURLparam(params, 'oauth_token')
        session['oauth_token_secret'] = parseURLparam(params, 'oauth_token_secret')
        # pass
        return 'https://api.twitter.com/oauth/authorize?' + content.decode("utf-8")
        # return redirect('https://api.twitter.com/oauth/authorize?' + content.decode("utf-8"))


@user.route('/sendSMS', methods=['GET', 'POST'])
@login_required
def sendSMS():
    url_target = 'https://gateway.sms77.io/api/sms'
    to = json.loads(request.data)['recipient']

    # create OTP code
    digits = "0123456789"
    otp_code = ""
    for i in range(4):
        otp_code += digits[math.floor(random.random() * 10)]

    phoneEntry = PhoneEntry().query.filter_by(phone=to).first()
    if phoneEntry is not None:
        if phoneEntry.verified:
            return jsonify(error=2)
        else:
            # user is retrying, not verified yet
            phoneEntry.otp = otp_code
            phoneEntry.timestamp = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))

    else:
        phoneEntry = PhoneEntry()
        phoneEntry.phone = to
        phoneEntry.otp = otp_code
        db.session.add(phoneEntry)

    db.session.commit()

    message = translations['sms:title'][session['lang']] + ' ' + otp_code + '\n' + \
              translations['sms:expires'][session['lang']]

    payload = {'p': SMS_SEVENIO_KEY,
               'to': to,
               'from': "Gambit's",
               'text': message
               }
    x = requests.post(url_target, data=payload)
    try:
        # if x.content.decode("utf-8").split('\n')[0] == '100':
        if x.content.decode("utf-8") == '100':
            return jsonify(error=0)
        else:
            return jsonify(error=1)
    except:
        return jsonify(error=1)

    return jsonify(error=1)
