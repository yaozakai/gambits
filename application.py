import flask as flask

from flask import render_template
from flask_login import login_required, logout_user, login_user
from flask_wtf import csrf


import utils
from db_access import *
from email_confirmation import create_verify_email, create_reset_pass_email
from forms import LoginForm, RegisterForm, verify_captcha
from utils import *
from config import app as application
from constants import RECAPTCHA_PUBLIC_KEY
from route_cq9_api import cq9_api, game_launch, player_report_today
from route_template import template
from utils import reload_game_titles, reload_icon_placement, activate_account, icon_placement, game_titles

uaform = None
ftform = None
theSession = None
iframe_game_toggle = False
stream = ''
datastream = {}
price_array = []


# CAPTCHA_CONFIG = {'SECRET_CAPTCHA_KEY': 'sshhhhhhh secret cphaata key'}

# main = Blueprint('main', __name__)


# reloading will check user login state
@application.login_manager.user_loader
def load_user(user_id):
    return db_get_user(user_id)


@application.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    return render_template('page_search.html', search_page=True, lang=session['lang'])


@application.route('/search_user', methods=['GET', 'POST'])
@login_required
def search_user():
    search_input = json.loads(request.data)['search_input']

    result = db_search_user(search_input)
    rec = []
    for row in result:
        entry = {'user_id': row.user_id,
                 'created': row.created.strftime('%m/%d/%y - %H:%M'),
                 'username': row.username,
                 'email': row.email,
                 'referral': row.referral,
                 'balance': row.balance,
                 'currency': row.currency,
                 'active': row.active,
                 'admin': row.admin,
                 'logged_in': row.logged_in
                 }

        rec.append(entry)

    return jsonify(lang=session['lang'], rec=rec, num_results=len(rec))


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
            return render_template('page_profile.html', rec=[], num_results=0,
                                   report_date=report_date, lang=session['lang'])
        else:
            return render_template('page_profile.html', rec=rec['Data'], num_results=rec['TotalSize'],
                                   report_date=report_date, lang=session['lang'])


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


@application.route('/lang/<token>', methods=['GET', 'POST'])
def language(lang):
    if request.method == 'POST':
        if len(request.data) > 0:
            lang = json.loads(request.data)['lang']
        else:
            lang = 'en'
        return jsonify({'redirect': url_for("/", lang=lang)})


@application.route('/', methods=['GET', 'POST'])
def home():
    # if session['logged_in']:
    #     db_get_user(session['_user_id'])

    notification = ''
    notification_title = ''
    if 'notification' in request.args:
        notification = request.args['notification']
        notification_popup = True
    else:
        notification_popup = False
    if 'notification_title' in request.args:
        notification_title = request.args['notification_title']

    csrf_token = csrf.generate_csrf()
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token

    if request.method == 'POST' and 'language-select' in request.form:
        session['lang'] = request.form['language-select']
    else:
        session['lang'] = 'zh-tw'

    session['flag'] = session['lang']
    if session['flag'] == 'en':
        session['flag'] = 'gb'
    elif session['flag'] == 'zh-tw':
        session['flag'] = 'tw'
    elif session['flag'] == 'zh-cn':
        session['flag'] = 'cn'
    elif session['flag'] == 'ja':
        session['flag'] = 'jp'

    return render_template('gallery.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
                           static_path='', login_form=login_form, register_form=register_form,
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=notification_popup,
                           notification=notification, notification_title=notification_title, reset_pass=False,
                           lang=session['lang'], translations=utils.translations)


@application.route('/login', methods=['POST'])
def login():
    # captcha_response = login_form.data['recaptcha']
    captcha_response = json.loads(request.data)['recaptcha']
    if 'lang' not in session:
        session['lang'] = 'zh-tw'
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
                        session['admin'] = user.is_admin()
                        # output['page'] = 'profile'
                        return jsonify(output)
                        # return render_template('page_profile.html', page_call='profile')
                        # return redirect(next or url_for('profile'))
                    else:
                        return jsonify(error=translations['created not verified'][session['lang']],
                                       resend_email=email,
                                       link_text=translations['resend verification email'][session['lang']])
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
                return jsonify(error=translations['please reload'][session['lang']])
    else:
        return jsonify({"error": translations['recaptcha not verified'][session['lang']]})
    # if LoginForm().validate_on_submit():
    #     return "the form has been submitted. Success!"


@application.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()

    return redirect(url_for('home'))


@application.route('/profile', methods=['GET', 'POST'])
@application.route("/logout", methods=['GET', 'POST'])
@application.route("/launch", methods=['GET', 'POST'])
def redirect_home():
    redirect(url_for('home'))


@application.route('/forgot_pass', methods=['POST'])
def forgot_pass():
    # check if the email is a user
    email = json.loads(request.data)['email']
    if db_getuser_email(email) is not None:
        create_reset_pass_email(email)

    return jsonify(notification_title=translations['forgot password'][session['lang']],
                   notification=translations['email sent to'][session['lang']])


