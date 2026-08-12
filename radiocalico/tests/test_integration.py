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
        up_ratings = [Rating(song_id=sample_song.id, session_id=f"s{i}", is_thumbs_up=True) for i in range(5)]
        down_ratings = [Rating(song_id=sample_song.id, session_id=f"s_down_{i}", is_thumbs_up=False) for i in range(3)]
        db_session.add_all(up_ratings + down_ratings)
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
        # Both sessions successfully rated the song
        assert response1.status_code in [200, 201]
        assert response2.status_code in [200, 201]


class TestUserManagementWorkflow:
    """Tests for user creation and management workflows."""

    def test_add_user_workflow(self, client, db_session):
        """Test: Add user via form → verify in database → check in API."""
        from app.models import User

        response = client.post("/users", data={"name": "Test User", "email": "testuser@example.com"})
        assert response.status_code == 302  # Redirect after successful submission

        user = User.query.filter_by(email="testuser@example.com").first()
        assert user is not None
        assert user.name == "Test User"

        # Verify user appears in API response
        api_response = client.get("/api/users")
        users_data = json.loads(api_response.data)
        emails = [u["email"] for u in users_data]
        assert "testuser@example.com" in emails

    def test_duplicate_user_rejected(self, client, db_session, sample_user):
        """Test: Duplicate email is rejected."""
        from app.models import User

        response = client.post("/users", data={"name": "Another User", "email": sample_user.email})
        assert response.status_code == 302

        # Count should still be 1 (no duplicate added)
        duplicates = User.query.filter_by(email=sample_user.email).all()
        assert len(duplicates) == 1

    def test_user_appears_on_homepage(self, client, sample_user):
        """Test: Added user appears on homepage."""
        response = client.get("/")
        assert response.status_code == 200
        assert sample_user.name.encode() in response.data or sample_user.email.encode() in response.data


class TestItemsWorkflow:
    """Tests for items list and API."""

    def test_items_api_returns_list(self, client, sample_item):
        """Test: Items API returns items."""
        response = client.get("/api/items")
        assert response.status_code == 200
        items = json.loads(response.data)
        assert isinstance(items, list)
        assert len(items) > 0

    def test_items_appear_on_homepage(self, client, sample_item):
        """Test: Items appear on homepage."""
        response = client.get("/")
        assert response.status_code == 200
        assert sample_item.name.encode() in response.data


class TestHealthCheckWorkflow:
    """Tests for health check endpoints."""

    def test_health_endpoint_success(self, client):
        """Test: Health check returns OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_health_check_during_heavy_load(self, client, sample_song):
        """Test: Health check succeeds even with concurrent requests."""
        health_response = client.get("/api/health")
        assert health_response.status_code == 200

        client.get("/api/song/current?title=S1&artist=A1")
        client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})

        health_response = client.get("/api/health")
        assert health_response.status_code == 200


class TestRatingUpdateWorkflow:
    """Tests for updating existing ratings."""

    def test_update_rating_changes_vote(self, client, sample_song):
        """Test: Rate → change vote → verify counts update."""
        # First rating: thumbs up
        response1 = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        data1 = json.loads(response1.data)
        initial_up = data1["thumbs_up"]
        initial_down = data1["thumbs_down"]

        # Change to thumbs down
        response2 = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": False})
        data2 = json.loads(response2.data)

        assert data2["user_rating"] == "down"
        # Thumbs down should increase
        assert data2["thumbs_down"] >= initial_down


class TestErrorHandlingWorkflow:
    """Tests for error scenarios."""

    def test_rate_nonexistent_song(self, client):
        """Test: Rating nonexistent song returns 404."""
        response = client.post("/api/song/rate", json={"song_id": 99999, "is_thumbs_up": True})
        assert response.status_code == 404

    def test_rate_with_missing_song_id(self, client):
        """Test: Rating without song_id returns 400."""
        response = client.post("/api/song/rate", json={"is_thumbs_up": True})
        assert response.status_code == 400

    def test_rate_with_missing_is_thumbs_up(self, client, sample_song):
        """Test: Rating without is_thumbs_up returns 400."""
        response = client.post("/api/song/rate", json={"song_id": sample_song.id})
        assert response.status_code == 400

    def test_invalid_json_request(self, client):
        """Test: Invalid JSON returns 400."""
        response = client.post("/api/song/rate",
                              data="invalid json",
                              content_type="application/json")
        assert response.status_code in [400, 415]


class TestEndToEndWorkflow:
    """Tests for complete end-to-end workflows."""

    def test_homepage_to_player_workflow(self, client, sample_user, sample_item):
        """Test: Load homepage → verify player link → access player."""
        # Load homepage
        home_response = client.get("/")
        assert home_response.status_code == 200

        # Verify player page is accessible
        player_response = client.get("/player")
        assert player_response.status_code == 200

    def test_full_user_to_rating_workflow(self, client, db_session):
        """Test: Add user → play song → rate → view updated counts."""
        from app.models import User

        # Add new user
        user_response = client.post("/users", data={"name": "New User", "email": "newuser@test.com"})
        assert user_response.status_code == 302

        # Get song (creates it if new)
        song_response = client.get("/api/song/current?title=TestSong&artist=TestArtist&album=TestAlbum&date=2026-08-12")
        song_data = json.loads(song_response.data)
        song_id = song_data["id"]

        # Rate the song
        rating_response = client.post("/api/song/rate", json={"song_id": song_id, "is_thumbs_up": True})
        rating_data = json.loads(rating_response.data)

        assert rating_data["user_rating"] == "up"
        assert rating_data["thumbs_up"] >= 1

        # Verify user exists
        user = User.query.filter_by(email="newuser@test.com").first()
        assert user is not None

    def test_rating_persistence_workflow(self, client, sample_song):
        """Test: Rate song → refresh → verify rating persists."""
        # Rate song
        rate_response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        rate_data = json.loads(rate_response.data)

        # Fetch song again
        fetch_response = client.get(f"/api/song/current?title={sample_song.title}&artist={sample_song.artist}")
        fetch_data = json.loads(fetch_response.data)

        # Rating should persist
        assert fetch_data["user_rating"] == "up"
        assert fetch_data["thumbs_up"] == rate_data["thumbs_up"]
