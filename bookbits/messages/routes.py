from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from bookbits import db
from bookbits.models import Messages
from flask_login import current_user, login_required

messages = Blueprint('messages', __name__)


@messages.route("/new_message", methods=["GET", "POST"])
@login_required
def new_message():
    if request.method == "GET":
        return render_template("message_new.html")

    if request.method == "POST":
        reciever = request.form.get("reciever")
        title = request.form.get("title")
        message_text = request.form.get("message_text")

        message = Messages(reciever=reciever, sender_email=current_user.email, sender_name=current_user.name,
                           title=title, message_text=message_text, date_posted=datetime.now())

        db.session.add(message)
        db.session.commit()

        flash('Your message was sent!', 'info')
        return redirect(url_for('users.profile'))


@messages.route('/sent', methods=["GET"])
@login_required
def sent_messages():
    sent_messages = Messages.query.filter_by(sender_email=current_user.email)\
        .order_by(Messages.date_posted.desc()).all()

    if not sent_messages:
        message = "You have no sent messages!"
    else:
        message = "These are your sent messages"

    return render_template('messages_sent.html', sent_messages=sent_messages, user=current_user, message=message)


@messages.route('/inbox', methods=["GET"])
@login_required
def recieved_messages():
    recieved_messages = Messages.query.filter_by(reciever=current_user.email)\
        .order_by(Messages.date_posted.desc()).all()

    if not recieved_messages:
        message = "Your inbox is empty!"
    else:
        message = "Inbox"

    return render_template('messages_recieved.html',
                           recieved_messages=recieved_messages, user=current_user, message=message)


@messages.route("/<string:status>/<msg_id>", methods=["GET"])
@login_required
def message_details(status, msg_id):
    msg = Messages.query.get(int(msg_id))

    return render_template('message_details.html', msg=msg, msg_id=msg_id, status=status)


@messages.route("/<int:msg_id>/delete", methods=['POST'])
def message_delete(msg_id):
    msg = Messages.query.get(msg_id)
    db.session.delete(msg)
    db.session.commit()

    flash("Message was deleted!", "success")
    return redirect(url_for('main.index'))