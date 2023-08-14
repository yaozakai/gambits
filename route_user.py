import math
import random
import oauth2 as oauth
import time
import string
import urllib.parse

import flask
from flask import Blueprint, json
from flask_login import login_user, login_required

from constants import SMS_SEVENIO_KEY, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET
from db_access import *
from email_confirmation import create_verify_email, create_reset_pass_email
from forms import verify_captcha
from util_geoloc import set_session_geo_lang
from util_oauth import OAuthSignature
from utils import *

user = Blueprint('user', __name__)


# @user.route('/user_new_address', methods=['POST'])
# # @login_required
# def user_new_address():
#     if 'address' in request.json:
#         db_set_public_address(request.json['address'])
#         session['publicAddress'] = request.json['address']
#         return jsonify(success=True, address=session['publicAddress'], address_set_message=utils.translations['address set'][session['lang']],
#                        address_set_title=utils.translations['crypto wallet'][session['lang']])
#     else:
#         return flask.abort(400)


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


@user.route('/lang/<lang>', methods=['GET'])
def language(lang):
    if request.method == 'GET':
        if len(lang) > 0:
            session['lang'] = lang
            if 'logged_in' in session and session['logged_in'] is True:
                db_set_language()
        else:
            set_session_geo_lang(request.remote_addr)
        set_flag_from_lang()

    return redirect(url_for('home'))


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
def twt_oauth():
    if 'oauth_token' in request.args:
        # make sure oauth_token matches
        db_user = db_get_user()
        # db_user.oauth_token = request.args['oauth_token']

        # match = OAuthEntry().query.filter_by(oauth_token=request.args['oauth_token']).first()
        # if match is None:
        if db_user.oauth_token != request.args['oauth_token']:
            return setup_home_template()
        if 'oauth_verifier' in request.args:
            url = 'https://api.twitter.com/oauth/access_token'
            myobj = {'oauth_consumer_key': TWITTER_CONSUMER_KEY,
                     'oauth_token': request.args['oauth_token'],
                     'oauth_verifier': request.args['oauth_verifier']
                     }

            x = requests.post(url, json=myobj)
            pass


def parseURLparam(big_str, small_str):
    index = big_str.find(small_str) + 1
    index += len(small_str)

    search_str = big_str[index:]
    amp = search_str.find('&')

    param = search_str[:amp]

    return param


@user.route('/connect_twitter', methods=['GET'])
# @login_required
def connect_twitter():
    # Create your consumer with the proper key/secret.
    consumer = oauth.Consumer(key=TWITTER_CONSUMER_KEY,
                              secret=TWITTER_CONSUMER_KEY_SECRET)

    # Request token URL for Twitter.
    request_token_url = "https://api.twitter.com/oauth/request_token"

    # Create our client.
    client = oauth.Client(consumer)

    # The OAuth Client request works just like httplib2 for the most part.
    resp, content = client.request(request_token_url, "GET")

    # Save auth_token
    params = content.decode("utf-8")
    # auth_token = parseURLparam(params, 'auth_token')
    # auth_token_secret = parseURLparam(params, 'auth_token_secret')
    user = db_get_user()
    user.oauth_token = parseURLparam(params, 'auth_token')
    user.oauth_token_secret = parseURLparam(params, 'auth_token_secret')
    db.session.commit()

    # pass
    return 'https://api.twitter.com/oauth/authorize?' + content.decode("utf-8")

    # url = twitter_client()
    #
    #
    # # Set the API endpoint
    # url = "https://api.twitter.com/1.1/statuses/user_timeline.json"

    # Set the base oauth_* parameters along with any other parameters required
    # for the API call.
    # params = {
    #     'oauth_version': '1.0',
    #     # 'oauth_consumer_key': "c_key",x
    #     'oauth_consumer_key': TWITTER_CONSUMER_KEY,
    #     'oauth_token': TWITTER_CONSUMER_KEY,
    #     # 'oauth_token': "t_key",
    #     'oauth_timestamp': int(time.time()),
    #     'oauth_signature_method': 'HMAC-SHA1',
    #     'oauth_nonce': oauth.generate_nonce(),
    # }
    # #
    # # params = {
    # #     'oauth_version': "1.0",
    # #     'oauth_nonce': oauth.generate_nonce(),
    # #     'oauth_timestamp': str(int(time.time())),
    # #     'user': 'joestump',
    # #     'photoid': 555555555555
    # # }
    #
    # # Set up instances of our Token and Consumer. The Consumer.key and
    # # Consumer.secret are given to you by the API provider. The Token.key and
    # # Token.secret is given to you after a three-legged authentication.
    # token = oauth.Token(key="TWITTER_CONSUMER_KEY", secret="tok-test-secret")
    # consumer = oauth.Consumer(key=TWITTER_CONSUMER_KEY, secret=TWITTER_CONSUMER_KEY_SECRET)
    #
    # # Set our token/key parameters
    # params['oauth_token'] = token.key
    # params['oauth_consumer_key'] = consumer.key
    #
    # # Create our request. Change method, etc. accordingly.
    # req = oauth.Request(method="GET", url=url, parameters=params)
    #
    # # Sign the request.
    # signature_method = oauth.SignatureMethod_HMAC_SHA1()
    # req.sign_request(signature_method, consumer, token)
    #
    # pass


    # oauthCtrl = OAuthSignature()
    # oauthCtrl.url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    # oauthCtrl.secrets = {
    #     # 'consumer_secret': stringToBase64(TWITTER_CONSUMER_KEY_SECRET),
    #     'consumer_secret': TWITTER_CONSUMER_KEY_SECRET,
    #     # 'token_secret': stringToBase64(TWITTER_CONSUMER_KEY)
    #     'token_secret': TWITTER_CONSUMER_KEY
    # }
    #
    # params = {
    #     'oauth_version': '1.0',
    #     'oauth_consumer_key': "c_key",
    #     # 'oauth_consumer_key': TWITTER_CONSUMER_KEY_SECRET,
    #     # 'oauth_token': TWITTER_CONSUMER_KEY,
    #     'oauth_token': "t_key",
    #     'oauth_timestamp': int(time.time()),
    #     'oauth_signature_method': 'HMAC-SHA1',
    #     'oauth_nonce': oauthCtrl.nonce()
    # }
    #
    # signature = oauthCtrl.generate(params)
    #
    # params['oauth_signature'] = signature
    #
    # x = requests.post('https://api.twitter.com/oauth/request_token', headers=header, data=params)
    #
    # try:
    #     launch_url = json.loads(x.text)['data']['url']
    # except:
    #     launch_url = ''
    # return launch_url


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
