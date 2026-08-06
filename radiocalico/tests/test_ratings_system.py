"""Tests specific to the ratings system constraints and functionality."""

import pytest
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Song, Rating


class TestRatingUniquenessConstraint:
    """Tests for the unique constraint on (song_id, session_id)."""

    def test_rating_unique_constraint_enforced(self, db_session, sample_song):
        """Test that UniqueConstraint(song_id, session_id) is enforced."""
        session_id = "unique_session"
        rating1 = Rating(song_id=sample_song.id, session_id=session_id, is_thumbs_up=True)
        db_session.add(rating1)
        db_session.commit()

        rating2 = Rating(song_id=sample_song.id, session_id=session_id, is_thumbs_up=False)
        db_session.add(rating2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_rating_same_song_different_sessions_allowed(self, db_session, sample_song):
        """Test that same song can be rated by different sessions."""
        rating1 = Rating(song_id=sample_song.id, session_id="session1", is_thumbs_up=True)
        rating2 = Rating(song_id=sample_song.id, session_id="session2", is_thumbs_up=False)
        db_session.add_all([rating1, rating2])
        db_session.commit()

        assert len(sample_song.ratings) == 2

    def test_rating_same_session_different_songs_allowed(self, db_session, sample_song):
        """Test that same session can rate different songs."""
        song2 = Song(title="Song2", artist="Artist2")
        db_session.add(song2)
        db_session.commit()

        rating1 = Rating(song_id=sample_song.id, session_id="session1", is_thumbs_up=True)
        rating2 = Rating(song_id=song2.id, session_id="session1", is_thumbs_up=False)
        db_session.add_all([rating1, rating2])
        db_session.commit()

        assert Rating.query.filter_by(session_id="session1").count() == 2


class TestRatingUpdates:
    """Tests for updating ratings."""

    def test_rating_update_thumbs_up_to_down(self, db_session, sample_rating):
        """Test changing vote from up to down."""
        original_id = sample_rating.id
        sample_rating.is_thumbs_up = False
        db_session.commit()

        rating = Rating.query.get(original_id)
        assert rating.is_thumbs_up is False
        assert rating.id == original_id

    def test_rating_update_down_to_up(self, db_session, sample_song):
        """Test changing vote from down to up."""
        rating = Rating(song_id=sample_song.id, session_id="sess", is_thumbs_up=False)
        db_session.add(rating)
        db_session.commit()

        rating.is_thumbs_up = True
        db_session.commit()

        updated = Rating.query.get(rating.id)
        assert updated.is_thumbs_up is True

    def test_rating_update_preserves_id(self, db_session, sample_rating):
        """Test that ID is preserved after update."""
        original_id = sample_rating.id
        sample_rating.is_thumbs_up = not sample_rating.is_thumbs_up
        db_session.commit()

        assert sample_rating.id == original_id


class TestVoteCountingEdgeCases:
    """Tests for vote counting edge cases."""

    def test_zero_ratings_returns_0_0(self, db_session, sample_song):
        """Test that new song has 0 up and 0 down."""
        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 0
        assert song_dict["thumbs_down"] == 0

    def test_only_thumbs_up(self, db_session, sample_song):
        """Test counting with only up votes."""
        for i in range(5):
            rating = Rating(song_id=sample_song.id, session_id=f"s{i}", is_thumbs_up=True)
            db_session.add(rating)
        db_session.commit()

        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 5
        assert song_dict["thumbs_down"] == 0

    def test_only_thumbs_down(self, db_session, sample_song):
        """Test counting with only down votes."""
        for i in range(5):
            rating = Rating(song_id=sample_song.id, session_id=f"s{i}", is_thumbs_up=False)
            db_session.add(rating)
        db_session.commit()

        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 0
        assert song_dict["thumbs_down"] == 5

    def test_mixed_ratings_counts_correct(self, db_session, sample_song):
        """Test counting with mixed votes (7 up, 3 down)."""
        for i in range(7):
            rating = Rating(song_id=sample_song.id, session_id=f"up{i}", is_thumbs_up=True)
            db_session.add(rating)
        for i in range(3):
            rating = Rating(song_id=sample_song.id, session_id=f"down{i}", is_thumbs_up=False)
            db_session.add(rating)
        db_session.commit()

        song_dict = sample_song.to_dict()
        assert song_dict["thumbs_up"] == 7
        assert song_dict["thumbs_down"] == 3

    def test_changing_rating_updates_counts(self, db_session, sample_song):
        """Test that changing vote updates counts."""
        rating = Rating(song_id=sample_song.id, session_id="change", is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()

        data1 = sample_song.to_dict()
        assert data1["thumbs_up"] == 1
        assert data1["thumbs_down"] == 0

        rating.is_thumbs_up = False
        db_session.commit()

        data2 = sample_song.to_dict()
        assert data2["thumbs_up"] == 0
        assert data2["thumbs_down"] == 1


class TestSessionIDHandling:
    """Tests for session ID handling in ratings."""

    def test_session_id_type_string(self, db_session, sample_song):
        """Test that session_id is stored as string."""
        rating = Rating(song_id=sample_song.id, session_id="test_session", is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()

        assert isinstance(rating.session_id, str)
        assert rating.session_id == "test_session"

    def test_session_id_minimum_length(self, db_session, sample_song):
        """Test that session_id follows expected format."""
        session_id = "a" * 32
        rating = Rating(song_id=sample_song.id, session_id=session_id, is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()

        assert len(rating.session_id) >= 1

    def test_null_session_id_rejected(self, db_session, sample_song):
        """Test that null session_id is rejected."""
        rating = Rating(song_id=sample_song.id, session_id=None, is_thumbs_up=True)
        db_session.add(rating)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestRatingBehavior:
    """Tests for rating creation and retrieval behavior."""

    def test_rating_lookup_by_song_and_session(self, db_session, sample_song):
        """Test looking up rating by song_id and session_id."""
        rating = Rating(song_id=sample_song.id, session_id="lookup", is_thumbs_up=True)
        db_session.add(rating)
        db_session.commit()

        found = Rating.query.filter_by(
            song_id=sample_song.id,
            session_id="lookup"
        ).first()
        assert found is not None
        assert found.is_thumbs_up is True

    def test_rating_not_found_returns_none(self, db_session, sample_song):
        """Test that nonexistent rating returns None."""
        found = Rating.query.filter_by(
            song_id=sample_song.id,
            session_id="nonexistent"
        ).first()
        assert found is None

    def test_multiple_ratings_per_user_different_songs(self, db_session):
        """Test that one user can rate multiple different songs."""
        from app.models import Song
        song1 = Song(title="Song1", artist="Artist1")
        song2 = Song(title="Song2", artist="Artist2")
        db_session.add_all([song1, song2])
        db_session.commit()

        rating1 = Rating(song_id=song1.id, session_id="user1", is_thumbs_up=True)
        rating2 = Rating(song_id=song2.id, session_id="user1", is_thumbs_up=False)
        db_session.add_all([rating1, rating2])
        db_session.commit()

        user_ratings = Rating.query.filter_by(session_id="user1").all()
        assert len(user_ratings) == 2
