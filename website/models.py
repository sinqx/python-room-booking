from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    firstName = db.Column(db.String(30), nullable=False)
    secondName = db.Column(db.String(30), nullable=False)
    surName = db.Column(db.String(30), nullable=False)
    department = db.Column(db.String(90))
    role = db.Column(db.String(20))
    room = db.relationship("Room", backref="user")

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomName = db.Column(db.String(30), nullable=False)
    conferenceTitle = db.Column(db.String(60), nullable=False)
    startDate = db.Column(db.DateTime(timezone=True), nullable=False)
    endDate = db.Column(db.DateTime(timezone=True), nullable=False)
    comment = db.Column(db.String(180))
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
