from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
import secrets

from app import db
from app.models import Item, User, Song, Rating

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


@bp.route("/api/song/current")
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

    return jsonify(
        {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "album": song.album,
            "date": song.date,
            "thumbs_up": len([r for r in song.ratings if r.is_thumbs_up]),
            "thumbs_down": len([r for r in song.ratings if not r.is_thumbs_up]),
            "user_rating": "up" if user_rating and user_rating.is_thumbs_up else "down" if user_rating else None,
        }
    )


@bp.route("/api/song/rate", methods=["POST"])
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

    return jsonify(
        {
            "thumbs_up": len([r for r in song.ratings if r.is_thumbs_up]),
            "thumbs_down": len([r for r in song.ratings if not r.is_thumbs_up]),
            "user_rating": "up" if is_thumbs_up else "down",
        }
    )
