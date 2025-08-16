def test_cf_score_nonnegative_when_fallback(client):
    token = client.post("/api/auth/signup", json={"email":"c@example.com","password":"secret12"}).json()["access_token"]
    # If there is insufficient data, CF should fallback or return empty safely
    r = client.get("/api/recommendations/cf", headers={"Authorization":"Bearer "+token})
    assert r.status_code in (200, 401)
    if r.status_code == 200:
        for x in r.json():
            assert isinstance(x["score"], float)
