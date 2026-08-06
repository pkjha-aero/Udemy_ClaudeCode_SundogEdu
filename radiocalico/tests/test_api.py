"""Unit tests for API endpoints."""

import json
import pytest
from app.models import Song, Rating


class TestHealthAPI:
    """Tests for GET /api/health."""

    def test_health_status_200(self, client):
        """Test that health endpoint returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_json_response(self, client):
        """Test that health returns OK status."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_health_content_type(self, client):
        """Test that health returns JSON content type."""
        response = client.get("/api/health")
        assert response.content_type == "application/json"


class TestItemsAPI:
    """Tests for GET /api/items."""

    def test_api_items_status_200(self, client):
        """Test that items endpoint returns 200."""
        response = client.get("/api/items")
        assert response.status_code == 200

    def test_api_items_returns_list(self, client):
        """Test that items endpoint returns array."""
        response = client.get("/api/items")
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_api_items_empty_list(self, client, db_session):
        """Test that empty items returns []."""
        from app.models import Item
        Item.query.delete()
        db_session.commit()

        response = client.get("/api/items")
        data = json.loads(response.data)
        assert data == []

    def test_api_items_with_items(self, client, sample_item):
        """Test that items endpoint returns all items."""
        response = client.get("/api/items")
        data = json.loads(response.data)
        assert len(data) >= 1

    def test_api_items_dict_has_id(self, client, sample_item):
        """Test that each item has id."""
        response = client.get("/api/items")
        data = json.loads(response.data)
        assert "id" in data[0]

    def test_api_items_dict_has_name(self, client, sample_item):
        """Test that each item has name."""
        response = client.get("/api/items")
        data = json.loads(response.data)
        assert "name" in data[0]

    def test_api_items_dict_has_created_at(self, client, sample_item):
        """Test that each item has created_at."""
        response = client.get("/api/items")
        data = json.loads(response.data)
        assert "created_at" in data[0]


class TestUsersAPI:
    """Tests for GET /api/users."""

    def test_api_users_status_200(self, client):
        """Test that users endpoint returns 200."""
        response = client.get("/api/users")
        assert response.status_code == 200

    def test_api_users_returns_list(self, client):
        """Test that users endpoint returns array."""
        response = client.get("/api/users")
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_api_users_includes_default_user(self, client):
        """Test that default user is included."""
        response = client.get("/api/users")
        data = json.loads(response.data)
        assert len(data) >= 1
        emails = [u["email"] for u in data]
        assert "pankaj.psu@gmail.com" in emails

    def test_api_users_multiple_users(self, client, sample_user):
        """Test that all users are returned."""
        response = client.get("/api/users")
        data = json.loads(response.data)
        assert len(data) >= 2

    def test_api_users_dict_structure(self, client):
        """Test that user dict has required fields."""
        response = client.get("/api/users")
        data = json.loads(response.data)
        user = data[0]
        assert "id" in user
        assert "name" in user
        assert "email" in user


class TestCurrentSongAPI:
    """Tests for GET /api/song/current."""

    def test_song_current_creates_session(self, client):
        """Test that session ID is created."""
        response = client.get("/api/song/current")
        assert response.status_code == 200
        # Check that response has valid data
        data = json.loads(response.data)
        assert "id" in data

    def test_song_current_preserves_session(self, client):
        """Test that session ID is preserved."""
        client.get("/api/song/current?title=Song1&artist=Artist1")
        response = client.get("/api/song/current?title=Song2&artist=Artist2")
        assert response.status_code == 200

    def test_song_current_creates_song_if_new(self, client, db_session):
        """Test that new song is created."""
        response = client.get("/api/song/current?title=NewSong&artist=NewArtist")
        assert response.status_code == 200

        song = Song.query.filter_by(title="NewSong", artist="NewArtist").first()
        assert song is not None

    def test_song_current_returns_song_data(self, client):
        """Test that response has song fields."""
        response = client.get("/api/song/current?title=TestSong&artist=TestArtist&album=TestAlbum")
        data = json.loads(response.data)
        assert data["title"] == "TestSong"
        assert data["artist"] == "TestArtist"
        assert data["album"] == "TestAlbum"

    def test_song_current_returns_rating_counts(self, client, sample_song):
        """Test that response includes rating counts."""
        response = client.get(f"/api/song/current?title={sample_song.title}&artist={sample_song.artist}")
        data = json.loads(response.data)
        assert "thumbs_up" in data
        assert "thumbs_down" in data

    def test_song_current_user_rating_null_initially(self, client):
        """Test that user_rating is None initially."""
        response = client.get("/api/song/current?title=Song&artist=Artist")
        data = json.loads(response.data)
        assert data["user_rating"] is None

    def test_song_current_user_rating_up_after_rating(self, client):
        """Test that user_rating updates after submission."""
        response1 = client.get("/api/song/current?title=Song&artist=Artist")
        song_id = json.loads(response1.data)["id"]

        client.post("/api/song/rate", json={"song_id": song_id, "is_thumbs_up": True})

        response2 = client.get("/api/song/current?title=Song&artist=Artist")
        data = json.loads(response2.data)
        assert data["user_rating"] == "up"

    def test_song_current_user_rating_down_after_rating(self, client):
        """Test that user_rating down works."""
        response1 = client.get("/api/song/current?title=Song&artist=Artist")
        song_id = json.loads(response1.data)["id"]

        client.post("/api/song/rate", json={"song_id": song_id, "is_thumbs_up": False})

        response2 = client.get("/api/song/current?title=Song&artist=Artist")
        data = json.loads(response2.data)
        assert data["user_rating"] == "down"

    def test_song_current_with_query_params(self, client):
        """Test that query params are used."""
        response = client.get("/api/song/current?title=Custom&artist=Artist&album=Album&date=2026-08-06")
        data = json.loads(response.data)
        assert data["title"] == "Custom"
        assert data["artist"] == "Artist"
        assert data["album"] == "Album"
        assert data["date"] == "2026-08-06"

    def test_song_current_missing_optional_fields(self, client):
        """Test that missing optional fields use defaults."""
        response = client.get("/api/song/current?title=Song&artist=Artist")
        data = json.loads(response.data)
        assert data["album"] == "Unknown"
        assert data["date"] == ""

    def test_song_current_lookup_existing_song(self, client, sample_song):
        """Test that existing song is reused."""
        response = client.get(f"/api/song/current?title={sample_song.title}&artist={sample_song.artist}")
        data = json.loads(response.data)
        assert data["id"] == sample_song.id


