import os
from datetime import date
from urllib.parse import urlparse

import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.db import get_connection


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def validate_url(url):
    errors = []

    if len(url) > 255:
        errors.append("URL превышает 255 символов")

    if not validators.url(url):
        errors.append("Некорректный URL")

    return errors


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/urls")
def urls_post():
    url = request.form.get("url", "")
    errors = validate_url(url)

    if errors:
        for error in errors:
            flash(error, "danger")
        return render_template("index.html", url=url), 422

    normalized_url = normalize_url(url)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM urls WHERE name = %s",
                (normalized_url,),
            )
            existing_url = cur.fetchone()

            if existing_url:
                flash("Страница уже существует", "info")
                return redirect(url_for("url_get", id=existing_url["id"]))

            cur.execute(
                """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s)
                RETURNING id
                """,
                (normalized_url, date.today()),
            )
            new_url = cur.fetchone()
            conn.commit()

    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_get", id=new_url["id"]))


@app.get("/urls")
def urls_get():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, created_at
                FROM urls
                ORDER BY id DESC
                """
            )
            urls = cur.fetchall()

    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:id>")
def url_get(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, created_at
                FROM urls
                WHERE id = %s
                """,
                (id,),
            )
            url = cur.fetchone()

    return render_template("url.html", url=url)
