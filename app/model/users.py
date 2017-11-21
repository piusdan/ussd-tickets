"""User relation
"""
from datetime import datetime
from flask import request
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import Integer, String, DateTime, Column, Boolean, ForeignKey, Float
from sqlalchemy.orm  import relationship
from flask_sqlalchemy import current_app
from flask_login import UserMixin, AnonymousUserMixin

from app import login_manager, hashids
from app.database import db
from app.utils.database import CRUDMixin, slugify
from app.utils.web import eastafrican_time

class Role(db.Model):
    """
    :param id: Unique identification for the role
    :type id: Integer
    :param name: Name for the role
    :param permissions: Set of permissions allowed for the role
    :param users: Assosiation of user's with the role
    :param default: default role for user
    :type default: Boolean
    """
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False)
    default = db.Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return "Role " + self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.BUY_TICKET, True),
            'Moderator': (Permission.BUY_TICKET |
                          Permission.ORGANIZE_EVENT |
                          Permission.MODERATE_EVENT, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Permission:
    BUY_TICKET = 0x01
    ORGANIZE_EVENT = 0x04
    MODERATE_EVENT = 0x08
    ADMINISTER = 0x80


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class User(UserMixin, CRUDMixin,db.Model):
    """
    :param id: Users ID unique for every user
    :param username: Unique username for every user
    :param phone_number: Unique phone number for every user, must start with a country code
    :param email: User's email address, Unique but optional
    :param address_id: The address relation id for a user
    :param account: One-to-One association to the user's account
    :param tickets: Users event tickets
    :param member_since: Tracks when user joined
    :param last_seen: last time the user was online
    :param role_id: Id of a user's role
    :param slug: Unique name/used for api endpoints for a user
    :param confirmed: Boolean to check if models is confirmed
    :type confirmed: Boolean
    :param avartar_hash: a hash of a user's avartar generated by gravartar
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    phone_number = Column(String(64), index=True, unique=True, nullable=False)
    email = Column(String, index=True, unique=True)
    confirmed = Column(Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    member_since = Column(DateTime, default=eastafrican_time)
    last_seen = Column(DateTime, default=eastafrican_time)
    _password = Column(String(128))
    role_id = Column(Integer, ForeignKey('roles.id'))
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship('Address', backref="users", lazy='subquery')
    account = relationship("Account", backref="user", uselist=False)
    tickets = relationship("Ticket", backref="user", lazy='dynamic')
    transactions =relationship('Transaction', backref='user', lazy='dynamic')

    slug = Column(String)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # assign role
        if self.role is None:
            if self.phone_number == current_app.config['ADMIN_PHONENUMBER']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        # assign an avatar hash
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        # create a new user account
        self.account = Account()
        self.slug = slugify(self.username)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        if self.email:
            hash = self.avatar_hash or hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        else:
            hash = self.avatar_hash or hashlib.md5(
                self.username + "@gmail.com".encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('Password is not a readable property')

    @property
    def code(self):
        return hashids.encode(self.id)

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    # user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def by_slug(slug):
        return db.session.query(User).filter(User.slug==slug).first()

    @staticmethod
    def by_phonenumber(phonenumber):
        return db.session.query(User).filter(User.phone_number==phonenumber).first()

    @staticmethod
    def by_username(username):
        return db.session.query(User).filter(User.username==username).first()

    @staticmethod
    def by_id(id):
        return User.query.get(id)

    @staticmethod
    def all():
        return db.session.query(User).all()

    # role verification
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

login_manager.anonymous_user = AnonymousUser


class Account(CRUDMixin, db.Model):
    """
    :param id: Unique identifier
    :param user_id: User's account id
    :param balance: User's account balance
    :param points: User's CVS points balance
    """
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey("user.id"))
    balance = Column(Float, default=0.00)
    points =Column(Float, default=0.00)

class Transaction(CRUDMixin, db.Model):
    """
    :param id: Unique identifier for the transaction
    :param request_id: Unique transaction request id
    :param status: Failed, Pending, Success - Request fro the transaction
    :param Description: More info about the transaction
    :param transaction_cost: Cost of the transaction
    :param timestamp: Time transaction took place
    :param request_id: Used to track responses fro AT gateway
    """
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    status = Column(String(12), default='Pending')
    description = Column(String)
    request_id = Column(String(255), default=None)
    amount = Column(Float, default=0.00)
    transaction_cost = Column(Float, default=0.00)
    timestamp = Column(DateTime, default=eastafrican_time)

    @property
    def transaction_code(self):
        return hashids.encode(self.id)

    @property
    def date(self):
        return self.timestamp.date().strftime('%d/%m/%y')

    @property
    def time(self):
        return self.timestamp.time().strftime('%H:%M %p')

    @staticmethod
    def by_id(id):
        return Transaction.query.get(id)

    @staticmethod
    def by_requestId(request_id):
        return Transaction.query.filter_by(request_id=request_id).first()

    @staticmethod
    def by_transactionCode(trasaction_code):
        id = hashids.decode(trasaction_code)[0]
        return Transaction.by_id(id)