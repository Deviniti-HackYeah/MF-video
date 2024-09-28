from config import Config
import flask
from flask import (Flask, Response, jsonify, redirect, render_template, request,
                   send_from_directory, url_for, send_file, make_response, session, url_for, flash, Blueprint)
import os
from app import app
from flask import redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required

from .utils.api_helper import post_video_action, result_ready
from .utils.functions import generate_hash, check_hash
from .utils.postgres_manager import PostgresManager

app = Blueprint('app', __name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})

@app.route("/register", methods=["POST"])
def register():
    form = request.form

    username = form.get('username', '')
    name = form.get('name', '')
    surname = form.get('surname', '')
    email = form.get('email', '')
    password = form.get('password', '')
    pm = PostgresManager()
    user = pm.create_user(username, name, surname, email, generate_hash(password))

    return jsonify({
        "status": "User created succesfully",
        "message": user.to_dict()}, 200)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = request.form

    username = form.get('username', '')
    password = form.get('password', '')

    pm = PostgresManager()
    user = pm.read_user_by_username(username)

    if not user or not check_hash(password, user.password):
        return jsonify({
            "status": "ERROR",
            "message": "Invalid username or password"
        }, 401)

    login_user(user, remember=True)
    return jsonify({
        "status": "OK",
        "message": f"User {user.username} logged in"
    }, 200)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({
        "status": "OK",
        "message": "User logged out"
    }, 200)

@app.route("/api/post_video", methods=["POST"])
def post_video():
    result = post_video_action(request)
    return result

@app.route("/api/result_ready/<customer_id>/<session>", methods=["GET"])
def result_ready(customer_id, session):
    result_ready = result_ready(customer_id, session)
    return result_ready

