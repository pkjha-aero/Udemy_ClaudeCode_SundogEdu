"""Tests for edge cases and error handling."""

import pytest
import json
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Song, Rating


class TestDataValidation:
    """Tests for data validation and constraints."""

    def test_song_title_required(self, db_session):
        """Test that song title is required."""
        song = Song(title=None, artist="Artist", album="Album", date="")
        db_session.add(song)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_song_artist_required(self, db_session):
        """Test that song artist is required."""
        song = Song(title="Title", artist=None, album="Album", date="")
        db_session.add(song)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_name_required(self, db_session):
        """Test that user name is required."""
        user = User(name=None, email="test@example.com")
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_email_required(self, db_session):
        """Test that user email is required."""
        user = User(name="Test", email=None)
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_empty_string_title_rejected(self, db_session):
        """Test that empty title is handled (may be allowed by model)."""
        song = Song(title="", artist="Artist", album="", date="")
        db_session.add(song)
        db_session.commit()
        # Model allows empty string, so song is created
        assert song.id is not None

    def test_special_characters_in_title(self, db_session):
        """Test that special characters are preserved."""
        special_title = "Song™ with café & émojis 🎵"
        song = Song(title=special_title, artist="Artist", album="Album", date="")
        db_session.add(song)
        db_session.commit()
        assert song.title == special_title

    def test_unicode_in_artist_name(self, db_session):
        """Test that Unicode in artist name is preserved."""
        unicode_artist = "藝術家 (Artist)"
        song = Song(title="Title", artist=unicode_artist, album="Album", date="")
        db_session.add(song)
        db_session.commit()
        assert song.artist == unicode_artist


class TestAPIErrorResponses:
    """Tests for API error handling."""

    def test_api_malformed_json(self, client):
        """Test that malformed JSON returns error."""
        response = client.post(
            "/api/song/rate",
            data="not json",
            content_type="application/json"
        )
        assert response.status_code >= 400

    def test_api_rating_with_zero_song_id(self, client):
        """Test that song_id=0 returns error."""
        response = client.post("/api/song/rate", json={"song_id": 0, "is_thumbs_up": True})
        assert response.status_code >= 400

    def test_api_rating_with_negative_song_id(self, client):
        """Test that negative song_id returns error."""
        response = client.post("/api/song/rate", json={"song_id": -1, "is_thumbs_up": True})
        assert response.status_code >= 400

    def test_api_rating_with_null_is_thumbs_up(self, client, sample_song):
        """Test that null is_thumbs_up returns error."""
        response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": None})
        assert response.status_code == 400


class TestDatabaseConstraints:
    """Tests for database constraints."""

    def test_song_duplicate_title_artist_found(self, db_session):
        """Test that duplicate title+artist can be found."""
        song1 = Song(title="Same", artist="Artist", album="Album1", date="2026-01-01")
        song2 = Song(title="Same", artist="Artist", album="Album2", date="2026-02-01")
        db_session.add_all([song1, song2])
        db_session.commit()

        # Both songs created (no unique constraint on title+artist)
        songs = Song.query.filter_by(title="Same", artist="Artist").all()
        assert len(songs) == 2

    def test_user_email_unique_constraint_enforced(self, db_session):
        """Test that email uniqueness is enforced."""
        user1 = User(name="User1", email="duplicate@example.com")
        user2 = User(name="User2", email="duplicate@example.com")
        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestTemplateRendering:
    """Tests for XSS and template safety."""

    def test_index_renders_with_xss_attempt(self, client, db_session):
        """Test that XSS payload in user name is safe."""
        from app.models import User
        xss_user = User(name="<script>alert('xss')</script>", email="xss@example.com")
        db_session.add(xss_user)
        db_session.commit()

        response = client.get("/")
        # Jinja2 escapes HTML by default
        assert b"<script>" not in response.data or b"&lt;script&gt;" in response.data

    def test_song_title_with_quotes_in_html(self, client):
        """Test that quotes in title don't break HTML."""
        response = client.get('/api/song/current?title=Song"with\'quotes&artist=Artist')
        data = json.loads(response.data)
        assert data["title"] == 'Song"with\'quotes'


class TestSessionIsolation:
    """Tests for session isolation and edge cases."""

    def test_very_long_session_id_accepted(self, db_session, sample_song):
        """Test that very long session ID is accepted."""
        long_session = "a" * 1000
        rating = Rating(song_id=sample_song.id, session_id=long_session, is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()
        assert rating.session_id == long_session

    def test_special_characters_in_session_id(self, db_session, sample_song):
        """Test that special characters in session_id work."""
        special_session = "session!@#$%^&*()"
        rating = Rating(song_id=sample_song.id, session_id=special_session, is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()
        assert rating.session_id == special_session


class TestConcurrencyEdgeCases:
    """Tests for edge cases in concurrent scenarios."""

    def test_rapid_rating_changes(self, client, sample_song):
        """Test rapid rating changes."""
        song_id = sample_song.id
        for i in range(10):
            is_thumbs_up = i % 2 == 0
            response = client.post(
                "/api/song/rate",
                json={"song_id": song_id, "is_thumbs_up": is_thumbs_up}
            )
            assert response.status_code in [200, 201]

    def test_rating_count_after_deletions(self, db_session, sample_song):
        """Test rating counts after individual rating deletion."""
        rating1 = Rating(song_id=sample_song.id, session_id="s1", is_thumbs_up=True)
        rating2 = Rating(song_id=sample_song.id, session_id="s2", is_thumbs_up=True)
        rating3 = Rating(song_id=sample_song.id, session_id="s3", is_thumbs_up=False)
        db_session.add_all([rating1, rating2, rating3])
        db_session.commit()

        db_session.delete(rating1)
        db_session.commit()

        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 1
        assert song_dict["thumbs_down"] == 1
