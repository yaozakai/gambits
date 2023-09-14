import json

from flask import render_template, session, jsonify
from flask_wtf import csrf

import utils
from constants import RECAPTCHA_PUBLIC_KEY
from db_classes import TxnEntry
from forms import LoginForm, RegisterForm
# from utils import translations, icon_placement, game_titles


def setup_pendingWithdraw_template(reload=False):
    rec = []

    queries = TxnEntry().query.filter_by(type='Withdraw').filter_by(status='Pending')
    records = {}
    loader = json.loads(records)
    for query in queries:
        loader.update(query.as_dict())
        rec.insert(0, query.serialize())
    if reload:
        return render_template('page-pendingWithdraw-wrap.html', rec=rec, json=json.dumps(loader), translations=utils.translations)
    else:
        session['page'] = 'pendingWithdraw'
        div_render = render_template('page-pendingWithdraw.html', rec=rec, json=json.dumps(loader), translations=utils.translations)
        return jsonify(
            render=render_template('page-pendingWithdraw-wrap.html', rec=rec, json=json.dumps(loader), translations=utils.translations),
            div_render=div_render)


def setup_search_template():
    session['page'] = 'search'
    div_render = render_template('page-search.html', rec=[], translations=utils.translations)
    return jsonify(render=render_template('page-search.html', rec=[], translations=utils.translations),
                   div_render=div_render)


def setup_home_template(notification_title='', notification='', reset_pass_popup=True):
    csrf_token = csrf.generate_csrf()
    login_form = LoginForm()
    login_form.csrf_token.data = csrf_token
    register_form = RegisterForm()
    register_form.csrf_token.data = csrf_token
    if len(notification) > 0:
        notification_popup = True
    else:
        notification_popup = False
    return render_template('page-gallery-wrap.html', icon_placement=utils.icon_placement, game_titles=utils.game_titles,
                           root_path='../', login_form=login_form, register_form=register_form,
                           RECAPTCHA_PUBLIC_KEY=RECAPTCHA_PUBLIC_KEY, translations=utils.translations,
                           notification_popup=notification_popup,
                           notification=notification, notification_title=notification_title,
                           reset_pass=reset_pass_popup)
