from flask import Blueprint, jsonify, render_template

from app import db
from app.models import Item, User

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    items = Item.query.all()
    user = User.query.first()
    return render_template("index.html", items=items, user=user)


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
