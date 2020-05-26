import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash
from memorylane import db
from memorylane.models import User, Posts
from memorylane.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm
from memorylane.users.utils import save_picture, send_reset_email
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users', __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.profile'))
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
        return redirect(url_for('users.profile', user=current_user))
    return render_template("registration.html", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("Sorry, you weren't found in the database. Please register!", "danger")
            return redirect(url_for('users.register'))

        hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
        if hashed_password != user.password:
            flash("Wrong password! Please try again!", "danger")
            return redirect(request.url)

        elif hashed_password == user.password:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You were successfully logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('users.profile', user=user))
    return render_template("login_page.html", form=form)


@users.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    flash('You were successfully logged out!', 'success')
    return redirect(url_for('main.index'))


@users.route('/profile', methods=["GET"])
@login_required
def profile():
    image_file = url_for('static', filename='img/profile_pics/' + current_user.image_file)
    page = int(request.args.get('page', 1))
    posts = Posts.query \
        .filter_by(author=current_user) \
        .order_by(Posts.date_posted.desc()) \
        .paginate(page=page, per_page=5, error_out=False)

    return render_template("profile.html", user=current_user, image_file=image_file, posts=posts)


@users.route('/profile/<user_id>', methods=["GET"])
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


@users.route('/update_profile', methods=["GET", "POST"])
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
        return redirect(url_for('users.profile'))

    elif request.method == "GET":
        form.firstname.data = current_user.firstname
        form.surname.data = current_user.surname
        form.email.data = current_user.email

    return render_template("profile_edit.html", user=current_user, form=form)


@users.route('/users')
@login_required
def reg_users():
    reg_users = User.query.all()
    return render_template('users.html', users=reg_users)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('posts.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('A password-reset email has been set to your inbox!', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('posts.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token!', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = hashlib.sha256(form.password.data.encode()).hexdigest()
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)
