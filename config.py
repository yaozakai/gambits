import secrets
import socket

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO

from constants import *
from flask_discord import DiscordOAuth2Session

#
import os

app = Flask('GambitFlask')
app.config.from_object('config')

# app.config['SERVER_NAME'] = '192.168.0.107:5000'
app.config['MAIL_SERVER'] = 'smtpout.secureserver.net'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'no-reply@gambits.vip'
app.config['MAIL_PASSWORD'] = 'Km09omm9HhwLCz44'
# app.config['MAIL_USERNAME'] = 'fd2972476e41bace13b99e5a60cb5e0f'
# app.config['MAIL_PASSWORD'] = 'ef3b620094a614e516615983cc7dce89'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['SECURITY_PASSWORD_SALT'] = secrets.token_urlsafe(16)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
# app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
app.config['RECAPTCHA_USE_SSL'] = False
# app.config['RECAPTCHA_SITE_KEY'] = RECAPTCHA_PUBLIC_KEY  # <-- Add your site key
# app.config['RECAPTCHA_SECRET_KEY'] = RECAPTCHA_PRIVATE_KEY  # <-- Add your secret key
app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_PRIVATE_KEY
app.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'dark'}
# recaptcha = ReCaptcha(app=app) # Create a ReCaptcha object by passing in 'app' as parameter
app.config["DISCORD_CLIENT_ID"] = DISCORD_CLIENT_KEY    # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = DISCORD_CLIENT_SECRET              # Discord client secret.

if 'env' not in os.environ:
    if socket.gethostname() == 'srv.gambits.vip':
        os.environ['env'] = 'prod'
        CQ9_AGENT_KEY = CQ9_AGENT_KEY_REMOTE_PROD
        app.config["DISCORD_REDIRECT_URI"] = "https://gambits.vip/oauth/discord"  # URL to your callback endpoint.
    else:
        os.environ['env'] = 'stage'
        CQ9_AGENT_KEY = CQ9_AGENT_KEY_LOCAL
        app.config["DISCORD_REDIRECT_URI"] = "https://995a-2001-b011-2000-34c1-2cd0-84ed-70d9-f022.ngrok-free.app/oauth/discord/callback"  # URL to your callback endpoint.
else:
    if os.environ['env'] == 'stage':
        CQ9_AGENT_KEY = CQ9_AGENT_KEY_REMOTE_STAGE
        app.config["DISCORD_REDIRECT_URI"] = "https://stage.gambits.vip/oauth/discord"                 # URL to your callback endpoint.
    else:
        app.config["DISCORD_REDIRECT_URI"] = "https://gambits.vip/oauth/discord"                 # URL to your callback endpoint.


app.config["DISCORD_BOT_TOKEN"] = DISCORD_BOT_TOKEN                   # Required to access BOT resources.


socketio = SocketIO(app, cors_allowed_origins='*')

login_manager = LoginManager()
# login_manager.login_view = 'profile'
app.config.from_object(__name__)
login_manager.init_app(app)
mail = Mail(app)
discord = DiscordOAuth2Session(app)
# Mobility(app)
