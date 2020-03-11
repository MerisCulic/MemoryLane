from flask import Flask, render_template, request, redirect, url_for, make_response
import uuid
import hashlib
from models import User, Messages, db
from datetime import datetime


app = Flask(__name__)
db.create_all()


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        return render_template('profile.html', user=user)
    else:
        return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
            return render_template("login_page.html")

    if request.method == "POST":
        name = request.form.get("user-name")
        email = request.form.get("user-email")
        password = request.form.get("user-password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(email=email).first()

        if not user:
            user = User(name=name, email=email, password=hashed_password)

            db.add(user)
            db.commit()

        if hashed_password != user.password:
            return "WRONG PASSWORD! Please go back and try again!"


        elif hashed_password == user.password:
            session_token = str(uuid.uuid4())

            user.session_token = session_token
            db.add(user)
            db.commit()

            response = make_response(redirect(url_for('profile', user=user)))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

            return response


@app.route('/profile', methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        return render_template("profile.html", user=user)
    else:
        return render_template('index.html')


@app.route("/new_message", methods=["GET", "POST"])
def new_message():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("message_new.html")
        else:
            return render_template('index.html')

    if request.method == "POST":

        reciever = request.form.get("reciever")
        title = request.form.get("title")
        message_text = request.form.get("message_text")
        sender = user.email

        message = Messages(reciever=reciever, sender=sender, title=title, message_text=message_text, date_posted=datetime.now())

        db.session.add(message)
        db.session.commit()

        return redirect(url_for('profile'))


@app.route('/sent', methods=["GET"])
def sent_messages():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    sender = user.email

    sent_messages = db.query(Messages).filter_by(sender=sender).order_by(Messages.date_posted.desc()).all()

    if not sent_messages:
        message = "You have no sent messages!"
    else:
        message = "These are your sent messages"

    return render_template('messages_sent.html', sent_messages=sent_messages, user=user, message=message)


@app.route("/sent/<sent_id>", methods=["GET"])
def message_details(sent_id):

    sent = db.query(Messages).get(int(sent_id))

    return render_template('message_details.html', sent=sent, sent_id=sent_id)


@app.route("/sent/<int:sent_id>/delete", methods=['POST'])
def message_delete(sent_id):
    session_token = request.cookies.get("session_token")
    if session_token:

        sent = db.query(Messages).get(sent_id)
        db.session.delete(sent)
        db.session.commit()

        #flash('Message was deleted!', 'success')
        return redirect(url_for('index'))

    else:
        return "WTF man?!"


if __name__ == '__main__':
    app.run(debug=True)
