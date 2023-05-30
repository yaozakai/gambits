from operator import itemgetter

from flask_login import login_required, logout_user

import utils
from db_access import *
# from email_confirmation import create_verify_email, create_reset_pass_email
# from forms import verify_captcha
from utils import *
from config import app as application
from constants import RECAPTCHA_PUBLIC_KEY
from route_cq9_api import cq9_api, game_launch, player_report_today
from route_template import template
from route_user import user
from route_wallet import wallet, verify_transaction_loop
from utils import reload_game_titles, reload_icon_placement, setup_home_template, set_flag_from_lang, \
    set_session_geo_lang

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
    return db_get_user_from_id(user_id)


@application.route('/', methods=['GET', 'POST'])
def home():
    csrf_token = csrf.generate_csrf()
    session['csrf'] = csrf_token
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token
    if 'lang' not in session:
        # find user's location, defaults to English
        debug_out('looking up geolocation for language setting...')
        set_session_geo_lang(request.remote_addr)
    set_flag_from_lang()
    debug_out('done')

    if 'page' in session:
        if session['page'] == 'gallery':
            return render_template('page-gallery.html', icon_placement=utils.icon_placement,
                                   game_titles=utils.game_titles,
                                   root_path='', login_form=login_form, register_form=register_form,
                                   RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=False,
                                   notification='', notification_title='', reset_pass=False,
                                   lang=session['lang'], translations=utils.translations)
        else:
            if len(request.data) > 0:
                report_date = json.loads(request.data)['reportDate']

            else:
                report_date = str(datetime.datetime.now()).split(' ')[0]

            if session['page'] == 'txnHistory':
                queries = TxnEntry().query.filter_by(user_id=session['_user_id'])
                rec = []
                for query in queries:
                    if pytz.UTC.localize(query.created) < pytz.UTC.localize(datetime.datetime.now()):
                        rec.insert(0, query)
                return render_template('page-txnHistory.html', rec=rec, report_date=report_date,
                                       translations=translations)
            elif session['page'] == 'gameHistory':
                rec = player_report_today(db_get_user().username, report_date)
                # report_date = report_date.strftime('%Y-%m-%d')
                if rec is None:
                    return render_template('page-gamehistory.html', rec=[], translations=utils.translations,
                                           report_date=report_date, lang=session['lang'])
                else:
                    return render_template('page-gamehistory.html', rec=rec['Data'], translations=utils.translations,
                                           report_date=report_date, lang=session['lang'])
            elif session['page'] == 'pendingWithdraw':
                return pendingWithdraw(True)


    else:
        return render_template('page-gallery.html', icon_placement=utils.icon_placement,
                               game_titles=utils.game_titles,
                               root_path='', login_form=login_form, register_form=register_form,
                               RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=False,
                               notification='', notification_title='', reset_pass=False,
                               lang=session['lang'], translations=utils.translations)


@application.route('/verify_transaction', methods=['POST'])
@login_required
def verify_transaction():
    run = True
    count = 0
    amount = 0
    start_time = time.time()
    # check if deposit exists
    user_db = db_get_user()
    # email = user_db.email
    # email = 'lele@gmeow.com'

    existing_deposit_entry = TxnEntry().query.filter_by(txHash=request.json['txHash']).first()

    if existing_deposit_entry.status != 'Complete':

        # db_create_deposit(session['email'], request.json)
        # db_create_deposit(email, request.json)
        if request.json['mode'] == 'pre':
            deposit = TxnEntry('Deposit', user_db.email, user_db.user_id, (request.json['amount']),
                               request.json['currency'],
                               request.json['chain'], 'Pending', request.json['fromAddress'], request.json['txHash'])
            deposit.commit()
        elif request.json['mode'] == 'post':
            deposit = db_get_deposit(request.json['txHash'])

        currency = request.json['currency']

        while run:
            if count < 6:
                count += 1
                print("count: " + str(count))
                amount = verify_transaction_loop(deposit)
                if amount > 0:
                    break
                else:
                    time.sleep(10.0 - ((time.time() - start_time) % 10.0))

        if amount > 0:
            # update user db
            user_db.add_balance(amount, request.json['currency'])
            notification_title = translations['success:wallet'][session['lang']]
            notification = translations['success:txnSuccess'][session['lang']]
            alert_type = 'success:txnSuccess'
        else:
            notification_title = translations['success:waiting'][session['lang']]
            notification = translations['alert:timeout'][session['lang']] + \
                           '<button type="button" class="btn btn-link" style="padding-left: 0px;">' + \
                           translations['alert:clickHere'][session['lang']] + '</button>'
            alert_type = 'alert:timeout'

    return jsonify(amount=amount, currency=currency, alert_type=alert_type, notification_title=notification_title,
                   notification=notification)