@application.route('/verify', endpoint='verify_email', methods=['GET'])
def verify():
    token = request.args['token']
    session['lang'] = request.args['lang']
    # get the notification
    notification_json = activate_account(token, session['lang'])
    notification = notification_json['notification']
    notification_title = notification_json['notification_title']

    csrf_token = csrf.generate_csrf()
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token

    if request.method == 'POST' and 'language-select' in request.form:
        session['lang'] = request.form['language-select']
    else:
        session['lang'] = 'zh-tw'

    # post_obj = {'notification_popup': True,
    #             'notification': notification_json['notification'],
    #             'notification_title': notification_json['notification_title']
    #             }
        # return render_template('gallery.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
    #                        static_path='', login_form=login_form, register_form=register_form,
    #                        RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=True,
    #                        notification=notification, notification_title=notification_title, reset_pass=False,
    #                        lang=session['lang'], translations=utils.translations)
    # return redirect(url_for('home', json=json.dumps(post_obj)))

    return redirect(url_for('home', notification_popup=True,
                            notification=notification_json['notification'],
                            notification_title=notification_json['notification_title']), code=307)

    # return url_for('home', )


@application.route('/reset', endpoint='reset_password', methods=['GET'])
def reset():
    token = request.args['token']
    session['lang'] = request.args['lang']
    email = 'walt.yao@gmail.com'
    if len(email) > 0:
        session["email"] = email
        return setup_home_template(notification='', notification_title='', reset_pass_popup=True)
    else:
        return setup_home_template(notification=translations['token expired'][session['lang']],
                                   notification_title=translations['reset password'][session['lang']],
                                   reset_pass_popup=False)

        # return redirect(url_for('home', notification='Token expired, please try again',
        #                         notification_title='Reset Password'), code=307)


def setup_home_template(notification_title, notification, reset_pass_popup):
    csrf_token = csrf.generate_csrf()
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token
    if len(notification) > 0:
        notification_popup = True
    else:
        notification_popup = False
    return render_template('gallery.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
                           static_path='../', login_form=login_form, register_form=register_form,
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=notification_popup,
                           notification=notification, notification_title=notification_title,
                           reset_pass=reset_pass_popup)


@application.route("/set_password", methods=['POST'])
def set_password():
    email = session.pop("email", None)
    password = json.loads(request.data)['password']
    if db_set_password(email, password) is not None:
        # return setup_home_template(notification='Password has been updated.  You may log in now!',
        #                            notification_title='Reset password', reset_pass_popup=False)
        # return redirect(url_for('home', notification='Password has been updated.  You may log in now!',
        #                         notification_title='Reset password', notification_popup=True))
        # return redirect('/')
        return jsonify(notification=translations['password has been updated'][session['lang']],
                       notification_title=translations['reset password'][session['lang']], reset_pass_popup=False)
    else:
        return setup_home_template(notification='Account not found',
                                   notification_title=translations['reset password'][session['lang']],
                                   reset_pass_popup=False)


@application.route('/resend', methods=['POST'])
def resend():
    email = json.loads(request.data)['email'][0:-1]
    create_verify_email(email, translations)
    return jsonify(notification_title=translations['verify account'][session['lang']],
                   notification=translations['email sent to'][session['lang']])


@application.route('/register', methods=['GET', 'POST'])
def register():

    if 'lang' not in session:
        session['lang'] = 'zh-tw'

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
                            return jsonify(notification_title=translations['verify account'][session['lang']],
                                           notification=translations['email sent to'][session['lang']])
                        else:
                            if user.is_active():
                                return jsonify(error=translations['account exists'][session['lang']])
                            else:
                                return jsonify(error=translations['account exists but not activated'][session['lang']],
                                               resend_email=email,
                                               link_text=translations['resend verification email'][session['lang']])
                    else:
                        if user.is_active():
                            return jsonify(error=translations['account exists'][session['lang']])
                        else:
                            return jsonify(error=translations['account exists but not activated'][session['lang']],
                                           resend_email=email,
                                           link_text=translations['resend verification email'][session['lang']])
                else:
                    return jsonify(error=password_not_valid)
            else:
                return jsonify(error=translations['username more than 2'][session['lang']])
        else:
            return jsonify(error=translations['invalid email format'][session['lang']])
    else:
        return jsonify(error=translations['recaptcha not verified'][session['lang']])


@application.route('/getBalance', methods=['GET', 'POST'])
@login_required
def get_balance():
    if session['logged_in']:
        user = db_get_user(session['_user_id'])
        return str(user.balance) + ' ' + user.currency
    else:
        return translations['reload website'][session['lang']]


@application.route('/update', methods=['GET', 'POST'])
def update_games():
    reload_icon_placement()
    reload_game_titles()
    return 'Done'


if __name__ == '__main__':
    application.debug = True
    reload_icon_placement()
    reload_translations()
    reload_game_titles()
    application.register_blueprint(cq9_api)
    application.register_blueprint(template)
    application.run()
