import os, time
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt, pytest, fakeredis.aioredis

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUB = key.public_key().public_bytes(serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
os.environ["OIDC_PUBLIC_KEY"] = PUB
os.environ["STUDENT_EMAIL"] = "me@x.com"

from fastapi.testclient import TestClient
from app.main import app
from app.routers import q6_redis
q6_redis._client = fakeredis.aioredis.FakeRedis(decode_responses=True)
c = TestClient(app)
ORIGIN = "https://dash-t3xuf4.example.com"

def test_q3():
    r = c.get("/stats?values=1,2,3,10", headers={"Origin": ORIGIN})
    j = r.json()
    assert j == {"email": "me@x.com", "count": 4, "sum": 16, "min": 1, "max": 10, "mean": 4.0}
    assert r.headers["access-control-allow-origin"] == ORIGIN
    assert float(r.headers["x-process-time"]) >= 0 and len(r.headers["x-request-id"]) == 36
    p = c.options("/stats", headers={"Origin": ORIGIN, "Access-Control-Request-Method": "GET"})
    assert p.status_code in (200, 204) and p.headers["access-control-allow-origin"] == ORIGIN
    assert "x-request-id" in p.headers
    e = c.options("/stats", headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in e.headers
    g = c.get("/stats?values=1,2", headers={"Origin": "https://evil.com"})
    assert "access-control-allow-origin" not in g.headers and "x-request-id" in g.headers

def tok(k=key, **over):
    now = int(time.time())
    claims = {"iss": "https://idp.exam.local", "aud": "tds-mz0o1f8p.apps.exam.local",
              "sub": "u1", "email": "a@b.c", "exp": now + 600, "iat": now}
    claims.update(over)
    return jwt.encode(claims, k, algorithm="RS256")

def test_q4():
    r = c.post("/verify", json={"token": tok()})
    assert r.status_code == 200 and r.json() == {"valid": True, "email": "a@b.c", "sub": "u1",
                                                  "aud": "tds-mz0o1f8p.apps.exam.local"}
    for bad in (tok(exp=int(time.time()) - 10), tok(aud="nope"), tok(iss="https://evil"), tok(k=other)):
        r = c.post("/verify", json={"token": bad})
        assert r.status_code == 401 and r.json() == {"valid": False}
    t = tok(); h, p, s = t.split("."); 
    import base64, json
    pl = json.loads(base64.urlsafe_b64decode(p + "=="))
    pl["email"] = "evil@x.com"
    p2 = base64.urlsafe_b64encode(json.dumps(pl).encode()).rstrip(b"=").decode()
    assert c.post("/verify", json={"token": f"{h}.{p2}.{s}"}).status_code == 401
    assert c.post("/verify", json={}).status_code == 401
    assert c.post("/verify", content="garbage").status_code == 401

def test_q5():
    j = c.get("/effective-config").json()
    assert j == {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "*****"}
    j = c.get("/effective-config?set-port=9000&set-debug=TRUE&set-workers=3&set-log_level=debug&set-api_key=zzz").json()
    assert j == {"port": 9000, "workers": 3, "debug": True, "log_level": "debug", "api_key": "*****"}
    assert c.get("/effective-config?set-debug=No").json()["debug"] is False
    j = c.get("/effective-config?set=port=8851&set=log_level=debug").json()
    assert j["port"] == 8851 and j["log_level"] == "debug" and j["workers"] == 1

def test_q6():
    assert c.get("/count/k1").json() == {"key": "k1", "count": 0}
    for i in range(1, 4):
        assert c.post("/hit/k1").json() == {"key": "k1", "count": i}
    assert c.post("/hit/k2").json()["count"] == 1
    assert c.get("/count/k1").json()["count"] == 3
    h = c.get("/healthz").json()
    assert h["status"] == "ok" and h["redis"] == "up" and h["uptime_s"] >= 0

def test_q7():
    k = "ak_33h2xi1ieu8vtosuib0g6ehoi"
    ev = [{"user": "a", "amount": 10}, {"user": "b", "amount": 30.5}, {"user": "a", "amount": -5},
          {"user": "c", "amount": 0}, {"user": "a", "amount": 25}]
    assert c.post("/analytics", json={"events": ev}).status_code == 401
    assert c.post("/analytics", json={"events": ev}, headers={"X-API-Key": "x"}).status_code == 401
    r = c.post("/analytics", json={"events": ev}, headers={"X-API-Key": k, "Origin": "https://x.y"})
    assert r.json() == {"email": "me@x.com", "total_events": 5, "unique_users": 3,
                        "revenue": 65.5, "top_user": "a"}
    assert r.headers["access-control-allow-origin"] == "*"

def val():
    t = c.get("/metrics").text
    return int([l for l in t.splitlines() if l.startswith("http_requests_total")][0].split()[1])

def test_q8():
    b = val()
    for n in (1, 5, 7, 2):
        assert c.get(f"/work?n={n}").json() == {"email": "me@x.com", "done": n}
    assert val() >= b + 4
    assert c.get("/healthz").json()["uptime_s"] >= 0
    t = c.get("/logs/tail?limit=10").json()
    assert isinstance(t, list) and 1 <= len(t) <= 10
    assert all({"level", "ts", "path", "request_id"} <= set(e) for e in t)
    assert any("/work" in e["path"] for e in t)
