import os
from datetime import date

import requests
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
from page_analyzer.parser import parse_page
from page_analyzer.url import normalize_url, validate_url

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.template_filter("truncate_text")
def truncate_text(value):
    if value is None:
        return ""

    value = str(value)

    if len(value) > 200:
        return f"{value[:200]}..."

    return value


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
                SELECT DISTINCT ON (urls.id)
                    urls.id,
                    urls.name,
                    url_checks.created_at AS last_check_created_at,
                    url_checks.status_code AS last_check_status_code
                FROM urls
                LEFT JOIN url_checks
                    ON urls.id = url_checks.url_id
                ORDER BY urls.id DESC, url_checks.id DESC
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

            cur.execute(
                """
                SELECT
                    id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC
                """,
                (id,),
            )
            checks = cur.fetchall()

    return render_template("url.html", url=url, checks=checks)


@app.post("/urls/<int:id>/checks")
def checks_post(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name
                FROM urls
                WHERE id = %s
                """,
                (id,),
            )
            url = cur.fetchone()

    try:
        response = requests.get(url["name"], timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("url_get", id=id))

    page_data = parse_page(response.text)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO url_checks (
                    url_id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    id,
                    response.status_code,
                    page_data["h1"],
                    page_data["title"],
                    page_data["description"],
                    date.today(),
                ),
            )
            conn.commit()

    flash("Страница успешно проверена", "success")
    return redirect(url_for("url_get", id=id))
