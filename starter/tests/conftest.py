import pytest

from app import app as flask_app
from app import CURRENT


@pytest.fixture()
def app():
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_game_state():
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None
