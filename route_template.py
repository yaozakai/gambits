from flask import Blueprint, request, render_template, json
from flask_wtf import csrf

import utils
from forms import LoginForm, RegisterForm
from consts import RECAPTCHA_PUBLIC_KEY

static_path = 'static'

template = Blueprint('template', __name__)


@template.route('/topbar', methods=['POST'])
def topbar():

    if request.method == 'POST' and 'lang' in request.form:
        lang = request.form['lang']
    else:
        lang = 'en'

    return render_template('topbar.html', static_path=static_path, lang=lang)


@template.route('/modals')
def modals():
    csrf_token = csrf.generate_csrf()
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token
    return render_template('modals.html', login_form=login_form, register_form=register_form,
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY)


@template.route('/navigationbar')
def navigationbar():

    return render_template('navigationbar.html')


@template.route('/carousel')
def carousel():

    return render_template('carousel.html')


@template.route('/gallery')
def gallery():

    if len(request.data) > 0:
        lang = json.loads(request.data)['lang']
    else:
        lang = 'en'

    return render_template('gallery.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
                           static_path='', lang=lang)