from flask import url_for, render_template
from itsdangerous import URLSafeTimedSerializer
from config import app
from flask_mail import Mail
import boto3
import os


mail = Mail(app)
# app.config.update(dict(
#     DEBUG=True,
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT=465,
#     MAIL_USE_TLS=False,
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME='my_username@gmail.com',
#     MAIL_PASSWORD='my_password',
# ))

email_text = 'Welcome! Thanks for signing up. Please follow this link to activate your account:'


def send_email(subject, recipient, html):
    ses_client = boto3.client('ses',
                              region_name=app.config['SES_REGION'],
                              aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                              aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
                              )
    # sending email with all details with amzon ses
    response = ses_client.send_email(
        Destination={'ToAddresses': [recipient], },
        Message={'Body': {'Html': {'Charset': 'UTF-8', 'Data': html, },
                          'Text': {'Charset': 'UTF-8', 'Data': email_text, }, },
                 'Subject': {'Charset': 'UTF-8', 'Data': subject, }, },
        Source=app.config['SES_EMAIL_SOURCE']
    )


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def create_verify_email(email):
    token = generate_confirmation_token(email)
    confirm_url = url_for('verify_email', token=token, _external=True)
    html = render_template('email.html', confirm_url=confirm_url)
    subject = "Gambits Casino: Please verify your email"
    send_email(subject=subject, recipient=email, html=html)
