import os
import hashlib
import secrets
from PIL import Image
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, abort
from memorylane import app, db, mail
from memorylane.models import User, Messages, Posts
from memorylane.forms import (RegistrationForm, LoginForm, UpdateProfileForm, PostForm,
                              PostEditForm, RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('profile', user=current_user))
    else:
        return render_template('index.html')


@app.route('/home', methods=['GET'])
@login_required
def home():
    form = PostForm()
    page = int(request.args.get('page', 1))
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5, error_out=False)

    return render_template('home.html', posts=posts, user=current_user, form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = RegistrationForm()
    if form.validate_on_submit():

        name = form.firstname.data + " " + form.surname.data
        hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
        user = User(name=name, firstname=form.firstname.data, surname=form.surname.data,
                    email=form.email.data, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash('Welcome to Memory Lane {}! '
              'Your account has been successfully created!'.format(form.firstname.data), 'success')
        return redirect(url_for('profile', user=current_user))
    return render_template("registration.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

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
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You were successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('profile', user=user))
    return render_template("login_page.html", form=form)


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    flash('You were successfully logged out!', 'success')
    return redirect(url_for('index'))


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
@login_required
def profile():
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    page = int(request.args.get('page', 1))
    posts = Posts.query \
        .filter_by(author=current_user) \
        .order_by(Posts.date_posted.desc()) \
        .paginate(page=page, per_page=5, error_out=False)

    return render_template("profile.html", user=current_user, image_file=image_file, posts=posts)



@app.route('/profile/<user_id>', methods=["GET"])
@login_required
def user_profile(user_id):
    user = User.query.get(int(user_id))
    page = int(request.args.get('page', 1))
    posts = Posts.query\
        .filter_by(author=user)\
        .order_by(Posts.date_posted.desc())\
        .paginate(page=page, per_page=5, error_out=False)

    image_file = url_for('static', filename='img/profile_pics/' + user.image_file)
    return render_template("profile.html", posts=posts, user=user, image_file=image_file)


@app.route('/update_profile', methods=["GET", "POST"])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.firstname = form.firstname.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data
        current_user.name = form.firstname.data + " " + form.surname.data

        db.session.commit()
        flash('Your profile was successfully updated!', 'success')
        return redirect(url_for('profile'))

    elif request.method == "GET":
        form.firstname.data = current_user.firstname
        form.surname.data = current_user.surname
        form.email.data = current_user.email

    return render_template("profile_edit.html", user=current_user, form=form)


@app.route("/new_message", methods=["GET", "POST"])
@login_required
def new_message():
    if request.method == "GET":
        return render_template("message_new.html")

    if request.method == "POST":
        reciever = request.form.get("reciever")
        title = request.form.get("title")
        message_text = request.form.get("message_text")

        message = Messages(reciever=reciever, sender_email=current_user.email, sender_name=current_user.name, title=title,
                           message_text=message_text, date_posted=datetime.now())

        db.session.add(message)
        db.session.commit()

        flash('Your message was sent!', 'info')
        return redirect(url_for('profile'))


@app.route('/sent', methods=["GET"])
@login_required
def sent_messages():
    sent_messages = Messages.query.filter_by(sender_email=current_user.email).order_by(Messages.date_posted.desc()).all()

    if not sent_messages:
        message = "You have no sent messages!"
    else:
        message = "These are your sent messages"

    return render_template('messages_sent.html', sent_messages=sent_messages, user=current_user, message=message)


@app.route('/inbox', methods=["GET"])
@login_required
def recieved_messages():
    recieved_messages = Messages.query.filter_by(reciever=current_user.email).order_by(Messages.date_posted.desc()).all()

    if not recieved_messages:
        message = "Your inbox is empty!"
    else:
        message = "Inbox"

    return render_template('messages_recieved.html', recieved_messages=recieved_messages, user=current_user, message=message)


@app.route("/<string:status>/<msg_id>", methods=["GET"])
@login_required
def message_details(status, msg_id):
    msg = Messages.query.get(int(msg_id))

    return render_template('message_details.html', msg=msg, msg_id=msg_id, status=status)


@app.route("/<int:msg_id>/delete", methods=['POST'])
def message_delete(msg_id):
    msg = Messages.query.get(msg_id)
    db.session.delete(msg)
    db.session.commit()

    flash("Message was deleted!", "success")
    return redirect(url_for('index'))


@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/addpost', methods=["GET", "POST"])
@login_required
def addpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, user_id=current_user.id, date_posted=datetime.now())

        db.session.add(post)
        db.session.commit()

        flash('Post added!', 'success')
        return redirect(url_for('home'))
    return render_template('home.html', form=form)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Posts.query.get(int(post_id))
    date_posted = post.date_posted.strftime('%B %d, %Y')

    return render_template('post_edit.html', post=post, user=current_user, date_posted=date_posted)


@app.route('/post/<int:post_id>/edit', methods=["GET", "POST"])
@login_required
def post_edit(post_id):
    post = Posts.query.get(int(post_id))

    if post.author.name != current_user.name:
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
    post = Posts.query.get(post_id)

    if post.author.id == current_user.id:
        db.session.delete(post)
        db.session.commit()

        flash("Your post was deleted!", "success")
        return redirect(url_for('home'))

    else:
        return redirect(url_for('index'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])

    msg.body = f'''To reset your password visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('A password-reset email has been set to your inbox!', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token!', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)