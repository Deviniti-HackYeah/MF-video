from config import Config
import flask
from flask import (Flask, Response, jsonify, redirect, render_template, request,
                   send_from_directory, url_for, send_file, make_response, session, url_for, flash, Blueprint)
import os
from app import app
from flask import redirect, render_template, url_for

from .utils.api_helper import post_video_action, result_ready

app = Blueprint('app', __name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})

@app.route("/api/post_video", methods=["POST"])
def post_video():
    result = post_video_action(request)
    return result

@app.route("/api/result_ready/<customer_id>/<session>", methods=["GET"])
def result_ready(customer_id, session):
    result_ready = result_ready(customer_id, session)
    return result_ready