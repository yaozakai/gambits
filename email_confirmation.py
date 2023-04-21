from flask import url_for, render_template, session
from itsdangerous import URLSafeTimedSerializer
from config import app
from flask_mail import Mail
import boto3

mail = Mail(app)

email_text = 'Welcome! Thanks for signing up. Please follow this link to activate your account: '


def send_email(subject, recipient, html, text):
    ses_client = boto3.client('ses',
                              region_name=app.config['SES_REGION'],
                              aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                              aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
                              )
    # sending email with all details with amzon ses
    response = ses_client.send_email(
        Destination={'ToAddresses': [recipient], },
        Message={'Body': {'Html': {'Charset': 'UTF-8', 'Data': html, },
                          'Text': {'Charset': 'UTF-8', 'Data': text, }, },
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


def create_verify_email(email, translations):
    token = generate_confirmation_token(email)
    confirm_url = url_for('verify_email', token=token, lang=session['lang'], _external=True)
    html = render_template('email_verify.html', confirm_url=confirm_url, translations=translations)
    subject = "Gambits Casino: " + translations['please verify your email'][session['lang']]
    send_email(subject=subject, recipient=email, html=html, text=email_text + confirm_url)


def create_reset_pass_email(email, translations):
    token = generate_confirmation_token(email)
    confirm_url = url_for('reset_password', lang=session['lang'], token=token, _external=True)
    html = render_template('email_reset_pass.html', confirm_url=confirm_url, translations=translations)
    subject = "Gambits Casino: " + translations['password reset'][session['lang']]
    send_email(subject=subject, recipient=email, html=html)


def create_forgot_password_email(email):
    token = generate_confirmation_token(email)
    confirm_url = url_for('verify_email', token=token, _external=True)
    html = render_template('email_verify.html', confirm_url=confirm_url)
    subject = "Gambits Casino: Please verify your email"
    send_email(subject=subject, recipient=email, html=html)
