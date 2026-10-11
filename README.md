# 💰 Personal Expense Tracker
**By Kerem Yildirim**

> A lightweight Python application designed to easily log daily transactions, categorize spending, and keep your personal budget on track.

**Project Status:** 🟡 *Initial Setup* (Virtual environment activated, Git repository configured, and core files initialized).

## 🐳 Run with Docker

Requires Docker Desktop. Copy `.env.example` to `.env` and put your Anthropic API key in it.

```bash
# Build the image (once, and again after code changes)
docker build -t expense-tracker .

# Run it: map the port, pass the API key at runtime, keep the database in a volume
docker run -d --name expense-tracker -p 5000:5000 --env-file .env -v expense-data:/data expense-tracker
```

Then open http://localhost:5000.

- `--env-file .env` hands the API key to the container when it starts. The key is never copied into the image (`.env` is in `.dockerignore`).
- `-v expense-data:/data` stores the SQLite database in a Docker volume, so expenses survive deleting the container. Without it, every new container starts empty.
- Flask runs with debug off and listens on `0.0.0.0` inside the container (set via `FLASK_HOST` in the Dockerfile).

Stop and remove the container (your data stays in the volume):

```bash
docker rm -f expense-tracker
```

Run locally without Docker: `python init_db.py`, then `python app.py` (set `FLASK_DEBUG=1` for debug mode).
