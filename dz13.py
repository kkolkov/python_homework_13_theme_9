from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
import hashlib
import uuid

# ============================================================
#                     СЕРВИС FASTAPI
# ============================================================

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Фейковый "пользователь"
FAKE_USERNAME = "admin"
FAKE_PASSWORD = "1234"


# ---- Логика аутентификации ----
def authenticate_user(username: str, password: str):
    return username == FAKE_USERNAME and password == FAKE_PASSWORD


def create_token(username: str):
    return hashlib.sha256(f"{username}-{uuid.uuid4()}".encode()).hexdigest()


# ---- Эндпойнты ----

@app.post("/login")
def login(username: str, password: str):
    if not authenticate_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(username)}


@app.get("/profile")
def profile(token: str = Depends(oauth2_scheme)):
    return {"msg": f"Ваш профиль. Токен: {token}"}


@app.get("/items")
def get_items():
    return {"items": ["item1", "item2", "item3"]}


@app.post("/items")
def create_item(name: str):
    return {"msg": "Item created", "name": name}


@app.get("/status")
def status():
    return {"status": "ok"}


# ============================================================
#                     ТЕСТЫ FASTAPI
# ============================================================

client = TestClient(app)


# ----------- LOGIN -----------
def test_login_success():
    r = client.post("/login", params={"username": "admin", "password": "1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_failure():
    r = client.post("/login", params={"username": "admin", "password": "wrong"})
    assert r.status_code == 401


# ----------- PROFILE -----------
def test_profile_without_token():
    r = client.get("/profile")
    assert r.status_code == 401


def test_profile_with_token():
    token = client.post("/login", params={"username": "admin", "password": "1234"}).json()["access_token"]
    r = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


# ----------- GET ITEMS -----------
def test_get_items_ok():
    r = client.get("/items")
    assert r.status_code == 200
    assert "items" in r.json()


def test_get_items_length():
    r = client.get("/items")
    assert len(r.json()["items"]) == 3


# ----------- CREATE ITEM -----------
def test_create_item_ok():
    r = client.post("/items", params={"name": "test"})
    assert r.status_code == 200
    assert r.json()["name"] == "test"


def test_create_item_empty():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 200
    assert r.json()["name"] == ""


# ----------- STATUS -----------
def test_status_ok():
    r = client.get("/status")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_status_key_exists():
    r = client.get("/status")
    assert "status" in r.json()


# ============================================================
#       Запуск сервиса вручную 
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
