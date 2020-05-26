from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from memorylane import db
from memorylane.models import Posts
from memorylane.posts.forms import PostForm, PostEditForm
from flask_login import current_user, login_required

posts = Blueprint('posts', __name__)


@posts.route('/home', methods=['GET'])
@login_required
def home():
    form = PostForm()
    page = int(request.args.get('page', 1))
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5, error_out=False)

    return render_template('home.html', posts=posts, user=current_user, form=form)


@posts.route('/addpost', methods=["GET", "POST"])
@login_required
def addpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data,
                     user_id=current_user.id, date_posted=datetime.now())

        db.session.add(post)
        db.session.commit()

        flash('Post added!', 'success')
        return redirect(url_for('posts.home'))
    return render_template('home.html', form=form)


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Posts.query.get(int(post_id))
    date_posted = post.date_posted.strftime('%B %d, %Y')

    return render_template('post_edit.html', post=post, user=current_user, date_posted=date_posted)


@posts.route('/post/<int:post_id>/edit', methods=["GET", "POST"])
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
        return redirect(url_for('posts.home', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_edit.html', form=form, post=post)


@posts.route('/postdelete/<int:post_id>', methods=['POST'])
def post_delete(post_id):
    post = Posts.query.get(post_id)

    if post.author.id == current_user.id:
        db.session.delete(post)
        db.session.commit()

        flash("Your post was deleted!", "success")
        return redirect(url_for('posts.home'))

    else:
        return redirect(url_for('main.index'))
