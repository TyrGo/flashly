"""SQLAlchemy models for Flash App."""
import os
from datetime import datetime, timedelta
import jwt
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()
SECRET_KEY = os.environ.get('SECRET_KEY', "it's a secret")
##############################################################################
# Card model


class Card(db.Model):
    """A Card"""

    __tablename__ = 'cards'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    word = db.Column(
        db.String(25),
        nullable=False,
    )

    defn = db.Column(
        db.Text,
        nullable=False,
    )

    bin = db.Column(
        db.Integer,
        default=0,
        nullable=False,
    )

    wrongs = db.Column(
        db.Integer,
        default=0,
        nullable=False,
    )

    due = db.Column(
        db.DateTime(),
        default=datetime.now(),
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    def reset_due(self):
        """Reset due date of card by current date and bin"""

        current_time = datetime.now()
        if self.bin == 1:
            return current_time + timedelta(seconds=5)
        if self.bin == 2:
            return current_time + timedelta(seconds=25)
        if self.bin == 3:
            return current_time + timedelta(minutes=2)
        if self.bin == 4:
            return current_time + timedelta(minutes=5)
        if self.bin == 5:
            return current_time + timedelta(minutes=10)
        if self.bin == 6:
            return current_time + timedelta(hours=1)
        if self.bin == 7:
            return current_time + timedelta(hours=5)
        if self.bin == 8:
            return current_time + timedelta(days=1)
        if self.bin == 9:
            return current_time + timedelta(days=5)
        if self.bin == 10:
            return current_time + timedelta(days=25)
        if self.bin >= 11:
            return current_time + timedelta(days=120)

##############################################################################
# User model


class User(db.Model):
    """A user"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(25),
        nullable=False,
    )

    password = db.Column(
        db.Text,
        default=False,
        nullable=False,
    )

    is_admin = db.Column(
        db.Boolean,
        nullable=False,
    )

    def generate_token(self, user_id, is_admin):
        """Creates JSON Web Token"""

        payload = {'userId': user_id, 'isAdmin': is_admin}
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    @classmethod
    def sign_up(cls, username, password):
        """Signs up user. Hashes password and adds user to database"""

        try:
            hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
            user = User(username=username, password=hashed_pwd, is_admin=False)
            db.session.add(user)
            return user
        except Exception as e:
            return e

    @classmethod
    def authenticate(cls, username, password):
        """Find user by username and password; otherwise return False."""

        user = cls.query.filter_by(username=username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


def connect_db(app):
    """Connect database to app."""

    db.app = app
    db.init_app(app)
