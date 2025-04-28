from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import AppConfig


app = Flask(__name__)
app.config.from_object(AppConfig)

db = SQLAlchemy(app, session_options={"expire_on_commit": False})

with app.app_context():
    from models import *
    db.create_all()

import views
import hooks
