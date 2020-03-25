from flask import Flask, render_template, request, redirect, url_for, make_response, flash
import uuid
import hashlib
from models import User, Messages, db, Posts
from datetime import datetime


app = Flask(__name__)
db.create_all()
app.secret_key = b'\xbf,\x92\xda\x11\x844\xae\xf4i\xd36\x01\xef\xa4\xde\x8f\xc4\xbb\x0b\x99(\xad\xb4'


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        return render_template('profile.html', user=user)
    else:
        return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("registration.html")

    if request.method == "POST":
        first_name = request.form.get("user-firstname").strip()
        surname = request.form.get("user-surname").strip()
        email = request.form.get("user-email").strip()
        password = request.form.get("user-password").strip()
        confirm_password = request.form.get("confirm-user-password").strip()
        name = first_name + " " + surname

        if not len(password) >= 5:
            flash("Password length must be at least 5 characters", "warning")
            return redirect(request.url)

        if confirm_password != password:
            flash("Your passwords don't match!", "warning")
            return redirect(request.url)

        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            user = User(name=name, email=email, password=hashed_password)

            session_token = str(uuid.uuid4())
            user.session_token = session_token

            db.add(user)
            db.commit()

            response = make_response(redirect(url_for('profile', user=user)))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
            flash('Account successfully created!', 'success')

            return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html")

    if request.method == "POST":
        email = request.form.get("user-email")
        password = request.form.get("user-password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(email=email).first()

        if not user:
            flash("Sorry, you weren't found in the database. Please register!", "warning")
            return redirect(url_for('register'))

        if hashed_password != user.password:
            flash("Wrong password! Please try again!", "warning")
            return redirect(request.url)

        elif hashed_password == user.password:
            session_token = str(uuid.uuid4())

            user.session_token = session_token
            db.add(user)
            db.commit()

            response = make_response(redirect(url_for('profile', user=user)))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
            flash('You were successfully logged in', 'success')

            return response


@app.route('/logout', methods=["GET"])
def logout():

    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", expires=0)
    flash('You were successfully logged out!', 'success')
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

        message = Messages(reciever=reciever, sender_email=user.email, sender_name=user.name, title=title,
                           message_text=message_text, date_posted=datetime.now())

        db.add(message)
        db.commit()

        flash('Your message was sent!', 'info')
        return redirect(url_for('profile'))


@app.route('/sent', methods=["GET"])
def sent_messages():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    sent_messages = db.query(Messages).filter_by(sender_email=user.email).order_by(Messages.date_posted.desc()).all()

    if not sent_messages:
        message = "You have no sent messages!"
    else:
        message = "These are your sent messages"

    return render_template('messages_sent.html', sent_messages=sent_messages, user=user, message=message)


@app.route('/inbox', methods=["GET"])
def recieved_messages():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    reciever = user.email

    recieved_messages = db.query(Messages).filter_by(reciever=reciever).order_by(Messages.date_posted.desc()).all()

    if not recieved_messages:
        message = "Your inbox is empty!"
    else:
        message = "Inbox"

    return render_template('messages_recieved.html', recieved_messages=recieved_messages, user=user, message=message)


@app.route("/<string:status>/<msg_id>", methods=["GET"])
def message_details(status, msg_id):

    msg = db.query(Messages).get(int(msg_id))

    return render_template('message_details.html', msg=msg, msg_id=msg_id, status=status)


@app.route("/<int:msg_id>/delete", methods=['POST'])
def message_delete(msg_id):
    session_token = request.cookies.get("session_token")
    if session_token:

        msg = db.query(Messages).get(msg_id)
        db.delete(msg)
        db.commit()

        flash("Message was deleted!", "success")
        return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


@app.route('/users')
def users():
    users = db.query(User).all()
    return render_template('users.html', users=users)


@app.route("/users/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))

    return render_template("user_details.html", user=user)


@app.route('/addpost', methods=["GET", "POST"])
def addpost():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template('add_post.html')
        else:
            return render_template('index.html')

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")
        author = user.name

        post = Posts(title=title, author=author, content=content, date_posted=datetime.now())

        db.add(post)
        db.commit()

        flash('Post added!', 'info')
        return redirect(url_for('home'))


@app.route('/home', methods=['GET'])
def home():
    posts = db.query(Posts).order_by(Posts.date_posted.desc()).all()

    return render_template('home.html', posts=posts)


@app.route('/post/<int:post_id>')
def post(post_id):
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    post = db.query(Posts).get(int(post_id))

    date_posted = post.date_posted.strftime('%B %d, %Y')

    return render_template('post.html', post=post, user=user, date_posted=date_posted)


@app.route('/postdelete/<int:post_id>', methods=['POST'])
def post_delete(post_id):
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    post = db.query(Posts).get(post_id)

    if post.author == user.name:
        db.delete(post)
        db.commit()

        flash("Your post was deleted!", "success")
        return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
