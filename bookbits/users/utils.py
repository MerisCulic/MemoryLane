import os
import secrets
from PIL import Image
from flask import current_app, url_for, request
from bookbits import mail
from flask_mail import Message
from bookbits.config import Config
import boto3
import botocore


# Connect to AWS S3 file storage
s3 = boto3.resource(
        service_name='s3',
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)


def upload_image(user, form_picture, image):
    # Create a random filename
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    filename = random_hex + f_ext

    # Define if it's a profile or cover picture
    if image == 'profile':
        file_path = os.path.join(current_app.root_path, 'static/img/profile_pics/', filename)
        upload_path = os.path.join('img/profile_pics/', filename)
        image_size = (250, 250)
        previous_picture = user.image_file
        s3_delete_path = os.path.join('img/profile_pics/', previous_picture)
    else:
        file_path = os.path.join(current_app.root_path, 'static/img/cover_photos/', filename)
        upload_path = os.path.join('img/cover_photos/', filename)
        image_size = (1000, 1000)
        previous_picture = user.cover_photo
        s3_delete_path = os.path.join('img/cover_photos/', previous_picture)

    # Delete previous image from AWS S3
    if previous_picture == 'default_avatar.jpg' or previous_picture == 'default_cover.jpg':
        pass
    else:
        s3.Object(Config.AWS_STORAGE_BUCKET_NAME, s3_delete_path).delete()

    # Resize and save new img to local folder or heroku tmp folder
    i = Image.open(form_picture)
    i.thumbnail(image_size)
    i.save(file_path)

    # Upload file to AWS S3 bucket
    s3.Bucket(Config.AWS_STORAGE_BUCKET_NAME).upload_file(file_path, upload_path)

    return filename


def load_image(user, image):
    if image == 'profile':
        path = 'img/profile_pics/'
        user_image = user.image_file
        default_image = 'default_avatar.jpg'
    else:
        path = 'img/cover_photos/'
        user_image = user.cover_photo
        default_image = 'default_cover.jpg'

    try:
        aws_path = os.path.join(path, user_image)
        save_path = os.path.join(current_app.root_path, 'static/', path, user_image)
        s3.Bucket(Config.AWS_STORAGE_BUCKET_NAME).download_file(aws_path, save_path)
        image = url_for('static', filename=path + user_image)
    except s3.meta.client.exceptions.ClientError:
        print("The object does not exist.")
        default_path = os.path.join(path, default_image)
        image = url_for('static', filename=default_path)

    return image


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])

    msg.body = f'''To reset your password visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

# TODO Set up a BB email account from which reset mails can be sent
# For this to work less secure app approval must be enabled in the e-mail account
