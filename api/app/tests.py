from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.app.main import app, get_db
from api.app.database import Base

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables in the test database
Base.metadata.create_all(bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    db = None
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_short_url():
    response = client.post("/shorten", json={"long_url": "https://www.google.com"})
    assert response.status_code == 201
    assert "short_code" in response.json()

def test_redirect_to_long_url():
    # First, create a short URL
    response = client.post("/shorten", json={"long_url": "https://www.google.com"})
    short_code = response.json()["short_code"]

    # Then, test the redirection
    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://www.google.com/"

def test_get_analytics():
    # First, create a short URL
    response = client.post("/shorten", json={"long_url": "https://www.google.com"})
    short_code = response.json()["short_code"]

    # Then, access it to increment the hit count
    client.get(f"/{short_code}", follow_redirects=False)

    # Finally, get the analytics with the correct API key
    response = client.get(f"/analytics/{short_code}", headers={"X-API-KEY": "mysecretapikey"})
    assert response.status_code == 200
    data = response.json()
    assert data["long_url"] == "https://www.google.com/"
    assert data["short_code"] == short_code
    assert data["hits"] == 1
