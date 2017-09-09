from datetime import datetime
import hashlib
import cPickle as pickle
from dateutil.parser import parse
from geopy.geocoders import googlev3
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request

from flask_sqlalchemy import current_app
from sqlalchemy.ext.serializer import dumps
from flask_login import UserMixin, AnonymousUserMixin

from app_exceptions import GeocoderError
from . import login_manager
from . import db

from app.app_exceptions import SignupError


class User(UserMixin, db.Model):
    """
    User models
    fields:
    id          Primary key - Uniquely identifies each user
    phone_number 
    """
    __tablename__ = 'users'
    # core details
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    phone_number = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String, index=True, unique=True)

    name = db.Column(db.String(64))

    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    # auth details
    token = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))

    # account details for mobile wallet
    account = db.relationship('Account', backref="holder", uselist=False, lazy='subquery')

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    location = db.relationship('Location', backref="user", uselist=False, lazy='subquery')

    # relationship to events user has organised
    events = db.relationship('Event', backref='organiser', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.phone_number == current_app.config['ADMIN_PHONENUMBER']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.account = Account()

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

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # role verification
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_bin(self):
        return dumps(self)


class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    balance = db.Column(db.Float, default=0.0)
    points = db.Column(db.Float, default=0.0)
    purchases = db.relationship('Purchase', backref='account', lazy='subquery')


    @property
    def balance_available(self):
        return self.holder.location.currency_code + ". " + str(self.balance)


class Role(db.Model):
    """
    Anonymous - Unknown user
    user - basic permission, can register for events
    moderator - moderates events to check their eligibility
    administer - full access
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

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

    def to_bin(self):
        return pickle.dumps(self)


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, index=True)
    description = db.Column(db.String(64), index=True)

    date = db.Column(db.DateTime)
    logo_url = db.Column(db.String(64))
    closed = db.Column(db.Boolean, default=False)

    tickets = db.relationship('Ticket', backref='event', lazy='subquery')
    organiser_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    db.relationship('Location', backref="event", uselist=False, lazy='subquery')
    venue = db.Column(db.String(64))

    def __repr__(self):
        return "<Event {}>".format(self.name)

    def can_add_tickets(self):
        if self.tickets.count() == len(current_app.config["TICKET_TYPES"]):
            return False
        else:
            return True

    def to_bin(self):
        return pickle.dumps(self)

    @property
    def day(self):
        return self.date.strftime('%B %d, %y')


class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    code = db.Column(db.String(64), unique=True)
    url = db.Column(db.String(64))
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    confirmed = db.Column(db.Boolean, default=False)

    def to_json(self):
        json_data = {}
        json_data.setdefault('count', self.count)
        json_data.setdefault('type', self.ticket.type)
        json_data["PurchaserUserName"] = self.account.holder.username 
        json_data["Event Name"] = self.ticket.event.title
        json_data["Event Date"] = self.ticket.event.date
        return json_data


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    price = db.Column(db.Float)
    type = db.Column(db.String(64), default='regular', index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    purchases = db.relationship('Purchase', backref='ticket', lazy='dynamic')

    def __repr__(self):
        return "<Type> {} <Price> {}".format(self.type, self.price)

    @property
    def price_code(self):
        return self.event.location.currency_code + ". " + str(self.price)
    
    @staticmethod
    def from_json(json_data):
        type = json_data.get('type', None)
        event_id = json_data.get('event_id', None)
        price = json_data.get("price")
        if event_id is None:
            raise (ValueError('A ticket must be associated with an event'))
        ticket = Ticket(event_id=event_id, price=price)
        if type is None:
            raise (ValueError('Please specify the ticket type'))
        ticket.type = type
        return ticket


class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64))
    city = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    codes = {
        "kenya": {
            "currency": "KES"
        },
        "uganda": {
            "currency": "UGX"
        }
    }

    @property
    def address(self):
        return self.city

    @address.setter
    def address(self, city):
        try:
            geocoder = googlev3.GoogleV3()
            location = str(geocoder.geocode(city).address)
            self.city, self.country = location.split(", ")
        except:
            raise GeocoderError

    @property
    def currency_code(self):
        return self.codes.get(self.country.lower()).get("currency")

    @property
    def country_code(self):
        return self.codes.get(self.country.lower()).get("phone")

    def __repr__(self):
        return "{} {}".format(self.city, self.country)
