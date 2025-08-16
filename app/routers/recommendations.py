from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.recommenders import content_based, collaborative_filtering
from app.schemas import RecoOut

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("/content", response_model=List[RecoOut])
def rec_content(db: Session = Depends(get_db), user=Depends(get_current_user), top_n: int = Query(20, ge=1, le=100)):
    rows = content_based(db, user, top_n=top_n)
    return [RecoOut(movie_id=i, title=t, score=s) for i, t, s in rows]

@router.get("/cf", response_model=List[RecoOut])
def rec_cf(db: Session = Depends(get_db), user=Depends(get_current_user), k: int = Query(20, ge=1, le=100), top_n: int = Query(20, ge=1, le=100)):
    rows = collaborative_filtering(db, user, k=k, top_n=top_n)
    return [RecoOut(movie_id=i, title=t, score=s) for i, t, s in rows]
