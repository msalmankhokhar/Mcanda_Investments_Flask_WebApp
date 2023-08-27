from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from threading import Thread
from time import sleep
from os.path import join
from werkzeug.utils import secure_filename
from markupsafe import Markup

app = Flask(__name__)

app.secret_key = 'salman'

# mail settings
app.config['MAIL_SERVER']='mail.mcandainvest.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'info@mcandainvest.com'
app.config['MAIL_PASSWORD'] = 'mcandain123!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['EMAIL_HTML_FILES_FOLDER'] = 'EMAIL_UPLOADS'

mail = Mail(app)

def send_mail(emailobj):
    with app.app_context():
        try:
            mail.send(emailobj)
            return True
        except Exception as e:
            print(f'Error is\n{e}')
            return False

def send_subscription_mail(content, recipient_email):
    mailobj =  Message(
            subject='Newsletter Email',
            html=content,
            recipients=[recipient_email],
            sender=('Mcanda Investments', 'info@mcandainvest.com')
            )
    send_mail(mailobj)
    return True

# setting up SQLite Database
app.secret_key = "salman"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db = SQLAlchemy(app)

# Creating database schema
class subscribers(db.Model):
    s = db.Column(db.Integer, nullable=True, unique=False)
    email = db.Column(db.String(100), primary_key=True, nullable=False)
class users(db.Model):
    username = db.Column(db.String(25), primary_key=True, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False, unique=False)

# creating database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html', headertitle='Home', currentNavLink='#navlink-home')

@app.route('/send', methods=['GET', 'POST'])
def send():
    email_msg = Message(
            subject='Thanks for contacting Mcanda Investments',
            html='This is a test message from <strong>Mcanda Investments</strong>',
            recipients=['kjokhars@gmail.com', 'mxolisimasuku5@gmail.com'],
            # recipients=['kjokhars@gmail.com'],
            sender=('Mcanda Investments', 'info@mcandainvest.com')
            # sender=('Mcanda Investments', 'alphadevsol@outlook.com')
            )
    mail.send(email_msg)
    return 'check your inbox'

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html', headertitle='Contact', currentNavLink='#navlink-contact')
    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        user_msg = request.form.get('msg')

        owner_email_content = Markup(f"A user has dropped a messege on your website's contact page.<br><br><h3>User data:</h3><br><strong>Name: </strong><br> {name}<br><strong>Email: </strong><br> {email}<br><br><strong>User Message: </strong><br> {user_msg}<br>")
        user_email_content = Markup('We have received your message. Our team will reach you back as soon as possible.<br>Have a good day!')
        
        email_for_user = Message(
            subject='Thanks for contacting Mcanda Investments',
            html=render_template('email/contact_form_user.html', name=name, content=user_email_content),
            recipients=[email],
            sender=('Mcanda Investments', 'info@mcandainvest.com')
            )
        
        email_for_owner = Message(
            "New Notification",
            sender=("Mcanda Investments", 'info@mcandainvest.com'),
            recipients=["kjokhars@gmail.com", "mxolisimasuku5@gmail.com"],
            # recipients=["kjokhars@gmail.com"],
            html=render_template('email/contact_form_owner.html', content=owner_email_content)
            )
        # email_thread_owner = Thread(target=send_mail, args=[email_for_owner])
        # email_thread_user = Thread(target=send_mail, args=[email_for_user])    
        # email_thread_owner.start()
        # email_thread_user.start()

        ownerEmailStatus = send_mail(email_for_user)
        userEmailStatus = send_mail(email_for_owner)

        # ownerEmailStatus = True
        # userEmailStatus =  False
        if userEmailStatus == True and ownerEmailStatus == True:
            responseMsg = 'Message sent successfully. Keep checking your email inbox. Our team will reply you within 2 - 3 minutes'
            return {
                'isEmailSent' : True,
                'msg' : responseMsg
            }
        else:
            responseMsg = 'Sorry, the email was not sent due to a technical fault on the server'
            return {
                'isEmailSent' : False,
                'msg' : responseMsg
            }


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        subsList = subscribers.query.all()
        s = len(subsList) + 1;
        requestJSON = request.get_json()
        email = requestJSON['email']
        selectedSubscriber = subscribers.query.filter_by(email=email).first()
        new_subscriber = subscribers(email=email, s=s)
        db.session.add(new_subscriber)
        try:
            response = {
                'error' : {
                    'state': False,
                    'msg' : f'''Thanks for subscribing to our Newsletter. Your email <span style="color: black;">{email}</span> has been successfully registered in our mailing list. Have a Good day!'''
                    }
            }
            db.session.commit()
        except Exception as error:
            if selectedSubscriber:
                print('went in e if')
                response['error'] = {
                    'state' : True,
                    'value' : str(error),
                    'msg'   : f'Your email <span style="color: black;">{email}</span> is already registered in our mailing list'
                }
            else:
                response['error'] = {
                    'state' : True,
                    'value' : str(error),
                    'msg'   : f'Sorry, an error occured due to duplicate subscriber ID'
                }
        finally:
            sleep(5)
            return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_user = users.query.filter_by(username=username).first()
        if selected_user != None:
            if password == selected_user.password:
                session['user'] = selected_user.username
                return redirect(url_for('admin'))
            else:
                return 'Wrong password Try Again.<br><hr><a href="/login">Click Here to go to login page</a>'
        else:
            return f'Sorry, there is no account with this username <strong>{username}</strong>'
        
