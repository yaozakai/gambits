# import sys
# from operator import itemgetter
from operator import itemgetter
from os import environ
from threading import Lock

from flask import render_template, redirect, url_for
# from os import environ

# from waitress import serve

from flask_login import login_required, logout_user
from flask_wtf import csrf

import utils
from db_access import *
from forms import LoginForm, RegisterForm
from util_geoloc import set_session_geo_lang
from util_render_template import setup_pendingWithdraw_template, setup_search_template, setup_home_template
# from util_geoloc import set_session_geo_lang
# from email_confirmation import create_verify_email, create_reset_pass_email
# from forms import verify_captcha
from utils import *
from config import app as application, socketio
from constants import RECAPTCHA_PUBLIC_KEY, BANK_ADDRESS, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET
# from route_stage import stage
from route_cq9_api import cq9_api, game_launch, player_report_today
# from route_template import template
from route_user import user, tweet_twitter
from route_wallet import wallet, etherscan_parser
# from utils import set_flag_from_lang
from utils import reload_game_titles, reload_icon_placement

from os.path import abspath, dirname

app.root_path = abspath(dirname(__file__))

uaform = None
ftform = None
theSession = None
iframe_game_toggle = False
stream = ''
datastream = {}
price_array = []

thread = None
thread_lock = Lock()

icon_placement = []
game_titles = []


# CAPTCHA_CONFIG = {'SECRET_CAPTCHA_KEY': 'sshhhhhhh secret cphaata key'}

# main = Blueprint('main', __name__)


# reloading will check user login state
@application.login_manager.user_loader
def load_user(user_id):
    return db_get_user_from_id(user_id)


