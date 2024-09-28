from datetime import datetime
from flask_login import UserMixin
from flask import jsonify
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    files = db.relationship('File', back_populates='user', cascade="all, delete")

    def __init__(self, username, name, surname, email, password):
        self.username = username
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "files": [file.to_dict() for file in self.files]
        }

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(100), nullable=True)
    ftype = db.Column(db.String(100), nullable=True)
    size = db.Column(db.Integer, nullable=False)  # Dodano atrybut size
    progress = db.Column(db.Float, default=0.0)  # Zmieniono na db.Float
    session = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    processed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', back_populates='files')

    analysis = db.relationship('Analysis', back_populates='file', cascade="all, delete")

    def __init__(self, name, ftype, size, session, user_id, hash):
        self.name = name
        self.ftype = ftype
        self.size = size
        self.session = session
        self.user_id = user_id
        self.hash = hash

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "hash": self.hash,
            "document_type": self.ftype,
            "created_at": self.created_at.strftime("%d.%m.%Y") if self.created_at else None,
            "progress": self.progress,
            "processed": self.processed,
            "session": self.session,
            "size": self.size,
            "user_id": self.user_id
        }

class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)
    file = db.relationship('File', back_populates='analysis')  # Dodano relację

    def __init__(self, file_id):
        self.file_id = file_id

    def to_dict(self):
        return {
            "id": self.id,
            "file_id": self.file_id
        }
