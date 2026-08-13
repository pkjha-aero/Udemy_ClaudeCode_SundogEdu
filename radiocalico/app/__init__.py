
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
import secrets
import os

db = SQLAlchemy()
csrf = CSRFProtect()
compress = Compress()


def create_app():
    app = Flask(__name__)

    # Support PostgreSQL in production, SQLite in development
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # PostgreSQL connection string
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        # SQLite for development
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///radiocalico.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = secrets.token_hex(32)
    app.config["COMPRESS_LEVEL"] = 6
    app.config["COMPRESS_MIN_SIZE"] = 500

    db.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()
        _seed_default_user()

    return app


def _seed_default_user():
    from app.models import User

    if User.query.count() == 0:
        db.session.add(User(name="Pankaj Jha", email="pankaj.psu@gmail.com"))
        db.session.commit()
