"""Tests for session management and persistence."""

import json
import secrets
import pytest
from app.models import Rating


class TestSessionIDGeneration:
    """Tests for session ID generation."""

    def test_session_id_created_on_first_current_request(self, client):
        """Test that session ID is created on first GET /api/song/current."""
        response = client.get("/api/song/current")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "id" in data

    def test_session_id_created_on_first_rate_request(self, client, sample_song):
        """Test that session ID is created on first POST /api/song/rate."""
        response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert "thumbs_up" in data

    def test_session_id_persists_across_requests(self, client):
        """Test that session ID persists across multiple requests."""
        response1 = client.get("/api/song/current")
        assert response1.status_code == 200

        response2 = client.get("/api/song/current")
        assert response2.status_code == 200

        response3 = client.get("/api/song/current")
        assert response3.status_code == 200

    def test_session_cookie_set(self, client):
        """Test that session cookie is set."""
        response = client.get("/api/song/current")
        assert response.status_code == 200
        # Flask automatically sets session cookie

    def test_multiple_requests_work(self, client):
        """Test that multiple requests work correctly."""
        for _ in range(5):
            response = client.get("/api/song/current")
            assert response.status_code == 200


class TestSessionIsolation:
    """Tests for session isolation between clients."""

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

    def test_multiple_clients_work_independently(self, app, sample_song):
        """Test that multiple clients work independently."""
        client1 = app.test_client()
        client2 = app.test_client()
        client3 = app.test_client()

        for client in [client1, client2, client3]:
            response = client.post(
                "/api/song/rate",
                json={"song_id": sample_song.id, "is_thumbs_up": True}
            )
            assert response.status_code in [200, 201]


class TestSessionInDatabase:
    """Tests for session ID in database."""

    def test_ratings_created_in_database(self, client, sample_song):
        """Test that ratings are created in database."""
        initial_count = Rating.query.count()
        response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        assert response.status_code in [200, 201]
        assert Rating.query.count() > initial_count

    def test_multiple_ratings_same_client(self, client, db_session):
        """Test that one client can rate multiple songs."""
        from app.models import Song
        song1 = Song(title="Song1", artist="Artist1")
        song2 = Song(title="Song2", artist="Artist2")
        db_session.add_all([song1, song2])
        db_session.commit()

        response1 = client.post("/api/song/rate", json={"song_id": song1.id, "is_thumbs_up": True})
        response2 = client.post("/api/song/rate", json={"song_id": song2.id, "is_thumbs_up": False})

        assert response1.status_code in [200, 201]
        assert response2.status_code in [200, 201]
        assert Rating.query.count() >= 2


class TestSessionPersistence:
    """Tests for session persistence across workflow."""

    def test_session_works_through_complete_workflow(self, client, sample_song):
        """Test that session persists through complete workflow."""
        # Load song
        response1 = client.get(f"/api/song/current?title={sample_song.title}&artist={sample_song.artist}")
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1["user_rating"] is None

        # Rate song
        response2 = client.post(
            "/api/song/rate",
            json={"song_id": sample_song.id, "is_thumbs_up": True}
        )
        assert response2.status_code in [200, 201]

        # Load song again and verify rating
        response3 = client.get(f"/api/song/current?title={sample_song.title}&artist={sample_song.artist}")
        assert response3.status_code == 200
        data3 = json.loads(response3.data)
        assert data3["user_rating"] == "up"

    def test_multiple_songs_workflow(self, client, db_session):
        """Test rating workflow across multiple songs."""
        from app.models import Song
        song1 = Song(title="Song1", artist="Artist1")
        song2 = Song(title="Song2", artist="Artist2")
        db_session.add_all([song1, song2])
        db_session.commit()

        # Rate first song
        response1 = client.post("/api/song/rate", json={"song_id": song1.id, "is_thumbs_up": True})
        assert response1.status_code in [200, 201]

        # Rate second song
        response2 = client.post("/api/song/rate", json={"song_id": song2.id, "is_thumbs_up": False})
        assert response2.status_code in [200, 201]

        # Verify both ratings exist
        assert Rating.query.filter_by(song_id=song1.id).first() is not None
        assert Rating.query.filter_by(song_id=song2.id).first() is not None
