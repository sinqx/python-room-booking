from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(30), unique = True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    second_name = db.Column(db.String(30))
    role = db.Column(db.String(20))
    room = db.relationship('Room', backref='user')
    

class Room(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    roomNumber = db.Column(db.Integer, nullable=False)
    conferenceTitle = db.Column(db.String(30))
    startDate = db.Column(db.DateTime(timezone=True), nullable=False)
    endDate = db.Column(db.DateTime(timezone=True), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
