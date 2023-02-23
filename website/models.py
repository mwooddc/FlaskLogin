from . import db
# The UserMixin library allows us to use built in methods called:
# is_authenticated, is_active, is_annoymous, get_id()
#see: https://youtu.be/2dEM-s3mRLE?t=282
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    #The UserMixin library insists that the field in the database for a user is called
    #id and not things like UID or user_ID, it has to be called id
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
