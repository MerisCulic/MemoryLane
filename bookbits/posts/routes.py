from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from bookbits import db
from bookbits.models import Posts, Comments
from bookbits.posts.forms import PostForm, PostEditForm, CommentForm, CommentEditForm
from flask_login import current_user, login_required

posts = Blueprint('posts', __name__)


@posts.route('/home', methods=['GET'])
def home():
    form = PostForm()
    comment_form = CommentForm()
    page = int(request.args.get('page', 1))
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5, error_out=False)
    comments = Comments.query.order_by(Comments.date_posted.asc())

    return render_template('home.html', posts=posts, comments=comments,
                           user=current_user, form=form, c_form=comment_form)


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
    comments = Comments.query.filter_by(com_post_id=post_id).all()

    if post.author.id == current_user.id:
        db.session.delete(post)
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()

        flash("Your post was deleted!", "success")
        return redirect(url_for('posts.home'))

    else:
        return redirect(url_for('main.index'))


@posts.route('/comment/<int:post_id>', methods=["GET", "POST"])
@login_required
def add_comment(post_id):
    commented_post = Posts.query.get(int(post_id))
    c_form = CommentForm()

    if c_form.validate_on_submit():
        comment = Comments(
            content=c_form.content.data,
            user_id=current_user.id,
            date_posted=datetime.now(),
            com_post_id=commented_post.id)

        db.session.add(comment)
        db.session.commit()

        flash('Comment added!', 'success')
        return redirect(url_for('posts.home'))
    return render_template('home.html', form=PostForm, c_form=c_form)


@posts.route('/comment/<int:comment_id>/edit', methods=["GET", "POST"])
@login_required
def comment_edit(comment_id):
    comment = Comments.query.get(int(comment_id))

    if comment.com_author != current_user:
        abort(403)
    form = CommentEditForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()

        flash('Your comment has been updated!', 'success')
        return redirect(url_for('posts.home'))

    elif request.method == 'GET':
        form.content.data = comment.content
    return render_template('comment_edit.html', form=form, comment=comment)


@posts.route('/comment/<int:comment_id>/delete', methods=['POST'])
def comment_delete(comment_id):
    comment = Comments.query.get(int(comment_id))

    if comment.com_author == current_user:
        db.session.delete(comment)
        db.session.commit()

        flash("Your comment has been deleted!", "success")
        return redirect(url_for('posts.home'))
    else:
        return redirect(url_for('main.index'))
