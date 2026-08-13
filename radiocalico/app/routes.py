from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for, make_response
import secrets
from sqlalchemy import func
from functools import wraps

from app import db, csrf
from app.models import Item, User, Song, Rating
from app.template_helpers import prepare_index_context

bp = Blueprint("main", __name__)


def add_cache_headers(max_age=3600):
    """Decorator to add Cache-Control headers to responses."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers["Cache-Control"] = f"public, max-age={max_age}"
            return response
        return decorated_function
    return decorator


def add_api_cache_headers(max_age=30):
    """Decorator to add Cache-Control headers to API responses."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers["Cache-Control"] = f"private, max-age={max_age}"
            return response
        return decorated_function
    return decorator


@bp.route("/")
def index():
    items = Item.query.all()
    users = User.query.all()
    context = prepare_index_context(items, users)
    return render_template("index.html", **context)


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
@csrf.exempt
@add_api_cache_headers(max_age=300)
def api_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])


@bp.route("/api/users")
@csrf.exempt
@add_api_cache_headers(max_age=300)
def api_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@bp.route("/api/health")
@csrf.exempt
@add_api_cache_headers(max_age=30)
def health():
    return jsonify({"status": "ok"})


@bp.route("/api/song/current")
@csrf.exempt
@add_api_cache_headers(max_age=30)
def get_current_song():
    if "session_id" not in session:
        session["session_id"] = secrets.token_hex(16)

    title = request.args.get("title", "Unknown")
    artist = request.args.get("artist", "Unknown")
    album = request.args.get("album", "Unknown")
    date = request.args.get("date", "")

    song = Song.query.filter_by(title=title, artist=artist).first()
    if not song:
        song = Song(title=title, artist=artist, album=album, date=date)
        db.session.add(song)
        db.session.commit()

    user_rating = Rating.query.filter_by(
        song_id=song.id, session_id=session["session_id"]
    ).first()

    thumbs_up = db.session.query(func.count(Rating.id)).filter(
        Rating.song_id == song.id,
        Rating.is_thumbs_up == True
    ).scalar() or 0

    thumbs_down = db.session.query(func.count(Rating.id)).filter(
        Rating.song_id == song.id,
        Rating.is_thumbs_up == False
    ).scalar() or 0

    return jsonify(
        {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "album": song.album,
            "date": song.date,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "user_rating": "up" if user_rating and user_rating.is_thumbs_up else "down" if user_rating else None,
        }
    )


@bp.route("/api/song/rate", methods=["POST"])
@csrf.exempt
def rate_song():
    if "session_id" not in session:
        session["session_id"] = secrets.token_hex(16)

    data = request.get_json()
    song_id = data.get("song_id")
    is_thumbs_up = data.get("is_thumbs_up")

    if not song_id or is_thumbs_up is None:
        return jsonify({"error": "Missing song_id or is_thumbs_up"}), 400

    song = Song.query.get(song_id)
    if not song:
        return jsonify({"error": "Song not found"}), 404

    existing_rating = Rating.query.filter_by(
        song_id=song_id, session_id=session["session_id"]
    ).first()

    if existing_rating:
        existing_rating.is_thumbs_up = is_thumbs_up
    else:
        rating = Rating(
            song_id=song_id, session_id=session["session_id"], is_thumbs_up=is_thumbs_up
        )
        db.session.add(rating)

    db.session.commit()

    thumbs_up = db.session.query(func.count(Rating.id)).filter(
        Rating.song_id == song_id,
        Rating.is_thumbs_up == True
    ).scalar() or 0

    thumbs_down = db.session.query(func.count(Rating.id)).filter(
        Rating.song_id == song_id,
        Rating.is_thumbs_up == False
    ).scalar() or 0

    return jsonify(
        {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "album": song.album,
            "date": song.date,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "user_rating": "up" if is_thumbs_up else "down",
        }
    )
