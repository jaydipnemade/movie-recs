from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.auth import get_current_user
from app.models import Rating, Movie
from app.schemas import RatingCreate, RatingOut

router = APIRouter(prefix="/api/ratings", tags=["ratings"])

@router.post("", response_model=RatingOut)
def upsert_rating(payload: RatingCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    movie = db.get(Movie, payload.movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    # upsert
    rat = db.query(Rating).filter(Rating.user_id == user.id, Rating.movie_id == payload.movie_id).first()
    if rat:
        rat.score = payload.score
    else:
        rat = Rating(user_id=user.id, movie_id=payload.movie_id, score=payload.score)
        db.add(rat)
    db.commit()
    return RatingOut(id=rat.id, movie_id=rat.movie_id, score=rat.score, title=movie.title)

@router.get("/me", response_model=List[RatingOut])
def my_ratings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (
        db.query(Rating, Movie.title)
        .join(Movie, Movie.id == Rating.movie_id)
        .filter(Rating.user_id == user.id)
        .order_by(Rating.updated_at.desc())
        .all()
    )
    return [RatingOut(id=r.Rating.id, movie_id=r.Rating.movie_id, score=r.Rating.score, title=r.title) for r in rows]

@router.delete("/{movie_id}")
def delete_rating(movie_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rat = db.query(Rating).filter(Rating.user_id == user.id, Rating.movie_id == movie_id).first()
    if not rat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    db.delete(rat)
    db.commit()
    return {"ok": True}
