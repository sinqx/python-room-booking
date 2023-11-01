from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    firstName = db.Column(db.String(30), nullable=False)
    secondName = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30))  # => department
    role = db.Column(db.String(20))
    room = db.relationship("Room", backref="user")
    message = db.relationship("Message", backref="user")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mainText = db.Column(db.String(650), nullable=False)
    messageTheme = db.Column(db.String(50), nullable=False)
    creationDate = db.Column(db.DateTime(timezone=True), nullable=False)
    sentFrom = db.Column(db.Integer, db.ForeignKey("user.id"))
    sentTo = db.Column(db.String(40), nullable=False)
    sentToHead = db.Column(db.String(40), nullable=False)
    userPosition = db.Column(db.String(40))
    userInitials = db.Column(db.String(20), nullable=False)
    isViewed = db.Column(db.Boolean, default=False)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomNumber = db.Column(db.Integer, nullable=False)
    conferenceTitle = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.String(150))
    startDate = db.Column(db.DateTime(timezone=True), nullable=False)
    endDate = db.Column(db.DateTime(timezone=True), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
