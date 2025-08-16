from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
from functools import lru_cache
from app.models import Movie, Rating, User
from app.config import settings
from app.utils import timed

def _genres_to_str(genres: str) -> str:
    return "" if not genres else " ".join([g.strip().replace("-", "").replace("|", " ") for g in genres.split("|")])

@timed("content_based_recommender")
def content_based(db: Session, user: User, top_n: int = 20) -> List[Tuple[int, str, float]]:
    movies = db.query(Movie).all()
    if not movies:
        return []

    # Build corpus: genres + optional overview
    docs = []
    ids = []
    for m in movies:
        text = _genres_to_str(m.genres)
        if settings.ENABLE_TFIDF and m.overview:
            text = f"{text} {m.overview}"
        docs.append(text)
        ids.append(m.id)

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), stop_words="english")
    X = vectorizer.fit_transform(docs)  # (#movies, #features)

    # User preference vector: weighted avg of liked movies (score-centered)
    user_ratings = db.query(Rating).filter(Rating.user_id == user.id).all()
    rated_ids = {r.movie_id: r.score for r in user_ratings}
    if not rated_ids:
        # cold-start: highest average rated (fallback)
        return _popular_unrated(db, user, top_n)

    # Center scores around neutral 3 to emphasize likes
    weights = []
    vecs = []
    id_to_idx = {mid: i for i, mid in enumerate(ids)}
    for mid, score in rated_ids.items():
        if mid in id_to_idx:
            w = score - 3.0
            if w > 0:  # focus on likes
                weights.append(w)
                vecs.append(X[id_to_idx[mid]].toarray()[0])

    if not weights:
        return _popular_unrated(db, user, top_n)

    user_vec = np.average(np.array(vecs), axis=0, weights=np.array(weights)).reshape(1, -1)
    sims = sk_cosine(user_vec, X).flatten()  # similarity to all movies

    # Exclude rated
    for mid in rated_ids:
        if mid in id_to_idx:
            sims[id_to_idx[mid]] = -1

    # Top-N
    order = np.argsort(-sims)[:top_n]
    out: List[Tuple[int, str, float]] = []
    for idx in order:
        m_id = ids[idx]
        m = next((mm for mm in movies if mm.id == m_id), None)
        if m:
            out.append((m.id, m.title, float(sims[idx])))
    return out

@timed("cf_user_user_knn")
def collaborative_filtering(db: Session, user: User, k: int = 20, top_n: int = 20) -> List[Tuple[int, str, float]]:
    # Build user-item matrix in-memory
    ratings = db.query(Rating).all()
    if not ratings:
        return []

    users = sorted({r.user_id for r in ratings})
    movies = sorted({r.movie_id for r in ratings})
    u_index = {u: i for i, u in enumerate(users)}
    m_index = {m: i for i, m in enumerate(movies)}

    R = np.zeros((len(users), len(movies)), dtype=float)
    mask = np.zeros_like(R, dtype=bool)
    for r in ratings:
        ui, mi = u_index[r.user_id], m_index[r.movie_id]
        R[ui, mi] = r.score
        mask[ui, mi] = True

    if user.id not in u_index:
        return _popular_unrated(db, user, top_n)

    ui = u_index[user.id]
    # Mean-center per-user to mitigate user bias
    means = np.sum(R, axis=1) / np.maximum(mask.sum(axis=1), 1)
    R_centered = R - means[:, None]
    R_centered[~mask] = 0.0

    # Cosine similarity between users
    def row_cosine(A):
        norms = np.linalg.norm(A, axis=1, keepdims=True) + 1e-9
        A = A / norms
        return np.dot(A, A.T)

    S = row_cosine(R_centered)
    sims = S[ui].copy()
    sims[ui] = 0.0  # exclude self

    # K nearest neighbors (by similarity)
    nn_idx = np.argsort(-sims)[:k]
    nn_sims = sims[nn_idx].reshape(-1, 1)

    # Predict for items the target user hasn't rated
    user_mask = mask[ui]
    preds = np.zeros(len(movies))
    denom = np.sum(np.abs(nn_sims), axis=0)[0] + 1e-9

    for mi in range(len(movies)):
        if user_mask[mi]:
            preds[mi] = -1  # already seen
            continue
        neigh_ratings = R_centered[nn_idx, mi].reshape(-1, 1)
        num = float(np.sum(nn_sims * neigh_ratings))
        score = means[ui] + num / denom  # de-center
        preds[mi] = score

    order = np.argsort(-preds)[:top_n]
    out = []
    movie_objs = {m.id: m for m in db.query(Movie).filter(Movie.id.in_(movies))}
    for mi in order:
        if preds[mi] <= 0:
            continue
        mid = movies[mi]
        m = movie_objs.get(mid)
        if m:
            out.append((m.id, m.title, float(preds[mi])))
    if not out:
        return _popular_unrated(db, user, top_n)
    return out

def _popular_unrated(db: Session, user: User, top_n: int):
    # fallback by avg rating
    subq = (
        db.query(Rating.movie_id, func.avg(Rating.score).label("avg"), func.count(Rating.id).label("cnt"))
        .group_by(Rating.movie_id)
        .subquery()
    )
    from sqlalchemy import func
    q = (
        db.query(Movie, subq.c.avg, subq.c.cnt)
        .join(subq, subq.c.movie_id == Movie.id, isouter=True)
        .order_by((subq.c.avg).desc().nullslast(), (subq.c.cnt).desc().nullslast())
        .limit(top_n * 2)
    )
    rated = {r.movie_id for r in db.query(Rating).filter(Rating.user_id == user.id)}
    out = []
    for m, avg, cnt in q:
        if m.id in rated:
            continue
        out.append((m.id, m.title, float(avg or 0.0)))
        if len(out) >= top_n:
            break
    return out
