import flask
from flask import Blueprint, request, render_template, json, session, redirect, url_for
from flask_login import login_required
from flask_wtf import csrf

import utils
from db_access import db_set_public_address
from forms import LoginForm, RegisterForm
from utils import *

user = Blueprint('user', __name__)


@user.route('/user_new_address', methods=['POST'])
# @login_required
def user_new_address():
    if 'address' in request.json:
        db_set_public_address(request.json['address'])
        session['publicAddress'] = request.json['address']
        return jsonify(success=True, address=session['publicAddress'], address_set_message=utils.translations['address set'][session['lang']],
                       address_set_title=utils.translations['crypto wallet'][session['lang']])
    else:
        return flask.abort(400)


@user.route('/verify', endpoint='verify_email', methods=['GET'])
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

    return setup_home_template(notification_title, notification, False)

    # return redirect(url_for('home', notification_popup=True,
    #                         notification=notification_json['notification'],
    #                         notification_title=notification_json['notification_title']), code=307)