@application.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()

    return redirect(url_for('home'))


@application.route('/search_page', methods=['GET', 'POST'])
@login_required
def search():
    return jsonify(render=render_template('page-search.html', rec=[], translations=translations) )


@application.route('/userDetails', methods=['GET'])
@login_required
def userDetails():
    if session['admin']:
        pass


@application.route('/search_user', methods=['GET', 'POST'])
@login_required
def search_user():

    if request.data and 'search_input' in json.loads(request.data):
        search_input = json.loads(request.data)['search_input']

        result = db_search_user(search_input)
        rec = []
        for row in result:
            entry = {'user_id': row.user_id,
                     'created': row.created.strftime('%m/%d/%y - %H:%M'),
                     'username': row.username,
                     'email': row.email,
                     'referral': row.referral,
                     'balance': row.balance_usdt,
                     'currency': row.currency,
                     'active': row.active,
                     'admin': row.admin,
                     'logged_in': row.logged_in
                     }

            rec.append(entry)

        return jsonify(lang=session['lang'], rec=rec)
    else:
        return jsonify(lang=session['lang'], rec=[])



@application.route('/gallery', methods=['POST'])
def gallery():
    session['page'] = 'gallery'
    return redirect(url_for('home'))


@application.route('/txnHistory', methods=['GET', 'POST'])
@login_required
def txnHistory():
    session['page'] = 'txnHistory'

    queries = TxnEntry().query.filter_by(user_id=session['_user_id'])
    if len(json.loads(request.data)['reportDate']) > 0:
        report_date = datetime.datetime.strptime(json.loads(request.data)['reportDate'], '%Y-%m-%d')
    else:
        # report_date = datetime.datetime.now()
        report_date = datetime.datetime.now()

    rec = []
    for query in queries:
        if pytz.UTC.localize(query.created) <= (pytz.UTC.localize(report_date) + datetime.timedelta(days=1)):
            rec.insert(0, query.serialize())

    rec.sort(key=itemgetter('created'), reverse=True)
    # rec.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))

    return jsonify(render=render_template('page-txnHistory.html', rec=rec, report_date=str(report_date).split(' ')[0],
                                          translations=translations))


@application.route('/pendingWithdraw', methods=['GET', 'POST'])
@login_required
def pendingWithdraw(reload=False):
    rec = []

    queries = TxnEntry().query.filter_by(type='Withdraw').filter_by(status='Pending')
    for query in queries:
        rec.insert(0, query.serialize())
    if reload:
        return render_template('page-pendingWithdraw.html', rec=rec, translations=translations)
    else:
        session['page'] = 'pendingWithdraw'

        # queries = queries.query.filter_by(status='Pending')
        # if len(json.loads(request.data)['reportDate']) > 0:
        #     report_date = datetime.datetime.strptime(json.loads(request.data)['reportDate'], '%Y-%m-%d')
        # else:
        #     # report_date = datetime.datetime.now()
        #     report_date = datetime.datetime.now()
        #
        # rec = []
        # for query in queries:
        #     if pytz.UTC.localize(query.created) <= (pytz.UTC.localize(report_date) + datetime.timedelta(days=1)):
        #         rec.insert(0, query.serialize())
        #
        # rec.sort(key=itemgetter('created'), reverse=True)
        # rec.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%d'))

        return jsonify(render=render_template('page-pendingWithdraw.html', rec=rec, translations=translations))

    # rec = player_report_today(db_get_user().username, report_date)
    # if rec is None:
    #     return jsonify(rec=[], report_date=report_date, render=render_template('page-txnHistory.html', rec=[],
    #                                                                            report_date=report_date))
    # else:
    #     return jsonify(rec=[], report_date=report_date, render=render_template('page-txnHistory.html', rec=[],
    #                                                                            report_date=report_date))


@application.route('/gameHistory', methods=['GET', 'POST'])
@login_required
def gameHistory():
    session['page'] = 'gameHistory'
    records = []
    if len(request.data) > 0 and 'reportDate' in json.loads(request.data) and len(
            json.loads(request.data)['reportDate']) > 0:
        report_date = json.loads(request.data)['reportDate']
        rec = player_report_today(db_get_user().username, report_date)
        records = rec['Data']
    else:
        report_date = get_timestamp(False, False)
        # rec = player_report_today(db_get_user().username, report_date)
        report_date = report_date.strftime('%Y-%m-%d')
    return jsonify(render=render_template('page-gamehistory.html', rec=records, translations=utils.translations,
                                          report_date=report_date, lang=session['lang']))


