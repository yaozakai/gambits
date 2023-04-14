import sys
import subprocess

# implement pip as a subprocess:
# subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel',
#                        'captcha', 'click', 'Flask', 'Flask-Login'])
# Flask
#
# Flask - Mail
# flask_simple_captcha
# flask_sqlalchemy
# Flask - WTF
# itsdangerous
# Jinja2
# MarkupSafe
# psycopg2 - binary
# pytz
# requests
# Werkzeug
# WTForms
# chinese_converter
#
# boto3
#
# conf
#
# SQLAlchemy

subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--no-cache-dir', 'psycopg2-binary==2.9.6', 'pip'])
# subprocess.check_call([sys.executable, '-m',  'pip', 'install', '--upgrade', 'setuptools'])