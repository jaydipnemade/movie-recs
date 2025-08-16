import csv
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import Movie

def run(csv_path: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count=0
        for row in reader:
            m = Movie(title=row["title"], year=int(row["year"]) if row["year"] else None,
                      genres=row.get("genres"), overview=row.get("overview"))
            db.add(m); count+=1
        db.commit()
        print(f"Inserted {count} movies")
    db.close()

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "data/movies_sample.csv")
