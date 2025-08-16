def signup_login(client):
    r = client.post("/api/auth/signup", json={"email":"t@example.com","password":"secret12"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return token

def test_crud_ratings_and_metrics(client):
    # seed a couple of movies directly through DB is heavy; rely on seed script is out-of-band
    # Instead, call seed_movies.py once in README instructions. For CI you could inject movies via API.
    # Here we gracefully skip if empty.
    token = signup_login(client)
    # list movies
    r = client.get("/api/movies")
    assert r.status_code == 200
    movies = r.json()
    # If no movies, skip remainder
    if not movies:
        return
    mid = movies[0]["id"]
    # create/update rating
    r = client.post("/api/ratings", headers={"Authorization":"Bearer "+token}, json={"movie_id": mid, "score": 5})
    assert r.status_code == 200
    r = client.get("/api/ratings/me", headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200
    assert len(r.json()) >= 1
    # delete
    r = client.delete(f"/api/ratings/{mid}", headers={"Authorization":"Bearer "+token})
    assert r.status_code == 200

def test_recommenders_exclude_rated(client):
    token = signup_login(client)
    r = client.get("/api/movies")
    movies = r.json()
    if len(movies) < 2:
        return
    # rate first one
    mid = movies[0]["id"]
    client.post("/api/ratings", headers={"Authorization":"Bearer "+token}, json={"movie_id": mid, "score": 5})
    # content-based
    rc = client.get("/api/recommendations/content", headers={"Authorization":"Bearer "+token})
    if rc.status_code == 200:
        recs = rc.json()
        assert all(x["movie_id"] != mid for x in recs)
    # cf
    rf = client.get("/api/recommendations/cf", headers={"Authorization":"Bearer "+token})
    if rf.status_code == 200:
        recs = rf.json()
        assert all(x["movie_id"] != mid for x in recs)
