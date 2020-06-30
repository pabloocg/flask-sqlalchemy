import datetime
from cfg import db


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    image_name = db.Column(db.String)
    messages = db.relationship('Message', backref='users', lazy=True)

    def __init__(self, first_name, last_name, image_name):
        self.first_name = first_name
        self.last_name = last_name
        self.image_name = image_name

    def __repr__(self):
        return f"This user's {self.first_name} {self.last_name}"
