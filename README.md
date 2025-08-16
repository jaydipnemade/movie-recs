# Movie Recommendation Web App (FastAPI)

## Features
- Email/password auth (JWT)
- Browse/search movies with pagination & filters
- Rate 1–5, update, delete
- Content-based & CF (user–user KNN) recommendations
- Analytics tiles + chart (Chart.js)
- JSON APIs; minimal UI (Jinja2)
- Seed scripts + tests
- Docker-ready

## Getting Started

### Local (Python 3.10+)
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_movies.py data/movies_sample.csv
python scripts/seed_random_ratings.py
uvicorn app.main:app --reload
