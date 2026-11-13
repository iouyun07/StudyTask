import os
import sys
import tempfile

import pytest

# 让测试可以直接 import 项目根目录下的 app / tasks / db
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture()
def app():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "SECRET_KEY": "test-key",
        }
    )
    yield application
    os.remove(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()
