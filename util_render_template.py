import json

from flask import render_template, session, jsonify
from flask_wtf import csrf

import utils
from constants import RECAPTCHA_PUBLIC_KEY
from db_classes import TxnEntry, UserEntry
from forms import LoginForm, RegisterForm


def create_db_table(queries):
    loader = []
    for query in queries:
        loader.append(query.as_dict())
        # rec.insert(0, query.serialize())
    return {"total": len(loader), "totalNotFiltered": len(loader), "rows": loader}


def setup_pendingWithdraw_template(wrap=False):
    # rec = []

    # queries = TxnEntry().query.filter_by(type='Withdraw').filter_by(status='Pending')
    queries = TxnEntry().query.all()
    txn_data = create_db_table(queries)
    queries = UserEntry().query.all()
    user_data = create_db_table(queries)
    # loader = []
    # for query in queries:
    #     loader.append(query.as_dict())
    #     # rec.insert(0, query.serialize())
    # txn_data = {"total": len(loader), "totalNotFiltered": len(loader), "rows": loader}

    if wrap:
        return render_template('page-pendingWithdraw-wrap.html', txn_data=txn_data, user_data=user_data,
                               translations=utils.translations)
    else:
        session['page'] = 'pendingWithdraw'
        div_render = render_template('page-pendingWithdraw.html', txn_data=txn_data, user_data=user_data,
                                     translations=utils.translations)
        return jsonify(
            render=render_template('page-pendingWithdraw-wrap.html', txn_data=txn_data, user_data=user_data,
                                   translations=utils.translations),
            div_render=div_render)


def setup_search_template(wrap=False):

    queries = UserEntry().query.all()
    loader = []
    for query in queries:
        loader.append(query.as_dict())
    user_data = {"total": len(loader), "totalNotFiltered": len(loader), "rows": loader}

    if wrap:
        rec = []
        return render_template('page-search-wrap.html', user_data=user_data, translations=utils.translations)
    else:
        session['page'] = 'search_user_page'
        div_render = render_template('page-search.html', user_data=user_data, translations=utils.translations)
        return jsonify(div_render=div_render)


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
