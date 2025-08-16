from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MovieOut(BaseModel):
    id: int
    title: str
    year: Optional[int]
    genres: Optional[str]
    overview: Optional[str]
    avg_rating: Optional[float] = None
    rating_count: int = 0
    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    movie_id: int
    score: int = Field(ge=1, le=5)

class RatingOut(BaseModel):
    id: int
    movie_id: int
    score: int
    title: Optional[str] = None
    class Config:
        from_attributes = True

class MetricsOut(BaseModel):
    total_users: int
    total_movies: int
    total_ratings: int
    avg_ratings_per_user: float
    coverage_pct: float

class RecoOut(BaseModel):
    movie_id: int
    title: str
    score: float
