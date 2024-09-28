from datetime import datetime
from flask_login import UserMixin

from . import db

class User(UserMixin, db.Model):
    """
    Defines a model for user data with attributes such as name, email, company, password,
    and role (user or admin).
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
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
        """Dict generation to store it in .json file, if necessary"""
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "created_at": self.created_at,
            "files": [file.to_dict() for file in self.files]   
        }

class File(db.Model):
    """
    Represents a document entity with various attributes such as name, type, category,
    file size, status (New/InProgress/Done), processed status (True/False), dates, content,
    and related json files.
    """
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    hash = db.Column(db.String(100), nullable=True)
    ftype = db.Column(db.String(100), nullable=True)
    progress= db.Column(db.Numeric(scale=1), default=0.0)
    created_at =  db.Column(db.DateTime, default=datetime.now)
    processed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', back_populates='files')

    analysis = db.relationship('Analysis', back_populates='file', cascade="all, delete")

    def __init__(
            self, name, ftype, size, user_id, hash
            ):
        self.name = name
        self.ftype = ftype
        self.size = size
        self.user_id = user_id
        self.hash = hash


    def to_dict(self):
        """Dict generation to store it in .json file, if necessary"""
        return {
            "id": self.id,
            "name": self.name,
            "hash": self.hash,
            "document_type": self.ftype,
            "created_at": self.created_at.strftime("%d.%m.%Y"),
            "progress": self.progress,
            "processed": self.processed,
            "file": self.size,
            "user_id": self.user_id
        }

class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)

    def __init__(self, file_id):
        self.file_id = file_id

    def to_dict(self):
        return {
            "id": self.id,
            "file_id": self.file_id
        }
