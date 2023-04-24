from flask import Flask
# from flask_session import Session
import secrets
from flask_login import LoginManager

from constants import *

app = Flask(__name__)

app.config['SES_REGION'] = 'ap-northeast-2'
app.config['SES_EMAIL_SOURCE'] = 'no-reply@gambits.vip'
app.config['AWS_ACCESS_KEY_ID'] = 'AKIASUDHOIDDYWZ754XV'
app.config['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['SECURITY_PASSWORD_SALT'] = secrets.token_urlsafe(16)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
app.config['RECAPTCHA_USE_SSL'] = False
# app.config['RECAPTCHA_SITE_KEY'] = RECAPTCHA_PUBLIC_KEY  # <-- Add your site key
# app.config['RECAPTCHA_SECRET_KEY'] = RECAPTCHA_PRIVATE_KEY  # <-- Add your secret key
app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_PRIVATE_KEY
app.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'dark'}
# recaptcha = ReCaptcha(app=app) # Create a ReCaptcha object by passing in 'app' as parameter

login_manager = LoginManager()
# login_manager.login_view = 'profile'
app.config.from_object(__name__)
login_manager.init_app(app)
# Mobility(app)

