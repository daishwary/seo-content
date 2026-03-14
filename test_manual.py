import traceback
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Make sure tables are created
from app.models.db_models import Job
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

try:
    with open("out.txt", "w") as f:
        f.write("Starting...\n")
        res1 = client.get("/health")
        f.write(f"Health: {res1.json()}\n")
        
        payload = {
            "topic": "test SEO keywords",
            "word_count": 500,
            "language": "English"
        }
        res2 = client.post("/api/jobs", json=payload)
        f.write(f"Post: {res2.status_code} {res2.json()}\n")
        
        job_id = res2.json()["id"]
        res3 = client.get(f"/api/jobs/{job_id}")
        f.write(f"Get: {res3.status_code} {res3.json()}\n")
except Exception as e:
    with open("out.txt", "a") as f:
        f.write(traceback.format_exc())
