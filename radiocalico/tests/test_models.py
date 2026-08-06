"""Unit tests for Radio Calico ORM models."""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Item, Song, Rating


class TestUserModel:
    """User model tests."""

    def test_user_create(self, db_session):
        """Test creating a user."""
        user = User(name="Alice", email="alice@example.com")
        db_session.add(user)
        db_session.commit()
        assert user.id is not None
        assert user.name == "Alice"
        assert user.email == "alice@example.com"

    def test_user_email_unique(self, db_session, sample_user):
        """Test that email uniqueness constraint is enforced."""
        user = User(name="Different", email=sample_user.email)
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_to_dict(self, db_session, sample_user):
        """Test user serialization to dict."""
        user_dict = sample_user.to_dict()
        assert user_dict["id"] == sample_user.id
        assert user_dict["name"] == sample_user.name
        assert user_dict["email"] == sample_user.email

    def test_user_query_by_id(self, db_session, sample_user):
        """Test retrieving user by ID."""
        user = User.query.get(sample_user.id)
        assert user.name == sample_user.name
        assert user.email == sample_user.email

    def test_user_query_by_email(self, db_session, sample_user):
        """Test retrieving user by email."""
        user = User.query.filter_by(email=sample_user.email).first()
        assert user.id == sample_user.id

    def test_user_update(self, db_session, sample_user):
        """Test updating user."""
        sample_user.name = "Updated Name"
        db_session.commit()
        user = User.query.get(sample_user.id)
        assert user.name == "Updated Name"

    def test_user_delete(self, db_session, sample_user):
        """Test deleting a user."""
        user_id = sample_user.id
        db_session.delete(sample_user)
        db_session.commit()
        user = User.query.get(user_id)
        assert user is None


class TestItemModel:
    """Item model tests."""

    def test_item_create(self, db_session):
        """Test creating an item."""
        item = Item(name="Test Item")
        db_session.add(item)
        db_session.commit()
        assert item.id is not None
        assert item.name == "Test Item"

    def test_item_created_at_auto(self, db_session):
        """Test that created_at is auto-set."""
        item = Item(name="Test Item")
        db_session.add(item)
        db_session.commit()
        assert item.created_at is not None
        assert isinstance(item.created_at, datetime)

    def test_item_to_dict(self, db_session, sample_item):
        """Test item serialization to dict."""
        item_dict = sample_item.to_dict()
        assert item_dict["id"] == sample_item.id
        assert item_dict["name"] == sample_item.name
        assert "created_at" in item_dict

    def test_item_query_by_id(self, db_session, sample_item):
        """Test retrieving item by ID."""
        item = Item.query.get(sample_item.id)
        assert item.name == sample_item.name

    def test_item_query_all(self, db_session, sample_item):
        """Test retrieving all items."""
        items = Item.query.all()
        assert len(items) >= 1
        assert sample_item in items


class TestSongModel:
    """Song model tests."""

    def test_song_create(self, db_session):
        """Test creating a song."""
        song = Song(
            title="Song Title",
            artist="Artist Name",
            album="Album Name",
            date="2026-08-06",
            bit_depth=24,
            sample_rate=48000
        )
        db_session.add(song)
        db_session.commit()
        assert song.id is not None
        assert song.title == "Song Title"
        assert song.artist == "Artist Name"

    def test_song_to_dict_empty_ratings(self, db_session, sample_song):
        """Test song serialization with no ratings."""
        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 0
        assert song_dict["thumbs_down"] == 0

    def test_song_to_dict_with_ratings(self, db_session, sample_song):
        """Test song serialization with ratings."""
        Rating(song_id=sample_song.id, session_id="session1", is_thumbs_up=True)
        Rating(song_id=sample_song.id, session_id="session2", is_thumbs_up=True)
        Rating(song_id=sample_song.id, session_id="session3", is_thumbs_up=False)
        db_session.commit()

        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 2
        assert song_dict["thumbs_down"] == 1

    def test_song_query_by_title_artist(self, db_session, sample_song):
        """Test looking up song by title and artist."""
        song = Song.query.filter_by(
            title=sample_song.title,
            artist=sample_song.artist
        ).first()
        assert song.id == sample_song.id

    def test_song_cascade_delete(self, db_session, sample_song, sample_rating):
        """Test that deleting song cascades to ratings."""
        song_id = sample_song.id
        rating_id = sample_rating.id
        db_session.delete(sample_song)
        db_session.commit()

        song = Song.query.get(song_id)
        rating = Rating.query.get(rating_id)
        assert song is None
        assert rating is None

    def test_song_ratings_relationship(self, db_session, sample_song):
        """Test accessing ratings through song relationship."""
        rating1 = Rating(song_id=sample_song.id, session_id="s1", is_thumbs_up=True)
        rating2 = Rating(song_id=sample_song.id, session_id="s2", is_thumbs_up=False)
        db_session.add_all([rating1, rating2])
        db_session.commit()

        assert len(sample_song.ratings) == 2
        assert rating1 in sample_song.ratings
        assert rating2 in sample_song.ratings


class TestRatingModel:
    """Rating model tests."""

    def test_rating_create_thumbs_up(self, db_session, sample_song):
        """Test creating a thumbs-up rating."""
        rating = Rating(song_id=sample_song.id, session_id="sess1", is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()
        assert rating.id is not None
        assert rating.is_thumbs_up is True

    def test_rating_create_thumbs_down(self, db_session, sample_song):
        """Test creating a thumbs-down rating."""
        rating = Rating(song_id=sample_song.id, session_id="sess1", is_thumbs_up=False)
        db_session.add(rating)
        db_session.commit()
        assert rating.is_thumbs_up is False

    def test_rating_unique_constraint(self, db_session, sample_song):
        """Test that one rating per song+session is enforced."""
        rating1 = Rating(song_id=sample_song.id, session_id="sess1", is_thumbs_up=True)
        db_session.add(rating1)
        db_session.commit()

        rating2 = Rating(song_id=sample_song.id, session_id="sess1", is_thumbs_up=False)
        db_session.add(rating2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_rating_session_id_required(self, db_session, sample_song):
        """Test that session_id is required."""
        rating = Rating(song_id=sample_song.id, session_id=None, is_thumbs_up=True)
        db_session.add(rating)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_rating_song_id_required(self, db_session):
        """Test that song_id is required."""
        rating = Rating(song_id=None, session_id="sess1", is_thumbs_up=True)
        db_session.add(rating)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_rating_created_at_auto(self, db_session, sample_rating):
        """Test that created_at is auto-set."""
        assert sample_rating.created_at is not None
        assert isinstance(sample_rating.created_at, datetime)

    def test_rating_query_by_song_session(self, db_session, sample_song):
        """Test looking up rating by song_id and session_id."""
        rating = Rating(song_id=sample_song.id, session_id="sess1", is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()

        found = Rating.query.filter_by(
            song_id=sample_song.id,
            session_id="sess1"
        ).first()
        assert found.id == rating.id

    def test_rating_update_thumbs(self, db_session, sample_rating):
        """Test updating a rating from up to down."""
        original_id = sample_rating.id
        sample_rating.is_thumbs_up = False
        db_session.commit()

        rating = Rating.query.get(original_id)
        assert rating.is_thumbs_up is False
        assert rating.id == original_id

    def test_rating_to_dict(self, db_session, sample_rating):
        """Test rating serialization to dict."""
        rating_dict = sample_rating.to_dict()
        assert rating_dict["song_id"] == sample_rating.song_id
        assert rating_dict["session_id"] == sample_rating.session_id
        assert rating_dict["is_thumbs_up"] == sample_rating.is_thumbs_up
