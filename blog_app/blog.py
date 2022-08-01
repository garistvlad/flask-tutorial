from flask import (
    Blueprint,
    flash, g,
    redirect, render_template, request,
    url_for
)
from werkzeug.exceptions import abort

from blog_app.auth import login_required
from blog_app.db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute("""
    SELECT
        post.id,
        post.title,
        post.body,
        post.created_timest,
        post.author_id,
        user.username
    FROM post
    JOIN user
        on post.author_id = user.id
    ORDER BY post.created_timest DESC
    """).fetchall()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("""
                INSERT INTO post (title, body, author_id)
                VALUES (?, ?, ?)
            """, (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template("blog/create.html")


def get_post(id: int, check_author: bool = True):
    """Load post from database by its id"""
    db = get_db()
    post = db.execute("""
    SELECT
        post.id,
        post.title,
        post.body,
        post.created_timest,
        post.author_id,
        user.username
    FROM post
    JOIN user
        on post.author_id = user.id
    WHERE post.id = ?
    """, (id,)).fetchone()

    if post is None:
        abort(404, f"Post #{id} does not exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("""
                UPDATE post SET title = ?, body = ?
                WHERE id = ?
            """, (title, body, id))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('blog.index'))
