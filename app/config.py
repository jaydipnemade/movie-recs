import os

class Settings:
    APP_NAME: str = "Movie Recommender"
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-prod")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    ENABLE_TFIDF: bool = os.getenv("ENABLE_TFIDF", "1") == "1"  # allow disabling TF-IDF for speed

settings = Settings()