@app.route('/logout/<string:givenusername>', methods=['GET', 'POST'])
def logout(givenusername):
    if request.method == 'GET':
        selected_user = users.query.filter_by(username=givenusername).first()
        if session['user'] == selected_user.username:
            session.pop('user')
            return redirect(url_for('admin'))
        else:
            return 'Sorry, An error occured in the Log Out Function'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        if 'user' in session:
            userLoggedIn = users.query.filter_by(username=session['user']).first()
            userlist = subscribers.query.all()
            return render_template('admin.html', userlist=userlist, userLoggedIn=userLoggedIn)
        else:
            return redirect(url_for('login'))

@app.route('/admin/delete-subscriber/<string:userEmail>', methods=['GET', 'POST'])
def del_subs(userEmail):
    selected_user = subscribers.query.filter_by(email=userEmail).first()
    db.session.delete(selected_user)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/send-newsletter-mail/<string:userEmail>', methods=['GET', 'POST'])
def send_newsletter_mail_route(userEmail):
    if request.method == 'POST':
        print(f'Content tye is {request.content_type}')
        if request.content_type == 'application/json':
            requestJSON = request.get_json()
            emailContent = requestJSON['emailcontent']
            sent_status = send_subscription_mail(content=emailContent, recipient_email=userEmail)
            response = { 'sent' : sent_status }
            return response
        else:
            print('went in elif')
            htmlFile = request.files['emailcontent']
            emailContent = htmlFile.read()
            sent_status = send_subscription_mail(content=emailContent, recipient_email=userEmail)
            response = { 'sent' : sent_status }
            return response
        
@app.route('/faq')
def faq():
    return render_template('faq.html', headertitle='FAQ', currentNavLink='#navlink-faq, #dropdown-about')

@app.route('/about')
def about():
    return render_template('about.html', headertitle='About', currentNavLink='#navlink-about, #dropdown-about')

@app.route('/mxolisi')
def mxolisi():
    return render_template('mxolisi.html', headertitle='Mxolisi')

@app.route('/news')
def news():
    return render_template('news.html', headertitle='News', currentNavLink='#navlink-news')

@app.route('/news-details-wed')
def news_details_wed():
    return render_template('news-details-wed.html', headertitle='News Details Wed')

@app.route('/news-details')
def news_details():
    return render_template('news-details.html', headertitle='News Details')

@app.route('/our_services')
def our_services():
    return render_template('our-services.html', headertitle='Our Services', currentNavLink='#navlink-services')

@app.route('/sibonile')
def sibonile():
    return render_template('sibonile.html', headertitle='Sibonile')

@app.route('/team')
def team():
    return render_template('team.html', headertitle='Our Team', currentNavLink='#navlink-team, #dropdown-about')

@app.route('/team_details')
def team_details():
    return render_template('team-details.html', headertitle='Team Details')

@app.route('/video-graphy')
def video_graphy():
    return render_template('video-graphy.html', headertitle='Video Graphy')

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        debug = True 
    )