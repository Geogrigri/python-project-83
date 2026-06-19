### Hexlet tests and linter status

[![Actions Status](https://github.com/Geogrigri/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Geogrigri/python-project-83/actions)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Geogrigri_python-project-83\&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Geogrigri_python-project-83)

# Page Analyzer

Page Analyzer is a Flask web application for checking basic SEO information of websites.

The application allows users to add website URLs, run availability checks, and collect basic page data:

* HTTP status code
* `<h1>` content
* `<title>` content
* meta description

The project uses PostgreSQL for data storage, Bootstrap for the interface, and Render for deployment.

## Demo

Deployed application:

https://python-project-83-mq0b.onrender.com

## Technologies

* Python
* Flask
* PostgreSQL
* psycopg
* requests
* BeautifulSoup
* Bootstrap 5
* Gunicorn
* uv
* Render
* SonarCloud
* GitHub Actions

## Requirements

* Python 3.12+
* uv
* PostgreSQL

## Installation

Clone the repository:

```bash
git clone https://github.com/Geogrigri/python-project-83.git
cd python-project-83
```

Install dependencies:

```bash
make install
```

Create a local PostgreSQL database:

```bash
createdb page_analyzer
```

Apply the database schema:

```bash
psql -d page_analyzer -f database.sql
```

Create a `.env` file in the project root:

```env
SECRET_KEY=dev-secret-key
DATABASE_URL=postgresql:///page_analyzer
```

## Usage

Run the application in development mode:

```bash
make dev
```

Open in browser:

```text
http://127.0.0.1:5000
```

Run the production server locally:

```bash
make start
```

The application will be available at:

```text
http://localhost:8000
```

## Development

Run linter:

```bash
make lint
```

Show Flask routes:

```bash
uv run flask --app page_analyzer:app routes
```

## Database

The database schema is stored in:

```text
database.sql
```

The schema contains two tables:

* `urls` — stores added website URLs
* `url_checks` — stores check results for each URL

## Deployment

The project is deployed on Render.

Build command:

```bash
make build
```

Start command:

```bash
make render-start
```
