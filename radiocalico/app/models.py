from datetime import datetime

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255))
    date = db.Column(db.String(4))
    ratings = db.relationship("Rating", backref="song", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        thumbs_up = len([r for r in self.ratings if r.is_thumbs_up])
        thumbs_down = len([r for r in self.ratings if not r.is_thumbs_up])
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "date": self.date,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
        }


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), nullable=False)
    session_id = db.Column(db.String(128), nullable=False)
    is_thumbs_up = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("song_id", "session_id", name="unique_song_rating_per_session"),)
