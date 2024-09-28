from flask import jsonify
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy import desc, and_
from app import db
from app.models import User, File


class PostgresManager:
    """
    Class for postgresql database CRUD operations.
    """
    def __init__(self):
        self.db = db
    
    def create_user(self, username, name, surname, email, password):
        """
        Create a new user in the database.
        """
        user = User(username, name, surname, email, password)
        self.db.session.add(user)
        self.db.session.commit()
        return {"message": "user created", "data": user.to_dict()}, 200
    
    def read_user(self, user_id):
        """
        Read a user from the database.
        """
        user = User.query.get(user_id)
        if user:
            return {"message": "user exist", "data": user.to_dict()}, 200
        return {"message": "user not found", "data": {}}, 404
    
    def read_user_by_username(self, username):
        """
        Read a user from the database by username.
        """
        user = User.query.filter_by(username=username).first()
        if user:
            return {"message": "user exist", "data": user.to_dict()}, 200
        return {"message": "user not found", "data": {}}, 404
    
    def create_file(self, name, ftype, size, user_id, hash):
        """
        Create a new file in the database.
        """
        file = File(name, ftype, size, user_id, hash)
        self.db.session.add(file)
        self.db.session.commit()
        return {"message": "file created", "data": file.to_dict()}, 200
    
