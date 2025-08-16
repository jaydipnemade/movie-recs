from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Movie, Rating
from app.schemas import MovieOut

router = APIRouter(prefix="/api/movies", tags=["movies"])

@router.get("", response_model=List[MovieOut])
def list_movies(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="search title"),
    year: Optional[int] = None,
    genre: Optional[str] = None,
    page: int = 1,
    size: int = 20,
):
    """
    List / search movies with optional filters and pagination.
    Returns avg rating & rating count for each movie.
    """
    query = db.query(Movie)

    if q:
        query = query.filter(Movie.title.ilike(f"%{q}%"))
    if year:
        query = query.filter(Movie.year == year)
    if genre:
        # allows partial match; e.g., "Action" matches "Action|Sci-Fi"
        query = query.filter(Movie.genres.ilike(f"%{genre}%"))

    # pagination + deterministic order
    query = query.order_by(Movie.title.asc()).offset((page - 1) * size).limit(size)

    movies = query.all()

    out: List[MovieOut] = []
    if not movies:
        return out

    ids = [m.id for m in movies]

    # Build mapping: movie_id -> (avg, cnt)
    rows = (
        db.query(
            Rating.movie_id,
            func.avg(Rating.score).label("avg"),
            func.count(Rating.id).label("cnt"),
        )
        .filter(Rating.movie_id.in_(ids))
        .group_by(Rating.movie_id)
        .all()
    )
    agg = {
        mid: (float(avg) if avg is not None else None, int(cnt))
        for mid, avg, cnt in rows
    }

    for m in movies:
        avg, cnt = agg.get(m.id, (None, 0))
        out.append(
            MovieOut(
                id=m.id,
                title=m.title,
                year=m.year,
                genres=m.genres,
                overview=m.overview,
                avg_rating=avg,
                rating_count=cnt,
            )
        )

    return out
