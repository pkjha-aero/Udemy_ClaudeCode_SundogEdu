"""Unit tests for template helper functions."""

import pytest
from app.template_helpers import prepare_index_context


class TestPrepareIndexContext:
    """Tests for prepare_index_context function."""

    def test_prepare_context_with_items_and_users(self, app, sample_item, sample_user):
        """Test context generation with items and users."""
        with app.app_context():
            context = prepare_index_context([sample_item], [sample_user])
            assert "items" in context
            assert "users" in context

    def test_prepare_context_empty_lists(self, app):
        """Test context generation with empty lists."""
        with app.app_context():
            context = prepare_index_context([], [])
            assert context["items"] == []
            assert context["users"] == []

    def test_prepare_context_has_logo_url(self, app):
        """Test that logo_url is in context."""
        with app.app_context():
            context = prepare_index_context([], [])
            assert "logo_url" in context
            assert "radiocalico_logo.png" in context["logo_url"]

    def test_prepare_context_has_css_url(self, app):
        """Test that css_url is in context."""
        with app.app_context():
            context = prepare_index_context([], [])
            assert "css_url" in context
            assert "index.css" in context["css_url"]

    def test_prepare_context_has_player_url(self, app):
        """Test that player_url is in context."""
        with app.app_context():
            context = prepare_index_context([], [])
            assert "player_url" in context
            assert "player" in context["player_url"]

    def test_prepare_context_has_add_user_url(self, app):
        """Test that add_user_url is in context."""
        with app.app_context():
            context = prepare_index_context([], [])
            assert "add_user_url" in context
            assert "add_user" in context["add_user_url"] or "users" in context["add_user_url"]

    def test_prepare_context_preserves_items(self, app, sample_item):
        """Test that items list is preserved."""
        with app.app_context():
            items = [sample_item]
            context = prepare_index_context(items, [])
            assert len(context["items"]) == 1
            assert context["items"][0] == sample_item

    def test_prepare_context_preserves_users(self, app, sample_user):
        """Test that users list is preserved."""
        with app.app_context():
            users = [sample_user]
            context = prepare_index_context([], users)
            assert len(context["users"]) == 1
            assert context["users"][0] == sample_user

    def test_prepare_context_multiple_items(self, app, db_session):
        """Test context with multiple items."""
        from app.models import Item
        items = [
            Item(name="Item1"),
            Item(name="Item2"),
            Item(name="Item3"),
        ]
        db_session.add_all(items)
        db_session.commit()

        with app.app_context():
            context = prepare_index_context(items, [])
            assert len(context["items"]) == 3

    def test_prepare_context_returns_dict(self, app):
        """Test that context is a dict."""
        with app.app_context():
            context = prepare_index_context([], [])
            assert isinstance(context, dict)

    def test_prepare_context_urls_are_strings(self, app):
        """Test that all URLs are strings."""
        with app.app_context():
            context = prepare_index_context([], [])
            assert isinstance(context["logo_url"], str)
            assert isinstance(context["css_url"], str)
            assert isinstance(context["player_url"], str)
            assert isinstance(context["add_user_url"], str)
