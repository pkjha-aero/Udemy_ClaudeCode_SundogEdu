from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from app import db
from app.models import Item, User

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    items = Item.query.all()
    users = User.query.all()
    return render_template("index.html", items=items, users=users)


@bp.route("/player")
def player():
    return render_template("player.html")


@bp.route("/users", methods=["POST"])
def add_user():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if name and email and not User.query.filter_by(email=email).first():
        db.session.add(User(name=name, email=email))
        db.session.commit()

    return redirect(url_for("main.index"))


@bp.route("/api/items")
def api_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])


@bp.route("/api/users")
def api_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@bp.route("/api/health")
def health():
    return jsonify({"status": "ok"})
