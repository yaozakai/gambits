import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import url_for, render_template, session, request
from itsdangerous import URLSafeTimedSerializer
from config import app, mail
from flask_mail import Message


# email_text = 'Welcome! Thanks for signing up. Please follow this link to activate your account: '

def send_email(subject, recipient, html, text):
    msg = Message(subject=subject,
                  sender=('Gambit\'s Casino', 'no-reply@gambits.vip'),
                  recipients=[recipient],
                  body=text,
                  html=html)
    mail.send(msg)

    # import smtplib
    # import ssl
    # from email.mime.multipart import MIMEMultipart
    # from email.mime.text import MIMEText
    # sender_email = "no-reply@gambits.vip"
    # receiver_email = "intensity_@hotmail.com"
    # password = "Km09omm9HhwLCz44"
    # message = MIMEMultipart("alternative")
    # message["Subject"] = 'ta-da!'
    # message["From"] = sender_email
    # message["To"] = receiver_email
    # # Turn these into plain/html MIMEText objects
    # part1 = MIMEText('text', "plain")
    # part2 = MIMEText('<br>yesy', "html")
    # # Add HTML/plain-text parts to MIMEMultipart message
    # # The email client will try to render the last part first
    # message.attach(part1)
    # message.attach(part2)
    # # Create secure connection with server and send email
    # context = ssl.create_default_context()
    # with smtplib.SMTP_SSL("smtpout.secureserver.net", 465, context=context) as server:
    #     server.login(sender_email, password)
    #     server.sendmail(
    #         sender_email, receiver_email, message.as_string()
    #     )
    #     server.quit()


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
    html = render_template('email_verify.html', confirm_url=confirm_url, translations=translations,
                           host_url=request.host_url)
    subject = "Gambits Casino: " + translations['please verify your email'][session['lang']]
    send_email(subject=subject, recipient=email, html=html,
               text=translations['email-activate'][session['lang']] + ' ' + confirm_url)


def create_reset_pass_email(email, translations):
    token = generate_confirmation_token(email)
    confirm_url = url_for('reset_password', lang=session['lang'], token=token, _external=True)
    html = render_template('email_reset_pass.html', confirm_url=confirm_url, translations=translations, root_path='../')
    subject = "Gambits Casino: " + translations['password reset'][session['lang']]
    send_email(subject=subject, recipient=email, html=html)

