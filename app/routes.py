from config import Config
import flask
from flask import (Flask, Response, jsonify, redirect, render_template, request,
                   send_from_directory, url_for, send_file, make_response, session, url_for, flash, Blueprint)
import os
from app import app
from flask import redirect, render_template, url_for

app = Blueprint('app', __name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})
