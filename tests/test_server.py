import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server"))
)

import server
import base64


def test_dummy_image_generation():
    img = server.generate_dummy_image()
    assert img is not None
    assert img.shape == (480, 640, 3)


def test_list_routes():
    routes = [rule.rule for rule in server.app.url_map.iter_rules()]
    print("Available routes:", routes)
    assert "/image123" in routes


def test_image_endpoint_returns_base64():
    # Simulate no real image available, fallback to dummy
    with server.image_lock:
        server.latest_image = None

    with server.app.test_client() as client:
        response = client.get("/image")
        assert response.status_code == 200

        data = response.get_json()
        assert "image" in data
        assert isinstance(data["image"], str)

        # Validate base64 format
        try:
            decoded = base64.b64decode(data["image"])
            assert decoded is not None and len(decoded) > 0
        except Exception as e:
            assert False, f"Failed to decode base64: {e}"
