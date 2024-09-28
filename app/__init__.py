from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import os
from dotenv import load_dotenv
import whisper

load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
whisper_model = whisper.load_model('large')

from .routes import app as app_blueprint
app.register_blueprint(app_blueprint)
