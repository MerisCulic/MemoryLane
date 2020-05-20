import os
import uuid
import hashlib
import secrets
from PIL import Image
from datetime import datetime
from flask import render_template, request, redirect, url_for, make_response, flash, abort
from memorylane import app, db
from memorylane.models import User, Messages, Posts
from memorylane.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm, PostEditForm


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()
    if user:
        return redirect(url_for('profile', user=user))
    else:
        return render_template('index.html')


@app.route('/home', methods=['GET'])
def home():
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()
    form = PostForm()

    page = int(request.args.get('page', 1))
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5, error_out=False)

    return render_template('home.html', posts=posts, user=user, form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        name = form.firstname.data + " " + form.surname.data
        hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
        user = User(name=name, firstname=form.firstname.data, surname=form.surname.data,
                    email=form.email.data, password=hashed_password)

        session_token = str(uuid.uuid4())
        user.session_token = session_token

        db.session.add(user)
        db.session.commit()

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
        user = User.query.filter_by(email=form.email.data).first()
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
            db.session.add(user)
            db.session.commit()

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
        user = User.query.filter_by(session_token=session_token).first()
        image_file = url_for('static', filename='img/profile_pics/' + user.image_file)
        page = int(request.args.get('page', 1))
        posts = Posts.query \
            .filter_by(author=user) \
            .order_by(Posts.date_posted.desc()) \
            .paginate(page=page, per_page=5, error_out=False)

        return render_template("profile.html", user=user, image_file=image_file, posts=posts)
    else:
        flash('You need to be logged in to view profile pages!', 'danger')
        return render_template('index.html')


@app.route('/profile/<user_id>', methods=["GET"])
def user_profile(user_id):
    session_token = request.cookies.get("session_token")
    if session_token:
        user = User.query.get(int(user_id))
        page = int(request.args.get('page', 1))
        posts = Posts.query\
            .filter_by(author=user)\
            .order_by(Posts.date_posted.desc())\
            .paginate(page=page, per_page=5, error_out=False)

        image_file = url_for('static', filename='img/profile_pics/' + user.image_file)
        return render_template("profile.html", posts=posts, user=user, image_file=image_file)
    else:
        flash('You need to be logged in to view profile pages!', 'danger')
        return render_template('index.html')


@app.route('/update_profile', methods=["GET", "POST"])
def update_profile():
    session_token = request.cookies.get("session_token")
    if session_token:
        user = User.query.filter_by(session_token=session_token).first()
        form = UpdateProfileForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                user.image_file = picture_file

            user.firstname = form.firstname.data
            user.surname = form.surname.data
            user.email = form.email.data
            user.name = form.firstname.data + " " + form.surname.data

            db.session.commit()
            flash('Your profile was successfully updated!', 'success')
            return redirect(url_for('profile'))

        elif request.method == "GET":
            form.firstname.data = user.firstname
            form.surname.data = user.surname
            form.email.data = user.email

        return render_template("profile_edit.html", user=user, form=form)
    else:
        flash('You need to be logged in to edit your profile page!', 'danger')
        return render_template('index.html')


@app.route("/new_message", methods=["GET", "POST"])
def new_message():
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()

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

        db.session.add(message)
        db.session.commit()

        flash('Your message was sent!', 'info')
        return redirect(url_for('profile'))


@app.route('/sent', methods=["GET"])
def sent_messages():
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()

    sent_messages = Messages.query.filter_by(sender_email=user.email).order_by(Messages.date_posted.desc()).all()

    if not sent_messages:
        message = "You have no sent messages!"
    else:
        message = "These are your sent messages"

    return render_template('messages_sent.html', sent_messages=sent_messages, user=user, message=message)


@app.route('/inbox', methods=["GET"])
def recieved_messages():
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()
    reciever = user.email

    recieved_messages = Messages.query.filter_by(reciever=reciever).order_by(Messages.date_posted.desc()).all()

    if not recieved_messages:
        message = "Your inbox is empty!"
    else:
        message = "Inbox"

    return render_template('messages_recieved.html', recieved_messages=recieved_messages, user=user, message=message)


@app.route("/<string:status>/<msg_id>", methods=["GET"])
def message_details(status, msg_id):

    msg = Messages.query.get(int(msg_id))

    return render_template('message_details.html', msg=msg, msg_id=msg_id, status=status)


@app.route("/<int:msg_id>/delete", methods=['POST'])
def message_delete(msg_id):
    session_token = request.cookies.get("session_token")
    if session_token:

        msg = Messages.query.get(msg_id)
        db.session.delete(msg)
        db.session.commit()

        flash("Message was deleted!", "success")
        return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/addpost', methods=["GET", "POST"])
def addpost():
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()
    if user:
        form = PostForm()
        if form.validate_on_submit():
            post = Posts(title=form.title.data, content=form.content.data, user_id=user.id, date_posted=datetime.now())

            db.session.add(post)
            db.session.commit()

            flash('Post added!', 'success')
            return redirect(url_for('home'))
        return render_template('home.html', form=form)
    else:
        return render_template('index.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()

    post = Posts.query.get(int(post_id))

    date_posted = post.date_posted.strftime('%B %d, %Y')

    return render_template('post_edit.html', post=post, user=user, date_posted=date_posted)


@app.route('/post/<int:post_id>/edit', methods=["GET", "POST"])
def post_edit(post_id):
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()
    if not user:
        return redirect(url_for('index'))

    post = Posts.query.get(int(post_id))

    if post.author.name != user.name:
        abort(403)
    form = PostEditForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()

        flash('Your post has been updated!', 'success')
        return redirect(url_for('home', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_edit.html', form=form, post=post)


@app.route('/postdelete/<int:post_id>', methods=['POST'])
def post_delete(post_id):
    session_token = request.cookies.get("session_token")
    user = User.query.filter_by(session_token=session_token).first()

    post = Posts.query.get(post_id)

    if post.author.name == user.name:
        db.session.delete(post)
        db.session.commit()

        flash("Your post was deleted!", "success")
        return redirect(url_for('home'))

    else:
        return redirect(url_for('index'))