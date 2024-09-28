from config import Config
import flask
from flask import (Flask, Response, jsonify, redirect, render_template, request,
                   send_from_directory, url_for, send_file, make_response, session, url_for, flash, Blueprint)
import os
from app import app
from flask import redirect, render_template, url_for
from flask_cors import cross_origin

from app.utils.api_helper import post_video_action, result_ready, get_file_path, send_mail_ok
from app.utils.functions import generate_hash, check_hash
from app.utils.postgres_manager import PostgresManager

from app.models import User

app = Blueprint('app', __name__)

data_dir = os.environ.get('DATA_DIR')


@app.route("/", methods=["GET", "OPTIONS"])
@cross_origin()
def home():
    return jsonify({"message": "Hello, World!"})

@app.route("/register", methods=["POST"])
@cross_origin()
def register():
    form = request.form

    username = form.get('username', '')
    name = form.get('name', '')
    surname = form.get('surname', '')
    email = form.get('email', '')
    password = form.get('password', '')
    pm = PostgresManager()
    user_data, _ = pm.create_user(username, name, surname, email, generate_hash(password))
    user = user_data.get("data", {})
    return jsonify({
        "status": "User created succesfully",
        "message": user}, 200)

@app.route("/login", methods=['GET', 'POST'])
@cross_origin()
def login():
    form = request.form

    username = form.get('username', '')
    password = form.get('password', '')

    pm = PostgresManager()

    user_data, _ = pm.read_user_by_username(username)
    print(f"user_data: {user_data}")

    user = user_data.get("data", {})

    print(f"Looking for user: {username}")
    print(f"User: {user}")

    if not user.get('username', '') or not check_hash(password, user.get('password', '')):
        print(f"username: {user.get('username', '') }")
        print(f"password: {user.get('password', '')}")
        print(f"entered password: {password}")
        return jsonify({
            "status": "ERROR",
            "message": "Invalid username or password"
        }, 401)

    # login_user(user, remember=True)
    return jsonify({
        "status": "OK",
        "message": f"User {user.get('username', '')} logged in"
    }, 200)

@app.route("/logout")
@cross_origin()
def logout():
    # logout_user()
    return jsonify({
        "status": "OK",
        "message": "User logged out"
    }, 200)

@app.route("/get_users", methods=["GET"])
@cross_origin()
def get_users():
    users = User.query.all()
    return jsonify({
        "status": "OK",
        "message": "Users found",
        "data": [user.to_dict() for user in users]
    }, 200)

@app.route("/post_video", methods=["POST"])
@cross_origin()
def post_video():
    result = post_video_action(request)
    return jsonify(result)

@app.route("/result_ready/<customer_id>/<session>", methods=["GET"])
@cross_origin()
def result_ready(customer_id, session):
    result_ready = result_ready(customer_id, session)
    return jsonify(result_ready)

@app.route("/download/<customer_id>/<session>", methods=["GET"])
@cross_origin()
def get_result(customer_id, session):
    if result_ready(customer_id, session):
        folder_path = os.path.join(data_dir, str(customer_id), str(session))
        return send_from_directory(directory=folder_path,
                                   path=get_file_path(folder_path),
                                   download_name="result.pdf",
                                   as_attachment=True)
    return jsonify({
        "status": "ERROR",
        "message": "Result is not ready! You can check if it is ready using ready_suffix",
        "ready_suffix": f"/api/result_ready/{customer_id}/{session}"}), 403
    
@app.route("/send_email/<customer_id>/<session>", methods=["POST"])
@cross_origin()
def send_mail(customer_id, session):
    params = {
        "customer_id": customer_id,
        "session": session 
    }
    resp = send_mail_ok(request, params)
    if resp.get("status") == "ERROR":
        return jsonify(resp), 424
    return jsonify(resp), 200
    
@app.route("/delete_reuslts/<customer_id>/<session>", methods=["GET"])
@cross_origin()
def delete_results(customer_id, session):
    print(f"customer id: {customer_id}, session id: {session}")
    deleted = delete_results(customer_id, session)
    if deleted['status'] == "ERROR":
        return jsonify(deleted), 420
    return jsonify(deleted), 200
