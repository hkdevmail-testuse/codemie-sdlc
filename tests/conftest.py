import os
import tempfile

import pytest


@pytest.fixture(scope="session")
def flask_app():
    """Create a Flask app instance configured to use a temporary sqlite DB.

    We import from src.app:create_app which initializes the DB.
    """
    db_fd, db_path = tempfile.mkstemp(prefix="expense-tracker-", suffix=".db")
    os.close(db_fd)

    os.environ["EXPENSE_TRACKER_DB"] = db_path

    from src.app import create_app  # pylint: disable=import-error

    app = create_app()
    app.config.update(TESTING=True)

    yield app

    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()
