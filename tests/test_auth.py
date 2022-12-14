from flask import g, session
import pytest

from blog_app.db import get_db


def test_register(client, app):
    assert client.get("/auth/register").status_code == 200, (
        "register endpoint is expected to be existed"
    )
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert response.headers["Location"] == "/auth/login", (
        "After registration user expected to be redirected to login page"
    )

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'"
        ).fetchone() is not None, (
            "User should be added to `user` table after registration"
        )


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('', '', b"Username is required"),
        ('a', '', b"Password is required"),
        ('test', 'test', b"is already registered"),
    )
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register",
        data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get("/auth/login").status_code == 200
    # BUG: auth.logit() returns 400 and raises exceptions.BadRequestKeyError(key)
    response = client.post("/auth/login", data={"username": "test", "password": "test"})
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", b"Incorrect username"),
        ("test", "a", b"Incorrect password"),
    )
)
def test_login_validate_input(client, auth, username, password, message):
    # response = auth.login(username, password)  # BUG: [400 BAD REQUEST]
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    assert message in response.data


def test_logout(client, auth):
    # auth.login()  # BUG: [400 BAD REQUEST]
    client.post("/auth/login", data={"username": "test", "password": "test"})
    with client:
        auth.logout()
        assert "user_id" not in session
