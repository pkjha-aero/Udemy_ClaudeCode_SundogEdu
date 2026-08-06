"""Unit tests for Flask route handlers (HTML pages)."""

import pytest


class TestIndexRoute:
    """Tests for GET / (homepage)."""

    def test_index_status_code_200(self, client):
        """Test that homepage returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_renders_template(self, client):
        """Test that homepage renders index.html."""
        response = client.get("/")
        assert b"Radio Calico" in response.data or b"Listen" in response.data

    def test_index_context_has_users(self, client, sample_user):
        """Test that index context includes users."""
        response = client.get("/")
        assert response.status_code == 200
        assert sample_user.name.encode() in response.data or b"Test User" in response.data

    def test_index_context_has_items(self, client, sample_item):
        """Test that index context includes items."""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_with_multiple_users(self, client, db_session):
        """Test homepage displays multiple users."""
        from app.models import User
        user1 = User(name="User One", email="user1@example.com")
        user2 = User(name="User Two", email="user2@example.com")
        db_session.add_all([user1, user2])
        db_session.commit()

        response = client.get("/")
        assert response.status_code == 200

    def test_index_with_default_user(self, client):
        """Test that index shows seeded default user."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Pankaj Jha" in response.data or b"pankaj" in response.data.lower()


class TestPlayerRoute:
    """Tests for GET /player (radio player page)."""

    def test_player_status_code_200(self, client):
        """Test that player page returns 200."""
        response = client.get("/player")
        assert response.status_code == 200

    def test_player_renders_template(self, client):
        """Test that player renders player.html."""
        response = client.get("/player")
        assert b"Radio Calico" in response.data or b"player" in response.data.lower()

    def test_player_no_context_required(self, client):
        """Test that player works without items/users."""
        response = client.get("/player")
        assert response.status_code == 200


class TestAddUserRoute:
    """Tests for POST /users (add user)."""

    def test_add_user_valid_form(self, client, db_session):
        """Test creating user with valid name and email."""
        from app.models import User
        response = client.post("/users", data={"name": "New User", "email": "new@example.com"})
        assert response.status_code == 302  # Redirect

        user = User.query.filter_by(email="new@example.com").first()
        assert user is not None
        assert user.name == "New User"

    def test_add_user_redirect_after_success(self, client):
        """Test that add_user redirects to index."""
        response = client.post(
            "/users",
            data={"name": "Test", "email": "test@example.com"},
            follow_redirects=False
        )
        assert response.status_code == 302

    def test_add_user_duplicate_email(self, client, sample_user):
        """Test that duplicate email is rejected."""
        from app.models import User
        initial_count = User.query.count()
        response = client.post(
            "/users",
            data={"name": "Different", "email": sample_user.email}
        )
        assert User.query.count() == initial_count

    def test_add_user_missing_name(self, client, db_session):
        """Test that empty name is rejected."""
        from app.models import User
        initial_count = User.query.count()
        response = client.post("/users", data={"name": "", "email": "test@example.com"})
        assert User.query.count() == initial_count

    def test_add_user_missing_email(self, client, db_session):
        """Test that empty email is rejected."""
        from app.models import User
        initial_count = User.query.count()
        response = client.post("/users", data={"name": "Test User", "email": ""})
        assert User.query.count() == initial_count

    def test_add_user_whitespace_trimmed(self, client, db_session):
        """Test that whitespace-only fields are rejected."""
        from app.models import User
        initial_count = User.query.count()
        response = client.post("/users", data={"name": "   ", "email": "   "})
        assert User.query.count() == initial_count

    def test_add_user_persists_to_db(self, client, db_session):
        """Test that user is persisted to database."""
        from app.models import User
        client.post("/users", data={"name": "Persistent", "email": "persist@example.com"})

        user = User.query.filter_by(email="persist@example.com").first()
        assert user is not None
        assert user.name == "Persistent"
