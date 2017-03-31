import os
import binascii

from flask import Flask, render_template, current_app
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required

from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Date, LargeBinary, Integer, Boolean, Text, String, DateTime, ForeignKey, Float


from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from io import StringIO

from .. import db
Base = db.Model


# Define models
roles_users = Table('roles_users',
        Base.metadata,
        Column('user_id', Integer, ForeignKey('user.id')),
        Column('role_id', Integer, ForeignKey('role.id')))


class Role(Base, RoleMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    @staticmethod
    def insert_roles():
        for r in APPLICATION_ROLES:
            role = Role.query.filter_by(name=r[0]).first()
            if role is None:
                role = Role()
                role.name = r[0]
                role.description = r[1]
                db.session.add(role)
        db.session.commit()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.__unicode__()


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __unicode__(self):
        return self.email

    def __repr__(self):
        return self.__unicode__()

    @property
    def password(self):
        raise AttributeError("User Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({'confirm': self.id})

    def generate_email_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({'id': self.id})

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data["id"])
        return user

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.load(StringIO(token))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.active = True
        db.session.add(self)
        return True

    @staticmethod
    def verify_email_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data["id"])
        return user

    def can(self, permission):
        roles = [x.name.lower() for x in self.roles]
        if "administrator" in roles:
            return True
        else:
            return permission.lower() in roles

    def is_user(self):
        return self.can("user")

    def is_admin(self):
        return self.can("administrator")

    def get_id(self):
        return self.id


user_datastore = SQLAlchemyUserDatastore(db, User, Role)


APPLICATION_ROLES = [
    ("User", "General site user"),
    ("Administrator", "Site administrator")
]
