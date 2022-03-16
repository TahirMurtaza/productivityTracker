import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    # Since Flask login uses sessions for authentication, create a secret key on your application.
    SECRET_KEY = os.urandom(32)
    #SqlAlchemy Database Configuration With db sqlite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)

    return app