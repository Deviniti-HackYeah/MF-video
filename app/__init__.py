from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)

app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DB')}"

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

app.config['MAIL_SERVER']=os.getenv("MAIL_SERVER", "")
app.config['MAIL_PORT'] = os.getenv("MAIL_PORT", 465)
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "")
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", False)
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", False)
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_SENDER", "")

print(f" CONFIG: {app.config}")