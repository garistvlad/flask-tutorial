from blog_app import create_app


def test_config():
    assert not create_app().testing, (
        "Initial config should not be testing"
    )
    assert create_app({"TESTING": True}).testing, (
        "Config is expected to testing after assignment"
    )


def test_hello(client):
    response = client.get("/check")
    assert response.status_code == 200
    assert response.data == b"OK"
