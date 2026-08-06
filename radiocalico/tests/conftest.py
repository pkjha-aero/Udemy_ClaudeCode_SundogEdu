"""Pytest configuration and shared fixtures for Radio Calico tests."""

import pytest
import secrets
from app import create_app, db
from app.models import User, Item, Song, Rating


@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        _seed_test_user()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Return a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Return an isolated database session."""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def session_id():
    """Return a test session ID."""
    return secrets.token_hex(16)


def _seed_test_user():
    """Seed default test user."""
    if User.query.count() == 0:
        db.session.add(User(name="Pankaj Jha", email="pankaj.psu@gmail.com"))
        db.session.commit()


@pytest.fixture
def sample_user(db_session):
    """Create and return a sample user."""
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_song(db_session):
    """Create and return a sample song."""
    song = Song(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        date="2026-08-06",
        bit_depth=24,
        sample_rate=48000
    )
    db_session.add(song)
    db_session.commit()
    return song


@pytest.fixture
def sample_rating(db_session, sample_song):
    """Create and return a sample rating."""
    rating = Rating(
        song_id=sample_song.id,
        session_id=secrets.token_hex(16),
        is_thumbs_up=True
    )
    db_session.add(rating)
    db_session.commit()
    return rating


@pytest.fixture
def sample_item(db_session):
    """Create and return a sample item."""
    item = Item(name="Test Item")
    db_session.add(item)
    db_session.commit()
    return item
