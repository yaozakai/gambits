import flask
from flask import Blueprint, json
from flask_login import login_user

from db_access import *
from forms import verify_captcha
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
