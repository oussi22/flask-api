from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return f"User>>> {self.username}"


class Decision(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=True)
    formation = db.Column(db.String, nullable=True)
    content = db.Column(db.Text, nullable=True )