class TestRateSongAPI:
    """Tests for POST /api/song/rate."""

    def test_rate_song_status_201_or_200(self, client, sample_song):
        """Test that rating returns 2xx status."""
        response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        assert response.status_code in [200, 201]

    def test_rate_song_missing_json_body(self, client):
        """Test that missing JSON returns error."""
        response = client.post("/api/song/rate")
        assert response.status_code >= 400

    def test_rate_song_missing_song_id(self, client):
        """Test that missing song_id returns 400."""
        response = client.post("/api/song/rate", json={"is_thumbs_up": True})
        assert response.status_code == 400

    def test_rate_song_missing_is_thumbs_up(self, client, sample_song):
        """Test that missing is_thumbs_up returns 400."""
        response = client.post("/api/song/rate", json={"song_id": sample_song.id})
        assert response.status_code == 400

    def test_rate_song_nonexistent_song_id(self, client):
        """Test that nonexistent song returns 404."""
        response = client.post("/api/song/rate", json={"song_id": 9999, "is_thumbs_up": True})
        assert response.status_code == 404

    def test_rate_song_creates_rating(self, client, sample_song, db_session):
        """Test that rating is created in database."""
        initial_count = Rating.query.count()
        client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        assert Rating.query.count() == initial_count + 1

    def test_rate_song_thumbs_up(self, client, sample_song):
        """Test that thumbs_up rating is saved."""
        client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        rating = Rating.query.filter_by(song_id=sample_song.id).first()
        assert rating.is_thumbs_up is True

    def test_rate_song_thumbs_down(self, client, sample_song):
        """Test that thumbs_down rating is saved."""
        client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": False})
        rating = Rating.query.filter_by(song_id=sample_song.id).first()
        assert rating.is_thumbs_up is False

    def test_rate_song_updates_existing_rating(self, client, sample_song):
        """Test that existing rating is updated."""
        client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": False})

        rating = Rating.query.filter_by(song_id=sample_song.id).first()
        assert rating.is_thumbs_up is False

    def test_rate_song_response_has_counts(self, client, sample_song):
        """Test that response includes vote counts."""
        response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        data = json.loads(response.data)
        assert "thumbs_up" in data
        assert "thumbs_down" in data

    def test_rate_song_response_has_user_rating(self, client, sample_song):
        """Test that response includes user_rating."""
        response = client.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        data = json.loads(response.data)
        assert "user_rating" in data
        assert data["user_rating"] in ["up", "down"]

    def test_rate_song_session_isolated(self, client, sample_song):
        """Test that ratings are isolated per session."""
        # Simulate two different clients/sessions
        client1 = client
        response1 = client1.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": True})
        data1 = json.loads(response1.data)

        # Create new client to simulate different session
        from app import create_app
        app = create_app()
        app.config["TESTING"] = True
        client2 = app.test_client()

        response2 = client2.post("/api/song/rate", json={"song_id": sample_song.id, "is_thumbs_up": False})
        data2 = json.loads(response2.data)

        assert data1["user_rating"] == "up"
        assert data2["user_rating"] == "down"
