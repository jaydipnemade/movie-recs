from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Movie, Rating
from app.schemas import MetricsOut

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/overview", response_model=MetricsOut)
def overview(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_movies = db.query(func.count(Movie.id)).scalar() or 0
    total_ratings = db.query(func.count(Rating.id)).scalar() or 0
    avg_ratings_per_user = (total_ratings / total_users) if total_users else 0.0
    # coverage: fraction of movies with at least 1 rating
    covered = db.query(func.count(func.distinct(Rating.movie_id))).scalar() or 0
    coverage_pct = (covered / total_movies * 100.0) if total_movies else 0.0
    return MetricsOut(
        total_users=total_users,
        total_movies=total_movies,
        total_ratings=total_ratings,
        avg_ratings_per_user=round(avg_ratings_per_user, 3),
        coverage_pct=round(coverage_pct, 2),
    )
