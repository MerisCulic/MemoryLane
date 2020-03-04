from flask import Flask, render_template, request, redirect, url_for, make_response
import uuid
import hashlib
from models import User, db
import json


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

            response = make_response(redirect(url_for('profile')))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

            return response


@app.route('/profile", methods=["GET"]')
def profile():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        return render_template("profile.html", user=user)
    else:
        return render_template('index.html')

@app.route("/new_message", methods=["GET", "POST"])
def new_message():
    if request.method == "GET":
            return render_template("new_message.html")

    if request.method == "POST":
        session_token = request.cookies.get("session_token")

        if session_token:
            user = db.query(User).filter_by(session_token=session_token).first()
        else:
            return render_template('index.html')

        reciever = request.form.get("reciever")
        title = request.form.get("reciever")
        message = request.form.get("message")
        sender = {{ user.email }}

        message.sender = sender
        message.reciever = reciever
        message.title = title
        message.message = message

        db.add(message)
        db.commit()

        #return redirect(url_for('profile'))





if __name__ == '__main__':
    app.run(debug=True)
