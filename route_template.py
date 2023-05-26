from flask import Blueprint, request, render_template, json, session
from flask_wtf import csrf
from wtforms import Label

from utils import *
from forms import LoginForm, RegisterForm
from constants import RECAPTCHA_PUBLIC_KEY

root_path = 'static'

template = Blueprint('template', __name__)


@template.route('/main_section', methods=['POST', 'GET'])
def main_section():

    # if 'lang' not in session:
    #     session['lang'] = 'zh-tw'
    # if 'page' in session:
    #     if session['page'] == 'txnHistory':
    #         return jsonify(render=render_template('page-txnhistory.html', rec=rec, report_date=report_date,
    #                                               translations=translations))

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
    return render_template('page-gallery.html', icon_placement=icon_placement, game_titles=game_titles,
                           root_path='', login_form=login_form, register_form=register_form,
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, notification_popup=False,
                           notification='', notification_title='', reset_pass=False,
                           lang=session['lang'], translations=translations)


@template.route('/navigationbar', methods=['POST', 'GET'])
def navigationbar():

    # if 'lang' not in session:
    #     session['lang'] = 'zh-tw'

    return render_template('section-navbar.html', lang=session['lang'], translations=translations)


@template.route('/topbar', methods=['POST', 'GET'])
def topbar():

    # if 'lang' not in session:
    #     session['lang'] = 'zh-tw'

    return render_template('section-topbar.html', root_path=root_path, lang=session['lang'], translations=translations)


@template.route('/modals', methods=['POST', 'GET'])
def modals():

    # if 'lang' not in session:
    #     session['lang'] = 'zh-tw'

    csrf_token = csrf.generate_csrf()
    login_form = LoginForm(session['lang'])
    login_form.csrf_token.data = csrf_token
    login_form.login.label = Label("login", translations['log in'][session['lang']])
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token
    register_form.register.label = Label("register", translations['register'][session['lang']])
    return render_template('template-modals.html', login_form=login_form, register_form=register_form,
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, lang=session['lang'], translations=translations,
                           notification_popup=request.form['notification_popup'], notification=request.form['notification'],
                           notification_title=request.form['notification_title'])


@template.route('/topSection')
def top_section():

    return render_template('live-baccarat.html', icon_placement=icon_placement, game_titles=game_titles,
                           root_path='', lang=session['lang'], translations=translations)
