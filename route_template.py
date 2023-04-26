from flask import Blueprint, request, render_template, json, session
from flask_wtf import csrf
from wtforms import Label

import utils
from forms import LoginForm, RegisterForm
from constants import RECAPTCHA_PUBLIC_KEY

static_path = 'static'

template = Blueprint('template', __name__)


@template.route('/topbar', methods=['POST', 'GET'])
def topbar():

    if 'lang' not in session:
        session['lang'] = 'zh-tw'

    return render_template('section-topbar.html', static_path=static_path, lang=session['lang'], translations=utils.translations)


@template.route('/navigationbar', methods=['POST', 'GET'])
def navigationbar():

    if 'lang' not in session:
        session['lang'] = 'zh-tw'

    return render_template('section-navbar.html', lang=session['lang'], translations=utils.translations)


@template.route('/modals', methods=['POST', 'GET'])
def modals():

    if 'lang' not in session:
        session['lang'] = 'zh-tw'

    csrf_token = csrf.generate_csrf()
    login_form = LoginForm(session['lang'])
    login_form.csrf_token.data = csrf_token
    login_form.login.label = Label("login", utils.translations['log in'][session['lang']])
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token
    register_form.register.label = Label("register", utils.translations['register'][session['lang']])
    return render_template('modals.html', login_form=login_form, register_form=register_form,
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, lang=session['lang'], translations=utils.translations,
                           notification_popup=request.form['notification_popup'], notification=request.form['notification'],
                           notification_title=request.form['notification_title'])


@template.route('/topSection')
def top_section():

    return render_template('live-baccarat.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
                           static_path='', lang=session['lang'], translations=utils.translations)


@template.route('/midSection')
def mid_section():

    return render_template('gallery.html', translations=utils.translations, icon_placement=utils.icon_placement,
                           game_titles=utils.game_titles, static_path='')


@template.route('/botSection')
def bot_section():

    return render_template('gallery.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
                           static_path='', lang=session['lang'], translations=utils.translations)
