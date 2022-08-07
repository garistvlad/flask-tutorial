import pytest

from blog_app.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data, (
        "There should be a link to `Log In` if user is not authenticated"
    )
    assert b"Register" in response.data, (
        "There should be a link to `Register` if user is not authenticated"
    )

    # auth.login() # BUG: [400 status code]
    client.post("/auth/login", data={"username": "test", "password": "test"})
    response = client.get("/")
    assert b"Log Out" in response.data, (
        "Authenticated user should have `Log out` button"
    )
    assert b"test title" in response.data, (
        "Test user is expected to see his test post"
    )
    assert b"/1/update" in response.data, (
        "Test user should have link to edit his post"
    )


@pytest.mark.parametrize(
    "url", (
        "/create",
        "/1/update",
        "/1/delete",
    )
)
def test_login_required(client, auth, url):
    response = client.post(url)
    assert response.headers["Location"] == "/auth/login"


def test_only_author_modify_his_posts(app, client, auth):
    with app.app_context():
        db = get_db()
        # change ID of test author and try to modify post after
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    # auth.login()  # BUG: [400 status code]
    client.post("/auth/login", data={"username": "test", "password": "test"})
    # current user can't modify
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user does't see edit link
    assert b"1/update" not in client.get("/").data


@pytest.mark.parametrize(
    "url", (
        "/2/update",
        "/2/delete"
    )
)
def test_exists_required(client, auth, url):
    # auth.login()  # BUG: 400
    client.post("/auth/login", data={"username": "test", "password": "test"})
    assert client.post(url).status_code == 404


def test_create(client, auth, app):
    client.post("/auth/login", data={"username": "test", "password": "test"})
    assert client.get("/").status_code == 200
    client.post("/create", data={"title": "title #2", "body": "body #2"})

    with app.app_context():
        db = get_db()
        n_posts = db.execute("SELECT count(id) FROM post WHERE author_id = 1").fetchone()[0]
        assert n_posts == 2


def test_update(client, auth, app):
    expected_new_title = "updated title"
    client.post("/auth/login", data={"username": "test", "password": "test"})
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": expected_new_title, "body": "updated body"})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == expected_new_title


@pytest.mark.parametrize(
    "url", (
        "/create",
        "/1/update"
    )
)
def test_create_update_validate(client, auth, url):
    client.post("/auth/login", data={"username": "test", "password": "test"})
    response = client.post(url, data={"title": "", "body": ""})
    assert b"Title is required" in response.data


def test_delete(client, auth, app):
    client.post("/auth/login", data={"username": "test", "password": "test"})
    response = client.post("1/delete")
    assert response.headers["Location"] == "/", (
        "Redirect to main page is expected after deletion"
    )

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None, (
            "Post should be deleted from database also"
        )
