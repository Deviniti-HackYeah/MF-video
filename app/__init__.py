from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'app.login'
login_manager.init_app(app)

from .models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from .routes import app as app_blueprint
app.register_blueprint(app_blueprint, url_prefix='/api')