@application.route('/', methods=['GET', 'POST'])
def home():
    # notifications
    notification = ''
    notification_title = ''
    notification_popup = False
    if 'notify' in session:
        notification_popup = True
        if session['notify'] == 'oauth':
            notification = translations['snb:subtask:twt:success'][session['lang']]
            notification_title = translations['snb:subtask:twt'][session['lang']]

    # lang selector
    if 'lang' in request.args:
        session['lang'] = request.args['lang']
        return redirect(url_for('home'))

    csrf_token = csrf.generate_csrf()
    session['csrf'] = csrf_token
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token
    if 'lang' not in session or 'country' not in session:
        # find user's location, defaults to English
        set_session_geo_lang()
    set_flag_from_lang()
    debug_out('done')

    session['env'] = environ['env']

    if 'ref' in request.args:
        session['ref'] = request.args['ref']

    if 'page' in session:
        if session['page'] == 'gallery':
            return render_template('page-gallery-wrap.html', icon_placement=utils.icon_placement,
                                   game_titles=utils.game_titles,
                                   root_path='', login_form=login_form, register_form=register_form,
                                   RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=notification_popup,
                                   notification=notification, notification_title=notification_title, reset_pass=False,
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
                        rec.insert(0, query.serialize())
                rec.sort(key=itemgetter('created'), reverse=True)
                return render_template('page-txnHistory-wrap.html', rec=rec, report_date=report_date,
                                       translations=utils.translations)
            elif session['page'] == 'gameHistory':
                rec = player_report_today(db_get_user().username, report_date)
                # report_date = report_date.strftime('%Y-%m-%d')
                if rec is None:
                    return render_template('page-gamehistory-wrap.html', rec=[], translations=utils.translations,
                                           report_date=report_date, lang=session['lang'])
                else:
                    return render_template('page-gamehistory-wrap.html', rec=rec['Data'],
                                           translations=utils.translations,
                                           report_date=report_date, lang=session['lang'])
            elif session['page'] == 'pendingWithdraw':
                return pendingWithdraw(True)
            elif session['page'] == 'search':
                return search()

    else:
        session['page'] = 'gallery'
        return render_template('page-gallery-wrap.html', icon_placement=utils.icon_placement,
                               game_titles=utils.game_titles,
                               root_path='', login_form=login_form, register_form=register_form,
                               RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=notification_popup,
                               notification=notification, notification_title=notification_title, reset_pass=False,
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

    txHash = request.json['txHash']

    if request.json['mode'] == 'pre':
        deposit = TxnEntry('Deposit', user_db.email, user_db.user_id, (request.json['amount']),
                           request.json['currency'],
                           request.json['chain'], 'Pending', request.json['fromAddress'], txHash)
        deposit.commit()
        lookup_address = BANK_ADDRESS
    elif request.json['mode'] == 'reconcile':
        # deposit = db_get_deposit(txHash)
        # lookup_address = request.json['fromAddress']
        new_txhash = request.json['txHash']
        old_reconcile_id = request.json['fromAddress']
        # mark deposit complete
        deposit = db_get_deposit(old_reconcile_id)
        deposit.mark_complete(new_txhash)
        return jsonify(deposit.serialize())
        # deposit.commit()
        # reconciled_txHash = request.json['txHash']
    elif request.json['mode'] == 'reverify':
        deposit = db_get_deposit(txHash)
        # deposit = TxnEntry().query.filter_by(txHash=txHash).first()

    if deposit.status != 'Complete':

        while run:
            if count < 3:
                count += 1
                print("count: " + str(count))
                amount = etherscan_parser(deposit)
                if amount > 0:
                    break
                else:
                    time.sleep(10.0 - ((time.time() - start_time) % 10.0))

        if amount > 0:
            # update user db
            user_db.add_balance(amount, request.json['currency'])

            # pop up notification
            notification_title = translations['success:wallet'][session['lang']]
            notification = translations['success:txnSuccess'][session['lang']]
            alert_type = 'success:txnSuccess'
        else:
            notification_title = translations['success:waiting'][session['lang']]
            notification = translations['alert:timeout'][session['lang']] + \
                           '<button type="button" class="btn btn-link" style="padding-left: 0px;">' + \
                           translations['alert:clickHere'][session['lang']] + '</button>'
            alert_type = 'alert:timeout'

    return jsonify(amount=amount, currency=request.json['currency'], alert_type=alert_type,
                   notification_title=notification_title,
                   notification=notification, reconciled_txHash=deposit.txHash, balance=user_db.balance_usdt)


@application.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()

    return redirect(url_for('home'))


@application.route('/search_page', methods=['GET', 'POST'])
@login_required
def search():
    return setup_search_template()
    # session['page'] = 'search'
    # div_render = render_template('page-search.html', rec=[], translations=utils.translations)
    # return jsonify(render=render_template('page-search.html', rec=[], translations=utils.translations),
    #                div_render=div_render)


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
    # return redirect(url_for('home'))
    return render_template('page-gallery.html', icon_placement=utils.icon_placement,
                           game_titles=utils.game_titles,
                           root_path='', login_form='', register_form='',
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=False,
                           notification='', notification_title='', reset_pass=False,
                           lang=session['lang'], translations=utils.translations)


@application.route('/txnHistory', methods=['GET', 'POST'])
@login_required
def txnHistory():
    session['page'] = 'txnHistory'

    queries = TxnEntry().query.filter_by(user_id=session['_user_id'])
    if len(request.data) > 0 and len(json.loads(request.data)['reportDate']) > 0:
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
    div_render = render_template('page-txnHistory.html', rec=rec, report_date=str(report_date).split(' ')[0],
                                 translations=utils.translations)
    return jsonify(
        render=render_template('page-txnHistory-wrap.html', rec=rec, report_date=str(report_date).split(' ')[0],
                               translations=utils.translations), div_render=div_render)


@application.route('/pendingWithdraw', methods=['GET', 'POST'])
@login_required
def pendingWithdraw(reload=False):
    return setup_pendingWithdraw_template(reload)


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
    div_render = render_template('page-gamehistory.html', rec=records, translations=utils.translations,
                                 report_date=report_date, lang=session['lang'])
    return jsonify(render=render_template('page-gamehistory-wrap.html', rec=records, translations=utils.translations,
                                          report_date=report_date, lang=session['lang']), div_render=div_render)


@application.route("/launch", methods=['GET', 'POST'])
@login_required
def launch():
    link = ''
    # if 'logged_in' in session:
    #     if session['logged_in']:
    if '_user_id' in session:
        user_db = db_get_user()
        if request.data:
            gamecode = json.loads(request.data.decode("utf-8"))['id'].split('_')[0]
            link = game_launch(user_db.username, gamecode)

    return jsonify(link=link)


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


@application.route('/gameHistory', methods=['GET', 'POST'])
@application.route("/logout", methods=['GET', 'POST'])
@application.route("/launch", methods=['GET', 'POST'])
def redirect_home():
    return redirect(url_for('home'))


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

    if float(request.json['amount']) <= round(user_db.balance_usdt, 2):
        txnHash_temp = str(TxnEntry().query.count() + 1)

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


def background_thread():
    print("Initiating balance updater for user:" + session['_user_id'])
    while True:
        socketio.emit('balance', {'value': db_get_balance()})
        socketio.sleep(1)


@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', request.sid)


# def tweet_twitter_pic():
#     twitter = Twython(
#         app_key=TWITTER_CONSUMER_KEY,
#         app_secret=TWITTER_CONSUMER_KEY_SECRET,
#         oauth_token='1486009629792698369-q6Zv5ksJ3OCOi76XP7Q637Mpd9FWGf',
#         oauth_token_secret='3OBx6AbCb1SyAZHqNPFrufS8ptqVAkzvgc8lHdTdY3B7j'
#     )
#
#     twitter.update_status_with_media(media='static/logos/favicon.png', status='wazzaaaaaa!')
#     pass


def create_app():
    with application.test_request_context():
        # global game_titles, icon_placement
        reload_icon_placement()
        reload_translations()
        reload_game_titles()
        tweet_twitter()

    # application.register_blueprint(template)
    application.register_blueprint(cq9_api)
    application.register_blueprint(user)
    application.register_blueprint(wallet)

    return application


if __name__ == '__main__':

    with application.test_request_context():
        reload_icon_placement()
        reload_translations()
        reload_game_titles()

    print('Socket: ' + socket.gethostname())
    environ['env'] = 'stage'

    if socket.gethostname() == 'srv.gambits.vip':
        application.run(host='0.0.0.0')
    elif socket.gethostname() == 'The-Only-Real-MacBook-Pro.local':
        application.debug = True
        application.run(host='192.168.1.107')