@application.route("/launch", methods=['GET', 'POST'])
@login_required
def launch():
    link = ''
    # if 'logged_in' in session:
    #     if session['logged_in']:
    if '_user_id' in session:
        user = db_get_user()
        if request.data:
            gamecode = json.loads(request.data.decode("utf-8"))['id'].split('_')[0]
            link = game_launch(user.username, gamecode)
    if link:
        return jsonify(link=link)


@application.route('/translate', methods=['POST'])
@login_required
def translate():
    if 'phrase' in request.json:
        phrase = translations[request.json['phrase']][session['lang']]

    return jsonify(phrase=phrase)


@application.route('/translate_alert', methods=['POST'])
@login_required
def translate_alert():
    msg = request.json['msg']
    title = request.json['title']

    return jsonify(msg=translations[msg][session['lang']], title=translations[title][session['lang']])


@application.route('/verify', endpoint='verify_email', methods=['GET'])
def verify_email():
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

    # if request.method == 'POST' and 'language-select' in request.form:
    #     session['lang'] = request.form['language-select']
    # else:
    #     session['lang'] = 'zh-tw'

    return setup_home_template(notification_title, notification, False)


# @application.route('/', methods=['GET', 'POST'])
# def home():
#     csrf_token = csrf.generate_csrf()
#     login_form = LoginForm()
#     login_form.csrf_token.data = csrf_token
#     register_form = RegisterForm()
#     register_form.csrf_token.data = csrf_token
#     if 'lang' not in session:
#         # find user's location, defaults to English
#         debug_out('looking up geolocation for language setting...')
#         set_session_geo_lang(request.remote_addr)
#     session['page'] = 'gallery'
#     # if 'page' in session and session['page'] == 'txnHistory':
#     #     if 'report_date' in session:
#     #         report_date = session['report_date']
#     #     else:
#     #         report_date = str(datetime.datetime.now()).split(' ')[0]
#     # else:
#     #     report_date = ''
#     set_flag_from_lang()
#     debug_out('done')
#     return render_template('page-gallery.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
#                            root_path='', login_form=login_form, register_form=register_form,
#                            RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=False,
#                            notification='', notification_title='', reset_pass=False,
#                            lang=session['lang'], translations=utils.translations)


@application.route('/gameHistory', methods=['GET', 'POST'])
@application.route("/logout", methods=['GET', 'POST'])
@application.route("/launch", methods=['GET', 'POST'])
def redirect_home():
    return redirect(url_for('home'))


