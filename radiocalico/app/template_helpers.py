from flask import url_for


def prepare_index_context(items, users):
    """Prepare data for index.html template.

    Processes items and users, generates URLs, and returns context dict.
    """
    return {
        'items': items,
        'users': users,
        'logo_url': url_for('static', filename='radiocalico_logo.png'),
        'css_url': url_for('static', filename='index.css'),
        'player_url': url_for('main.player'),
        'add_user_url': url_for('main.add_user'),
    }
