
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///radiocalico.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = secrets.token_hex(32)

    db.init_app(app)

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