# @application.route('/forgot_pass', methods=['POST'])
# def forgot_pass():
#     # check if the email is a user
#     email = json.loads(request.data)['email']
#     if db_getuser_email(email) is not None:
#         create_reset_pass_email(email)
#
#     return jsonify(notification_title=translations['check email'][session['lang']],
#                    notification=translations['email sent to'][session['lang']])
#
#
# @application.route('/reset', endpoint='reset_password', methods=['GET'])
# def reset():
#     token = request.args['token']
#     session['lang'] = request.args['lang']
#     email = 'walt.yao@gmail.com'
#     if len(email) > 0:
#         session["email"] = email
#         return setup_home_template(notification='', notification_title='', reset_pass_popup=True)
#     else:
#         return setup_home_template(notification=translations['token expired'][session['lang']],
#                                    notification_title=translations['reset password'][session['lang']],
#                                    reset_pass_popup=False)
#
#         # return redirect(url_for('home', notification='Token expired, please try again',
#         #                         notification_title='Reset Password'), code=307)
#
#
# @application.route("/set_password", methods=['POST'])
# def set_password():
#     email = session.pop("email", None)
#     password = json.loads(request.data)['password']
#     if db_set_password(email, password) is not None:
#         return jsonify(notification=translations['password has been updated'][session['lang']],
#                        notification_title=translations['reset password'][session['lang']], reset_pass_popup=False)
#     else:
#         return setup_home_template(notification='Account not found',
#                                    notification_title=translations['reset password'][session['lang']],
#                                    reset_pass_popup=False)
#
#
# @application.route('/resend', methods=['POST'])
# def resend():
#     email = json.loads(request.data)['email'][0:-1]
#     create_verify_email(email, translations)
#     return jsonify(notification_title=translations['check email'][session['lang']],
#                    notification=translations['email sent to'][session['lang']])
#
#
# @application.route('/register', methods=['GET', 'POST'])
# def register():
#     if 'lang' not in session:
#         session['lang'] = 'zh-tw'
#
#     # sharing the same captcha as login
#     captcha_response = json.loads(request.data)['recaptcha']
#
#     # verify captcha
#     if verify_captcha(captcha_response):
#         register_form = RegisterForm()
#         email = register_form.email.data
#         if email_valid(email):
#             password_not_valid = validate_password(register_form.password.data, session['lang'])
#             username = register_form.username.data
#             if len(username) > 2:
#                 # CHANGE this to == 0 on production
#                 if len(password_not_valid) != 0:
#                     # check email exists
#                     user = db_getuser_email(email)
#                     if user is None:
#                         # check username exists
#                         user = db_getuser_username(username)
#                         if user is None:
#                             # create the user
#                             create_verify_email(email, translations)
#                             db_new_user(register_form)
#                             return jsonify(notification_title=translations['check email'][session['lang']],
#                                            notification=translations['email sent to'][session['lang']])
#                         else:
#                             if user.is_active():
#                                 return jsonify(error=translations['account exists'][session['lang']])
#                             else:
#                                 return jsonify(error=translations['account exists but not activated'][session['lang']],
#                                                resend_email=email,
#                                                link_text=translations['resend verification'][session['lang']])
#                     else:
#                         if user.is_active():
#                             return jsonify(error=translations['account exists'][session['lang']])
#                         else:
#                             return jsonify(error=translations['account exists but not activated'][session['lang']],
#                                            resend_email=email,
#                                            link_text=translations['resend verification'][session['lang']])
#                 else:
#                     return jsonify(error=password_not_valid)
#             else:
#                 return jsonify(error=translations['username more than 2'][session['lang']])
#         else:
#             return jsonify(error=translations['invalid email format'][session['lang']])
#     else:
#         return jsonify(error=translations['recaptcha not verified'][session['lang']])


@application.route('/reset', endpoint='reset_password', methods=['GET'])
def reset_password():
    token = request.args['token']
    session['lang'] = request.args['lang']
    email = request.args['email']
    if len(email) > 0:
        session["email"] = email
        return setup_home_template(notification='', notification_title='', reset_pass_popup=True)
    else:
        return setup_home_template(notification=translations['token expired'][session['lang']],
                                   notification_title=translations['reset password'][session['lang']],
                                   reset_pass_popup=False)


@application.route('/withdrawRequest', methods=['GET', 'POST'])
@login_required
def withdraw_request():
    user_db = db_get_user()

    ##### make sure you check and make sure the user has enough to withdraw

    if float(request.json['amount']) <= round(user_db.balance_usdt, 2):
        txnHash_temp = str(TxnEntry().query.count())

        withdraw = TxnEntry('Withdraw', user_db.email, user_db.user_id, request.json['amount'],
                            request.json['currency'],
                            request.json['chain'], 'Pending', request.json['fromAddress'], txnHash_temp)
        withdraw.commit()

        user_db.minus_balance(float(request.json["amount"]), 'usdt')

        balances = {'usdt': f'{user_db.balance_usdt:.2f}',
                    'eth': user_db.balance_eth}
        return jsonify(balances)

    flask.abort(400)


@application.route('/getBalance', methods=['GET', 'POST'])
@login_required
def get_balance():
    # if session['logged_in']:
    user_db = db_get_user()
    balances = {'usdt': f'{user_db.balance_usdt:.2f}',
                'eth': user_db.balance_eth}
    return jsonify(balances)
    # if user_db.currency == 'USD':
    #     return f'{user_db.balance:.2f}'
    # return '{:.2f}'.format(user_db.balance) + ' ' + user_db.currency
    # else:
    #     return translations['reload website'][session['lang']]


@application.route('/update', methods=['GET', 'POST'])
def update_games():
    reload_icon_placement()
    reload_game_titles()
    return 'Done'


if __name__ == '__main__':

    reload_icon_placement()
    reload_translations()
    reload_game_titles()
    application.register_blueprint(cq9_api)
    application.register_blueprint(template)
    application.register_blueprint(user)
    application.register_blueprint(wallet)

    print('Socket: ' + socket.gethostname())
    # print('SQLALCHEMY_DATABASE_URI: ' + socket.gethostname())
    if socket.gethostname() == 'srv.gambits.vip':
        application.run(host='0.0.0.0')
    elif socket.gethostname() == 'The-Only-Real-MacBook-Pro.local':
        application.debug = True
        application.run(host='192.168.1.107')
        # application.run(port=8000)
