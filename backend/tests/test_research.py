from fastapi.testclient import TestClient

from app.models.research_event import ResearchEvent
from app.models.research_finding import ResearchFinding
from app.models.research_job import ResearchJob
from app.models.research_report import ResearchReport
from app.models.research_source import ResearchSource
from conftest import signup
from test_brands_and_state import create_brand
from app.services.research_service import get_research_job, run_deep_research_job


def test_quick_research_persists_report_sources_and_findings(client: TestClient) -> None:
    signup(client, "researcher@example.com")
    brand_id = create_brand(client)

    response = client.post(
        "/api/research/quick",
        json={
            "brand_id": brand_id,
            "query": "AI 브랜드 workspace 경쟁사 조사",
            "title": "경쟁사 Quick Research",
            "sources": [
                {
                    "url": "https://example.com/report",
                    "title": "Example Report",
                    "publisher": "Example",
                    "summary": "공식 자료 요약",
                    "source_type": "official",
                }
            ],
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["job"]["status"] == "completed"
    assert body["job"]["progress"]["sources_found"] == 1
    assert body["report"]["title"] == "경쟁사 Quick Research"
    assert len(body["report"]["sources"]) == 1
    assert body["report"]["findings"][0]["confidence"] == "supported"

    job = client.get(f"/api/research/jobs/{body['job']['id']}")
    report = client.get(f"/api/research/reports/{body['report']['id']}")
    assert job.status_code == 200
    assert report.status_code == 200
    assert report.json()["sources"][0]["url"] == "https://example.com/report"


def test_research_isolated_by_brand_membership(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)
    response = client.post(
        "/api/research/quick",
        json={"brand_id": brand_id, "query": "private research"},
    )
    assert response.status_code == 201
    job_id = response.json()["job"]["id"]
    report_id = response.json()["report"]["id"]

    client.post("/api/auth/logout")
    signup(client, "other@example.com")

    assert client.get(f"/api/research/jobs/{job_id}").status_code == 404
    assert client.get(f"/api/research/reports/{report_id}").status_code == 404


def test_deep_research_plan_job_approval_and_cancel(client: TestClient) -> None:
    signup(client, "deep@example.com")
    brand_id = create_brand(client)

    plan = client.post(
        "/api/research/plan",
        json={"brand_id": brand_id, "query": "시장 진입 가능성 분석"},
    )
    assert plan.status_code == 200
    assert plan.json()["output_type"] == "market_analysis"

    created = client.post(
        "/api/research/jobs",
        json={
            "brand_id": brand_id,
            "query": "시장 진입 가능성 분석",
            "plan": plan.json(),
        },
    )
    assert created.status_code == 201
    job_id = created.json()["id"]
    assert created.json()["status"] == "planning"

    approved = client.post(f"/api/research/jobs/{job_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    cancelled = client.post(f"/api/research/jobs/{job_id}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    invalid = client.post(f"/api/research/jobs/{job_id}/approve")
    assert invalid.status_code == 409


def test_approved_deep_research_job_runs_and_creates_report(client: TestClient) -> None:
    signup(client, "deep-run@example.com")
    brand_id = create_brand(client)
    plan = client.post("/api/research/plan", json={"brand_id": brand_id, "query": "AI 시장 분석"}).json()
    created = client.post("/api/research/jobs", json={"brand_id": brand_id, "query": "AI 시장 분석", "plan": plan})
    job_id = created.json()["id"]
    assert client.post(f"/api/research/jobs/{job_id}/approve").status_code == 200

    report = client.post(f"/api/research/jobs/{job_id}/start")
    assert report.status_code == 200, report.text
    assert report.json()["id"] == job_id
    from app.dependencies import get_database
    db_generator = client.app.dependency_overrides[get_database]()
    db = next(db_generator)
    try:
        run_deep_research_job(db, get_research_job(db, job_id))
    finally:
        db.close()
    job = client.get(f"/api/research/jobs/{job_id}")
    assert job.json()["status"] == "completed"
    completed_report = client.get(f"/api/research/jobs/{job_id}/report")
    assert completed_report.status_code == 200
    assert completed_report.json()["findings"]


def test_research_finding_creates_pending_proposal(client: TestClient) -> None:
    signup(client, "finding@example.com")
    brand_id = create_brand(client)
    response = client.post(
        "/api/research/quick",
        json={
            "brand_id": brand_id,
            "query": "고객 조사",
            "sources": [{"url": "https://example.com", "title": "Source"}],
        },
    )
    finding_id = response.json()["report"]["findings"][0]["id"]
    report_id = response.json()["report"]["id"]

    proposal = client.post(
        f"/api/research/reports/{report_id}/findings/{finding_id}/propose"
    )
    assert proposal.status_code == 201, proposal.text
    assert proposal.json()["status"] == "pending"