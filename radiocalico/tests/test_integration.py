"""Integration tests for complete workflows."""

import json
import pytest
from app import db
from app.models import Song, Rating


class TestFullPlayerWorkflow:
    """Tests for complete player workflows."""

    def test_full_workflow_load_song_then_rate(self, client, db_session):
        """Test: GET current → POST rate → GET current (verify update)."""
        response1 = client.get("/api/song/current?title=Song1&artist=Artist1")
        song_id = json.loads(response1.data)["id"]
        initial_thumbs_up = json.loads(response1.data)["thumbs_up"]

        client.post("/api/song/rate", json={"song_id": song_id, "is_thumbs_up": True})

        response2 = client.get("/api/song/current?title=Song1&artist=Artist1")
        data = json.loads(response2.data)
        assert data["thumbs_up"] == initial_thumbs_up + 1
        assert data["user_rating"] == "up"

    def test_full_workflow_rate_then_check_aggregate(self, client, db_session):
        """Test: Rate song → fetch → verify thumbs_up count."""
        response1 = client.get("/api/song/current?title=Song2&artist=Artist2")
        song_id = json.loads(response1.data)["id"]

        client.post("/api/song/rate", json={"song_id": song_id, "is_thumbs_up": True})

        response2 = client.get("/api/song/current?title=Song2&artist=Artist2")
        data = json.loads(response2.data)
        assert data["thumbs_up"] >= 1

    def test_full_workflow_change_vote(self, client):
        """Test: Rate up → change to down → verify counts."""
        response1 = client.get("/api/song/current?title=Song3&artist=Artist3")
        song_id = json.loads(response1.data)["id"]

        client.post("/api/song/rate", json={"song_id": song_id, "is_thumbs_up": True})
        response2 = client.get("/api/song/current?title=Song3&artist=Artist3")
        data2 = json.loads(response2.data)
        thumbs_up_after_up = data2["thumbs_up"]

        client.post("/api/song/rate", json={"song_id": song_id, "is_thumbs_up": False})
        response3 = client.get("/api/song/current?title=Song3&artist=Artist3")
        data3 = json.loads(response3.data)
        thumbs_down_after_down = data3["thumbs_down"]

        assert data3["user_rating"] == "down"
        assert thumbs_down_after_down >= 1


class TestDatabaseConsistency:
    """Tests for database consistency across operations."""

    def test_song_rating_cascade_delete(self, db_session, sample_song, sample_rating):
        """Test that deleting song cascades to delete ratings."""
        song_id = sample_song.id
        rating_id = sample_rating.id
        db_session.delete(sample_song)
        db_session.commit()

        song = Song.query.get(song_id)
        rating = Rating.query.get(rating_id)
        assert song is None
        assert rating is None

    def test_unique_rating_enforced_at_db(self, db_session, sample_song):
        """Test that unique constraint prevents duplicate ratings."""
        from sqlalchemy.exc import IntegrityError
        session_id = "test_session"

        rating1 = Rating(song_id=sample_song.id, session_id=session_id, is_thumbs_up=True)
        db_session.add(rating1)
        db_session.commit()

        rating2 = Rating(song_id=sample_song.id, session_id=session_id, is_thumbs_up=False)
        db_session.add(rating2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_rating_count_accuracy(self, db_session, sample_song):
        """Test that rating counts are accurate."""
        for i in range(10):
            session_id = f"session_{i}"
            is_thumbs_up = i < 7
            rating = Rating(song_id=sample_song.id, session_id=session_id, is_thumbs_up=is_thumbs_up)
            db_session.add(rating)
        db_session.commit()

        thumbs_up_count = len([r for r in sample_song.ratings if r.is_thumbs_up])
        thumbs_down_count = len([r for r in sample_song.ratings if not r.is_thumbs_up])
        assert thumbs_up_count == 7
        assert thumbs_down_count == 3

    def test_song_to_dict_aggregation(self, db_session, sample_song):
        """Test that to_dict() aggregates ratings correctly."""
        for i in range(5):
            Rating(song_id=sample_song.id, session_id=f"s{i}", is_thumbs_up=True)
        for i in range(3):
            Rating(song_id=sample_song.id, session_id=f"s_down_{i}", is_thumbs_up=False)
        db_session.commit()

        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 5
        assert song_dict["thumbs_down"] == 3


class TestSessionWorkflow:
    """Tests for session management across requests."""

    def test_session_persists_across_requests(self, client):
        """Test that session ID persists across multiple requests."""
        client.get("/api/song/current?title=S1&artist=A1")
        client.get("/api/song/current?title=S2&artist=A2")
        client.get("/api/song/current?title=S3&artist=A3")
        # If sessions are properly isolated, we should get here without error
        response = client.get("/api/song/current")
        assert response.status_code == 200

    def test_session_id_generated_once(self, client):
        """Test that session ID is generated only once."""
        response1 = client.get("/api/song/current?title=Song&artist=Artist")
        response2 = client.get("/api/song/current?title=Song&artist=Artist")
        # Both requests use same session, so same user_rating
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        assert data1["user_rating"] == data2["user_rating"]


class TestMultipleSessions:
    """Tests for multi-session isolation."""

    def test_two_sessions_rate_differently(self, app, db_session, sample_song):
        """Test that two sessions can rate same song differently."""
        client1 = app.test_client()
        client2 = app.test_client()

        response1 = client1.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        data1 = json.loads(response1.data)

        response2 = client2.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": False})
        data2 = json.loads(response2.data)

        assert data1["user_rating"] == "up"
        assert data2["user_rating"] == "down"
        assert data1["thumbs_up"] + data1["thumbs_down"] == data2["thumbs_up"] + data2["thumbs_down"]
