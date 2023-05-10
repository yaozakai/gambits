from flask import Blueprint, request, render_template, json, session, redirect, url_for
from flask_wtf import csrf

from forms import LoginForm, RegisterForm
from utils import *

user = Blueprint('user', __name__)


@user.route('/user_new_address', methods=['GET'])
def user_new_address():
    pass




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
