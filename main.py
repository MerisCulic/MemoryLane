import os
import uuid
import hashlib
import secrets
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from models import User, Messages, db, Posts
from forms import RegistrationForm, LoginForm, UpdateProfileForm
from datetime import datetime


app = Flask(__name__)
db.create_all()
app.config['SECRET_KEY'] = b'\xbf,\x92\xda\x11\x844\xae\xf4i\xd36\x01\xef\xb4'


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        return redirect(url_for('profile', user=user))
    else:
        return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

            name = form.firstname.data + " " + form.surname.data
            hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
            user = User(name=name, firstname=form.firstname.data, surname=form.surname.data,
                        email=form.email.data, password=hashed_password, image_file='default_avatar.jpg')

            session_token = str(uuid.uuid4())
            user.session_token = session_token

            db.add(user)
            db.commit()

            response = make_response(redirect(url_for('profile', user=user)))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
            flash('Welcome to Memory Lane {}! '
                  'Your account has been successfully created!'.format(form.firstname.data), 'success')
            return response
    return render_template("registration.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.query(User).filter_by(email=form.email.data).first()
        if not user:
            flash("Sorry, you weren't found in the database. Please register!", "danger")
            return redirect(url_for('register'))

        hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()

        if hashed_password != user.password:
            flash("Wrong password! Please try again!", "danger")
            return redirect(request.url)

        elif hashed_password == user.password:
            session_token = str(uuid.uuid4())

            user.session_token = session_token
            db.add(user)
            db.commit()

            response = make_response(redirect(url_for('profile', user=user)))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
            flash('You were successfully logged in!', 'success')
            return response

    return render_template("login_page.html", form=form)


@app.route('/logout', methods=["GET"])
def logout():

    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", expires=0)
    flash('You were successfully logged out!', 'success')
    return response


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/profile_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn


@app.route('/profile', methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        image_file = url_for('static', filename='img/profile_pics/' + user.image_file)
        return render_template("profile.html", user=user, image_file=image_file)
    else:
        flash('You need to be logged in to view profile pages!', 'danger')
        return render_template('index.html')


@app.route('/update_profile', methods=["GET", "POST"])
def update_profile():
    session_token = request.cookies.get("session_token")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        form = UpdateProfileForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                user.image_file = picture_file

            user.firstname = form.firstname.data
            user.surname = form.surname.data
            user.email = form.email.data
            user.name = form.firstname.data + " " + form.surname.data

            db.commit()
            flash('Your profile was successfully updated!', 'success')
            return redirect(url_for('profile'))

        elif request.method == "GET":
            form.firstname.data = user.firstname
            form.surname.data = user.surname
            form.email.data = user.email

        return render_template("update_profile.html", user=user, form=form)
    else:
        flash('You need to be logged in to edit your profile page!', 'danger')
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
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    posts = db.query(Posts).order_by(Posts.date_posted.desc()).all()

    return render_template('home.html', posts=posts, user=user)


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
        return redirect(url_for('home'))

    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True) #TODO: Disable debug before deployment
