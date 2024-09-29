from config import Config
import flask
from flask import (Flask, Response, jsonify, redirect, render_template, request,
                   send_from_directory, url_for, send_file, make_response, session, url_for, flash, Blueprint)
import os
from app import app
from flask import redirect, render_template, url_for
from flask_cors import cross_origin

from app.utils.api_helper import post_video_action, result_ready, get_file_path, send_mail_ok
from app.utils.functions import generate_hash, check_hash, write_to_file_with_lock, read_from_file_with_lock
from app.utils.postgres_manager import PostgresManager
from app.utils.text_results import TextResults

from app.models import User

app = Blueprint('app', __name__)

data_dir = os.environ.get('DATA_DIR')
cache_dir = os.environ.get('CACHE_DIR')


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
    # form = request.form
    req = request.get_json()

    username = req.get('username', '')
    password = req.get('password', '')

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
    pm = PostgresManager()
    users_data, _ = pm.read_all_users()
    users = users_data.get("data", [])
    return jsonify({
        "status": "OK",
        "message": users
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
    
@app.route("/send_email", methods=["POST"])
@cross_origin()
def send_mail():
    req = request.get_json()

    params = {
        "email": req.get('email', ''),
        "user_id": req.get('user_id', ''),
        "session": req.get('session', '')
    }
    resp = send_mail_ok(params)
    if resp.get("status") == "ERROR":
        return jsonify(resp), 424
    return jsonify(resp), 200

@app.route("/target_check", methods=["GET"])
@cross_origin()
def target_check():
    form = request.form
    req = request.get_json()
    user_id = req.get('user_id', '')
    session = req.get('session', '')
    target_groups = req.get('target_groups', '')
    target_education = req.get('target_education', '')
    transcription_data = read_from_file_with_lock(os.path.join(data_dir, str(user_id), str(session), "transcription_data.json"))
    full_text = transcription_data.get("full_text", "")
    tr = TextResults(cache_dir, user_id, session, data_dir)
    _ = tr.target_group_check(full_text, target_groups, target_education)
    return jsonify({
        "status": "OK",
        "message": "Target group check done"
    }, 200)

@app.route("/get_results", methods=["GET"])
@cross_origin()
def get_transcriptions_results():
    form = request.form
    req = request.get_json()
    user_id = req.get('user_id', '')
    session = req.get('session', '')
    folder_path = os.path.join(data_dir, str(user_id), str(session))
    jsons_in_folder = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if len(jsons_in_folder) < 15:
        return jsonify({
            "status": "Pending",
            "message": "Results are not ready yet"
        }, 201)
    transcription_results = []
    for json_file in jsons_in_folder:
        if json_file == "pause_check.json" or json_file == "false_words.json":
            continue
        data = read_from_file_with_lock(os.path.join(folder_path, json_file))
        transcription_results.append(data)

    return jsonify({"transcriptions": transcription_results}, 200)

@app.route("/get_pauses_results", methods=["GET"])
@cross_origin()
def get_pauses_results():
    form = request.form
    req = request.get_json()
    user_id = req.get('user_id', '')
    session = req.get('session', '')
    folder_path = os.path.join(data_dir, str(user_id), str(session))
    pause_check = read_from_file_with_lock(os.path.join(folder_path, "pause_check.json"))
    return jsonify(pause_check, 200)

@app.route("/get_false_words_results", methods=["GET"])
@cross_origin()
def get_false_words_results():
    form = request.form
    req = request.get_json()
    user_id = req.get('user_id', '')
    session = req.get('session', '')
    folder_path = os.path.join(data_dir, str(user_id), str(session))
    false_words = read_from_file_with_lock(os.path.join(folder_path, "false_words.json"))
    return jsonify(false_words, 200)
