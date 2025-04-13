import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client"))
)
import client


def test_server_url_env():
    assert client.SERVER_URL.startswith("http://")
