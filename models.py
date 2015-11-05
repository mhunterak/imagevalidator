from flask.ext.login import UserMixin
from flask.ext.bcrypt import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from peewee import *
import datetime

DATABASE = SqliteDatabase('validator.db')



class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(max_length=128)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        order_by = ('-joined_at',)
        database = DATABASE

    def get_posts(self):
        return Ticket.select().where(Ticket.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user==self)
            )

    @classmethod
    def create_user(cls, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                    )
        except IntegrityError:
            raise ValueError("User Already Exists!")
        
    
def initialize():
  DATABASE.connect()
  DATABASE.create_tables([User], safe=True)
  DATABASE.close()
