import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db

# Ensure startup events run and DB is initialized
@pytest.fixture(scope="module")
def client():
    # Remove existing jobs.db to start fresh if needed
    if os.path.exists("jobs.db"):
        os.remove("jobs.db")
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_and_poll_job(client):
    payload = {
        "topic": "test SEO keywords",
        "word_count": 500,
        "language": "English"
    }

    # Create the job
    post_response = client.post("/api/jobs", json=payload)
    assert post_response.status_code == 202
    job_id = post_response.json()["id"]
    assert job_id is not None
    assert post_response.json()["status"] == "pending"

    # Poll the job
    get_response = client.get(f"/api/jobs/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == job_id
    # Since agent processing happens Async without mocked sleep, it might remain in pending/running state initially.
    assert get_response.json()["status"] in ["pending", "running", "failed"] 

def test_seo_constraint_model_validation():
    from app.models.schemas import SEOMetadata
    # Valid model
    meta1 = SEOMetadata(
        title_tag="Best SEO Guide 2025",
        meta_description="Learn everything about SEO in 2025 and stay ahead of the curve.",
        primary_keyword="SEO Guide",
        secondary_keywords=["SEO 2025", "SEO Basics"]
    )
    assert meta1.primary_keyword == "SEO Guide"
