import datetime

from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash


DATABASE = SqliteDatabase('microblog.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(datetime.datetime.now)
    is_admin = False

    class meta:
        database = Database
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                is_admin=admin)

        except IntegrityError:
            raise ValueError("User exists already")


def initialise():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()

