import flask
from flask import Blueprint, request, render_template, json, session, redirect, url_for
from flask_login import login_required, logout_user, login_user
from flask_wtf import csrf

import utils
from db_access import *
from forms import LoginForm, RegisterForm, verify_captcha
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
                        debug_out('login: flask login')
                        login_user(user_db, remember=login_form.rememberme.data)
                        output = user_db.serialize()
                        session['admin'] = user_db.is_admin()
                        # output['page'] = 'profile'
                        debug_out('login: done, reloading website, check ajax success output')

                        return jsonify(output)
                        # return render_template('page_gamehistory.html', page_call='profile')
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
                return jsonify(error=translations['please reload'][session['lang']])
    else:
        return jsonify({"error": translations['recaptcha not verified'][session['lang']]})
    # if LoginForm().validate_on_submit():
    #     return "the form has been submitted. Success!"


@user.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()

    return redirect(url_for('home'))