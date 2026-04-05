# MLH PE Hackathon - Secure URL Shortener

An enterprise-ready URL Shortener built with Flask, Peewee, PostgreSQL, and an AI-powered Incident Response Analyst.

## Architecture & Core Features
* **Web Layer:** Nginx (Rate limiting & Reverse Proxy).
* **App Layer:** Gunicorn + Flask (4 workers).
* **Database:** PostgreSQL (Seeded via raw `psycopg2` script with collision bypass).
* **Security:** Custom RASP (Runtime Application Self-Protection) blocking XSS, SQLi, and Command Injection at the application layer.
* **Observability:** Integrated Llama-3 AI Analyst for raw log parsing and automated SRE incident reporting.

## Setup & Run
1. Clone the repo: `git clone <url>`
2. Start services: `sudo docker compose up -d --build`
3. Seed Database: `sudo docker compose exec web uv run python init_db.py`

## API Endpoints
* `GET /health`: Returns 200 OK for load balancers.
* `POST /shorten`: Expects `{"original_url": "..."}`. Returns 201 Created with `short_code`.
* `GET /<short_code>`: Redirects (302) to the original URL. Returns 404/403 for invalid or inactive links.

## Failure Modes & Troubleshooting (Runbook)
* **502 Bad Gateway:** Web workers failed to boot. *Fix:* Check `docker compose logs web` for ImportErrors.
* **403 Forbidden:** RASP triggered. *Fix:* Inspect payload for malicious signatures; run `uv run python scripts/ai_analyst.py` for root-cause report.
* **Database Seed Conflicts:** Handled automatically via `ON CONFLICT DO NOTHING`.
