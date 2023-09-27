#1)Как выгружать Приложение - Day_70 (https://www.udemy.com/course/100-days-of-code/learn/lecture/39239818)

#2)Flask-Bootstrap and Bootstrap-Flask can’t live together, so you have to uninstall Flask-Bootstrap first
# and then install Bootstrap-Flask:
#$ pip uninstall flask-bootstrap
#$ pip install bootstrap-flask

#3)If you accidentally installed both of them, you will need to uninstall them both first:
#$ pip uninstall flask-bootstrap bootstrap-flask
#$ pip install bootstrap-flask


from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap4
from flask_ckeditor import CKEditor
from datetime import date
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from flask_gravatar import Gravatar
import os
import bleach  #pip install bleach
from dotenv import load_dotenv

import smtplib
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import lxml.html

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL, Length
from flask_ckeditor import CKEditor, CKEditorField

load_dotenv ('E:\\PycharmProjects\\EnvironmentVariables\\.env')
MY_EMAIL = os.getenv("MY_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD") ##Using App Password instead of common Gggole email passeord
##For details of Google App Password see https://towardsdatascience.com/automate-sending-emails-with-gmail-in-python-449cc0c3c317

app = Flask(__name__)#creating a Flask type object
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")

app.app_context().push()
ckeditor = CKEditor(app)
bootstrap=Bootstrap4(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

class ContactForm(FlaskForm):
    email=EmailField('Enter your email', validators=[DataRequired()])
    name = StringField('Enter your name', validators=[DataRequired()])
    message_subject=StringField('Subject', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField("Submit")

##SANITIZING HTML
def strip_invalid_html(content):
    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
                    'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
                    'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                    'thead', 'tr', 'tt', 'u', 'ul']
    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }
    cleaned = bleach.clean(content,
                           tags=allowed_tags,
                           attributes=allowed_attrs,
                           strip=True)
    return cleaned

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        send_mail(fromaddr=MY_EMAIL,
                  toaddr=MY_EMAIL,
                  user_email=strip_invalid_html(contact_form.email.data),
                  name=strip_invalid_html(contact_form.name.data),
                  subject=f'Email from my Blog Capstone Project: {strip_invalid_html(contact_form.message_subject.data)}',
                  message=strip_invalid_html(contact_form.message.data))
        contact_form = ContactForm(formdata=None)
        return render_template("contact.html", msg_sent=True, form=contact_form)

    else:
        flash("Please fill in the name, email and message fields to send a message.")
        render_template("contact.html", msg_sent=False, form=contact_form)
    return render_template("contact.html", msg_sent=False, form=contact_form)

def send_mail(fromaddr, toaddr,name, user_email,  subject, message):
    msg = MIMEMultipart('related')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = f"From: {user_email} <br> Sender's name: {name} <br> Message: {message}"
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)
    part_text = MIMEText(lxml.html.fromstring(body).text_content().encode('utf-8'), 'plain', _charset='utf-8')
    part_html = MIMEText(body.encode('utf-8'), 'html', _charset='utf-8')
    msg_alternative.attach(part_text)
    msg_alternative.attach(part_html)
    server = smtplib.SMTP("smtp.gmail.com",port= 587, timeout=120)
    server.starttls()
    server.login(user=MY_EMAIL, password=APP_PASSWORD)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()

if __name__=='__main__':
    app.run(debug=True) ##Replaced app.run(debug=False) Note:  app.run() or app.run(debug=False) helps avoid arbitrary code execution
