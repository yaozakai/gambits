# import database
# import solana
# from solana.rpc.api import Client
import flask as flask
# import cq9_api as cq9_api

# from userAuth import UAT
from flask import render_template
from flask_login import login_required, logout_user, login_user
from flask_wtf import csrf

import utils
from db_access import *
from email_confirmation import create_verify_email
from forms import LoginForm, RegisterForm, verify_captcha
from utils import *
from config import app as application
from consts import RECAPTCHA_PUBLIC_KEY
from cq9_api import cq9_api, game_launch, player_report_today
from utils import reload_game_titles, reload_icon_placement, verify_user, icon_placement, game_titles
from datetime import datetime

uaform = None
ftform = None
theSession = None
iframe_game_toggle = False
stream = ''
datastream = {}
price_array = []
wallet = ''


# CAPTCHA_CONFIG = {'SECRET_CAPTCHA_KEY': 'sshhhhhhh secret cphaata key'}

# main = Blueprint('main', __name__)


# reloading will check user login state
@application.login_manager.user_loader
def load_user(user_id):
    return db_get_user(user_id)


@application.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = session['_user_id']
    # username = '0000-0001'
    if len(request.data) > 0 and 'reportDate' in json.loads(request.data):
        report_date = json.loads(request.data)['reportDate']
        rec = player_report_today(db_get_user(username).username, report_date)
        # report_date = report_date.strftime('%Y-%m-%d')
        return jsonify(rec=rec['Data'], num_results=rec['TotalSize'], report_date=report_date)
    else:
        report_date = get_timestamp(False, False)
        rec = player_report_today(db_get_user(username).username, report_date)
        report_date = report_date.strftime('%Y-%m-%d')
        if rec is None:
            return render_template('profile.html', rec=[], num_results=0,
                                   report_date=report_date)
        else:
            return render_template('profile.html', rec=rec['Data'], num_results=rec['TotalSize'],
                                   report_date=report_date)


@application.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()

    return redirect(url_for('home'))


@application.route("/launch", methods=['GET', 'POST'])
@login_required
def launch():
    link = ''
    if 'logged_in' in session:
        if session['logged_in']:
            if '_user_id' in session:
                user = db_get_user(session['_user_id'])
                if request.data:
                    gamecode = json.loads(request.data.decode("utf-8"))['id'].split('_')[0]
                    link = game_launch(user.username, gamecode)
    if link:
        return jsonify(link=link)


@application.route('/', methods=['GET', 'POST'])
def home():

    # if session['logged_in']:
    #     db_get_user(session['_user_id'])
    notification = ''
    notification_title = ''
    if 'notification' in request.args:
        notification = request.args['notification']
    if 'notification_title' in request.args:
        notification_title = request.args['notification_title']

    csrf_token = csrf.generate_csrf()
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token

    if login_form.validate_on_submit():
        return "you are already logged in"
    else:
        pass
    return render_template('gallery.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles, icon_path=icon_path,
                           login_form=login_form, register_form=register_form, RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY,
                           notification=notification, notification_title=notification_title)


@application.route('/profile', methods=['GET', 'POST'])
@application.route("/logout", methods=['GET', 'POST'])
@application.route("/launch", methods=['GET', 'POST'])
def redirect_home():
    redirect(url_for('home'))


@application.route('/verify/<token>', endpoint='verify_email', methods=['GET'])
def verify(token):
    notification_json = verify_user(token)
    return redirect(url_for('home', notification=notification_json['notification'],
                            notification_title=notification_json['notification_title']), code=307)
    # notification = notification_json['notification']
    # notification_title = notification_json['notification_title']


@application.route('/login', methods=['POST'])
def login():
    # captcha_response = login_form.data['recaptcha']
    captcha_response = json.loads(request.data)['recaptcha']

    # verify captcha
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
                user = db_user_verification(email, password)
                if user is not None:
                    if user.is_active():
                        # log the login
                        db_new_login(login_form)
                        session['logged_in'] = True

                        login_user(user, remember=login_form.rememberme.data)
                        output = user.serialize()
                        # output['page'] = 'profile'
                        return jsonify(output)
                        # return render_template('profile.html', page_call='profile')
                        # return redirect(next or url_for('profile'))
                    else:
                        return jsonify(error='Your account is created but not verified yet',
                                       resend_email=email)
                else:
                    return jsonify(error='Invalid e-mail or password')
            else:
                return jsonify(error='Invalid email format')
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
                return jsonify(error='Please refresh the website')
    else:
        return jsonify({"error": 'reCaptcha not verified'})
    # if LoginForm().validate_on_submit():
    #     return "the form has been submitted. Success!"


@application.route('/resend', methods=['POST'])
def resend():
    email = json.loads(request.data)['email'][0:-1]
    create_verify_email(email)
    return jsonify(notification_title='Verify account', notification='An e-mail has been sent to <b>' + email +
                                                                     '</b>.<br>Please check your email and click the link to verify.')


@application.route('/register', methods=['GET', 'POST'])
def register():
    # sharing the same captcha as login
    captcha_response = json.loads(request.data)['recaptcha']

    # verify captcha
    if verify_captcha(captcha_response):
        register_form = RegisterForm()
        email = register_form.email.data
        if email_valid(email):
            password_not_valid = validate_password(register_form.password.data)
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
                            create_verify_email(email)
                            db_new_user(register_form)
                            return jsonify(notification_title='Verify account',
                                           notification='An e-mail has been sent to <b>' + email +
                                                        '</b>.<br>Please check your inbox and click the link in the '
                                                        'email to verify.')
                        else:
                            if user.is_active():
                                return jsonify(error='Account with this e-mail exists')
                            else:
                                return jsonify(error='Account with this username exists')
                    else:
                        return jsonify(error='Your account is created but not verified yet', resend_email=email)
                else:
                    return jsonify(error=password_not_valid)
            else:
                return jsonify(error='Username must be more than 2 characters')
        else:
            return jsonify(error='Invalid e-mail format')
    else:
        return jsonify(error='reCaptcha not verified')


@application.route('/getBalance', methods=['GET', 'POST'])
@login_required
def get_balance():
    if session['logged_in']:
        user = db_get_user(session['_user_id'])
        return str(user.balance) + ' ' + user.currency
    else:
        return 'Reload website'


@application.route('/update', methods=['GET', 'POST'])
def update_games():

    reload_icon_placement()
    reload_game_titles()
    return 'Done'


if __name__ == '__main__':
    application.debug = True
    reload_icon_placement()
    reload_game_titles()
    application.register_blueprint(cq9_api)
    application.run()
