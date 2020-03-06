from flask import Flask, render_template, request, redirect, url_for, make_response
import uuid
import hashlib
from models import User, Sent_messages, db
import smtplib



app = Flask(__name__)
db.create_all()

def find_user():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    return user


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

        message = Sent_messages(reciever=reciever, sender=sender, title=title, message_text=message_text)

        db.add(message)
        db.commit()

        return redirect(url_for('profile'))

@app.route('/sent', methods=["GET"])
def sent_messages():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    sent_messages = db.query(Sent_messages).all()


    if not sent_messages:
        message = "You have no sent messages!"
    else:
        message = "These are your sent messages"

    return render_template('messages_sent.html', sent_messages=sent_messages, user=user, message=message)

@app.route("/sent/<sent_id>", methods=["GET"])
def messsage_details(sent_id):

    sent = db.query(Sent_messages).get(int(sent_id))

    return render_template('message_details.html', sent=sent)




if __name__ == '__main__':
    app.run(debug=True)
