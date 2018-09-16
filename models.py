import datetime

from peewee import *
import flask_mysqldb
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash


DATABASE = MySQLDatabase('micro', user='root', password='13571113', host='localhost', port=3306)


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = False

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)


    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )

    
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)

        except IntegrityError:
            raise ValueError("User exists already")



class Post(Model):

    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User, related_name='posts')

    content = TextField()


    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)



def initialise():
    DATABASE.connect()
    DATABASE.create_tables([User, Post], safe=True)
    DATABASE.close()

