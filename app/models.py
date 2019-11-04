from datetime import date, datetime
from pony.orm import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from uuid import UUID, uuid4

db = Database()

class User(db.Entity, UserMixin):
    _table_ = 'user'
    id = PrimaryKey(int, auto=True)
    user_id = Required(UUID, unique=True, default=lambda: uuid4())
    email = Required(str, unique=True)
    password = Required(str)
    first_name = Required(str)
    last_name = Required(str)
    user_bio = Optional(str, 128)
    created_date = Required(datetime, default=lambda: datetime.utcnow())
    last_updated = Required(datetime, default=lambda: datetime.utcnow())
    messages = Set('Message')
    chats = Set('Chat')
    contacts = Set('User', reverse='contacts')
    blocked = Set('User', reverse='blocked')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password_hash(self, password):
        return check_password_hash(self.password, password)

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name


class Message(db.Entity):
    _table_ = 'message'
    id = PrimaryKey(int, auto=True)
    sender_id = Required(User)
    chat = Required('Chat')
    body = Required(LongStr)
    date_created = Required(datetime, default=lambda: datetime.utcnow())


class Chat(db.Entity):
    _table_ = 'chat'
    id = PrimaryKey(int, auto=True)
    chat_name = Required(str)
    creator_id = Required(int)
    date_created = Required(datetime, default=lambda: datetime.utcnow())
    last_updated = Required(datetime, default=lambda: datetime.utcnow())
    is_group = Required(bool, default='false')
    users = Set(User)
    messages = Set(Message)


    @property
    def avatar(self):
        return f'https://robohash.org/{self.chat_name}.png?size=50x50'

