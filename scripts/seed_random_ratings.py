import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import User, Movie, Rating
from app.auth import hash_password

def run(num_users=5, ratings_per_user=(3,7)):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    movies = db.query(Movie).all()
    if not movies:
        print("Seed movies first."); return
    # make users if none
    users = db.query(User).all()
    if not users:
        for i in range(num_users):
            u = User(email=f"user{i+1}@example.com", password_hash=hash_password("password"))
            db.add(u)
        db.commit()
        users = db.query(User).all()
    for u in users:
        chosen = random.sample(movies, k=min(len(movies), random.randint(*ratings_per_user)))
        for m in chosen:
            r = Rating(user_id=u.id, movie_id=m.id, score=random.randint(2,5))
            db.add(r)
    db.commit()
    print("Inserted random ratings.")
    db.close()

if __name__ == "__main__":
    run()
