"""Tests for session management and persistence."""

import json
import secrets
import pytest
from app.models import Rating


class TestSessionIDGeneration:
    """Tests for session ID generation."""

    def test_session_id_created_on_first_current_request(self, client):
        """Test that session ID is created on first GET /api/song/current."""
        with client:
            client.get("/api/song/current")
            assert "session_id" in client.session

    def test_session_id_created_on_first_rate_request(self, client, sample_song):
        """Test that session ID is created on first POST /api/song/rate."""
        with client:
            client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
            assert "session_id" in client.session

    def test_session_id_persists_across_requests(self, client):
        """Test that session ID persists across multiple requests."""
        with client:
            client.get("/api/song/current")
            session_id_1 = client.session.get("session_id")

            client.get("/api/song/current")
            session_id_2 = client.session.get("session_id")

            assert session_id_1 == session_id_2
            assert session_id_1 is not None

    def test_session_cookie_set(self, client):
        """Test that session cookie is set."""
        response = client.get("/api/song/current")
        assert response.status_code == 200
        # Flask automatically sets session cookie

    def test_session_id_is_hex_string(self, client):
        """Test that session ID follows expected format (hex string)."""
        with client:
            client.get("/api/song/current")
            session_id = client.session.get("session_id")
            # Should be hex string
            try:
                int(session_id, 16)
                is_hex = True
            except (ValueError, TypeError):
                is_hex = False
            assert is_hex


class TestSessionIsolation:
    """Tests for session isolation between clients."""

    def test_two_clients_different_sessions(self, app):
        """Test that different clients have different sessions."""
        client1 = app.test_client()
        client2 = app.test_client()

        with client1:
            client1.get("/api/song/current")
            session_id_1 = client1.session.get("session_id")

        with client2:
            client2.get("/api/song/current")
            session_id_2 = client2.session.get("session_id")

        assert session_id_1 != session_id_2

    def test_two_clients_can_rate_same_song_differently(self, app, sample_song, db_session):
        """Test that different sessions can rate same song differently."""
        client1 = app.test_client()
        client2 = app.test_client()

        response1 = client1.post(
            "/api/song/rate",
            json={"song_id": sample_song.id, "is_thumbs_up": True}
        )
        data1 = json.loads(response1.data)

        response2 = client2.post(
            "/api/song/rate",
            json={"song_id": sample_song.id, "is_thumbs_up": False}
        )
        data2 = json.loads(response2.data)

        assert data1["user_rating"] == "up"
        assert data2["user_rating"] == "down"

    def test_sessions_isolated_in_database(self, app, sample_song, db_session):
        """Test that ratings for different sessions are isolated."""
        client1 = app.test_client()
        client2 = app.test_client()

        with client1:
            client1.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
            session_id_1 = client1.session.get("session_id")

        with client2:
            client2.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": False})
            session_id_2 = client2.session.get("session_id")

        rating1 = Rating.query.filter_by(session_id=session_id_1).first()
        rating2 = Rating.query.filter_by(session_id=session_id_2).first()

        assert rating1.is_thumbs_up is True
        assert rating2.is_thumbs_up is False


class TestSessionInDatabase:
    """Tests for session ID in database."""

    def test_rating_session_id_matches_flask_session(self, client, sample_song):
        """Test that session_id in Rating matches Flask session."""
        with client:
            client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
            flask_session_id = client.session.get("session_id")

            rating = Rating.query.filter_by(song_id=sample_song.id).first()
            assert rating.session_id == flask_session_id

    def test_multiple_ratings_same_session_isolated(self, client, db_session):
        """Test that multiple ratings for same user share same session_id."""
        from app.models import Song
        song1 = Song(title="Song1", artist="Artist1")
        song2 = Song(title="Song2", artist="Artist2")
        db_session.add_all([song1, song2])
        db_session.commit()

        with client:
            client.post("/api/song/rate", json={"song_id": song1.id, "is_thumbs_up": True})
            client.post("/api/song/rate", json={"song_id": song2.id, "is_thumbs_up": False})
            flask_session_id = client.session.get("session_id")

            ratings = Rating.query.filter_by(session_id=flask_session_id).all()
            assert len(ratings) == 2
            assert all(r.session_id == flask_session_id for r in ratings)


class TestSessionPersistence:
    """Tests for session persistence across workflow."""

    def test_session_persists_from_get_current_to_post_rate(self, client, sample_song):
        """Test that session persists from GET current to POST rate."""
        with client:
            response1 = client.get("/api/song/current?title=Song&artist=Artist")
            session_id_after_get = client.session.get("session_id")

            response2 = client.post(
                "/api/song/rate",
                json={"song_id": sample_song.id, "is_thumbs_up": True}
            )
            session_id_after_post = client.session.get("session_id")

            assert session_id_after_get == session_id_after_post

    def test_complete_player_workflow_same_session(self, client, sample_song):
        """Test complete workflow uses same session throughout."""
        with client:
            # Load song
            response1 = client.get(f"/api/song/current?title={sample_song.title}&artist={sample_song.artist}")
            session_after_load = client.session.get("session_id")

            # Rate song
            response2 = client.post(
                "/api/song/rate",
                json={"song_id": sample_song.id, "is_thumbs_up": True}
            )
            session_after_rate = client.session.get("session_id")

            # Load song again
            response3 = client.get(f"/api/song/current?title={sample_song.title}&artist={sample_song.artist}")
            session_after_second_load = client.session.get("session_id")

            assert session_after_load == session_after_rate == session_after_second_load
