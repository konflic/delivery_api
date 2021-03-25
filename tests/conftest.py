import pytest
import os

from dotenv import load_dotenv

load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--url", action="store", default="http://127.0.0.1:5000")


@pytest.fixture
def base_url(request):
    return request.config.getoption("--url")


@pytest.fixture
def test_database():
    os.remove("")
