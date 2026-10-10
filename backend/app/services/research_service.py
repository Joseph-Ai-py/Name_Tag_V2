from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.research_event import ResearchEvent
from app.models.research_finding import ResearchFinding
from app.models.research_job import ResearchJob
from app.models.research_report import ResearchReport
from app.models.research_source import ResearchSource
from app.schemas.research import ResearchSourceInput
from app.services.usage_service import record_usage, start_usage
from app.llm.gateway import get_llm_gateway
from app.db.session import SessionLocal
from app.research.providers.gemini_deep_research import GeminiDeepResearchProvider
from app.research.providers.gemini_deep_research import DeepResearchResult
from app.config import get_settings
from app.services.mutation_service import ALLOWED_PATHS


def build_research_proposal_changes(finding: ResearchFinding | dict) -> dict[str, str]:
	field_aliases = {
		"brand": "brand.positioning",
		"positioning": "brand.positioning",
		"target": "customer.target",
		"customer": "customer.target",
		"market": "market.competitors",
		"competitors": "market.competitors",
		"service": "business.service",
		"business": "business.service",
		"price": "business.pricing",
		"pricing": "business.pricing",
		"visual": "visual.mood",
		"mood": "visual.mood",
	}

	if isinstance(finding, dict):
		summary = finding.get("statement") or "Research finding"
		suggested_fields = finding.get("suggested_fields") or []
	else:
		summary = finding.statement
		suggested_fields = finding.suggested_fields or []

	changes: dict[str, str] = {}
	for field in suggested_fields:
		candidate = str(field).strip().lower()
		path = field_aliases.get(candidate, candidate)
		if path in ALLOWED_PATHS:
			changes[path] = summary
	if not changes:
		changes["brand.positioning"] = summary
	return changes


def create_research_plan(query: str) -> dict:
	return {
		"title": query[:300],
		"objective": query,
		"questions": [query],
		"scope": ["시장", "고객", "경쟁사"],
		"output_type": "market_analysis",
	}


def create_deep_research_job(db: Session, brand_id: str, user_id: str, query: str, plan: dict) -> ResearchJob:
	job = ResearchJob(
		brand_id=brand_id,
		created_by=user_id,
		mode="deep",
		status="planning",
		query=query,
		plan=plan,
		progress={"stage": "planning", "sources_found": 0},
	)
	db.add(job)
	db.flush()
	db.add(ResearchEvent(job_id=job.id, type="plan_created", stage="planning", message="Research Plan이 생성되었습니다."))
	db.commit()
	db.refresh(job)
	return job


def update_research_job_status(db: Session, job: ResearchJob, status: str) -> ResearchJob:
	allowed = {
		"planning": {"approved", "cancelled"},
		"approved": {"queued", "cancelled"},
		"queued": {"cancelled"},
		"failed": {"queued"},
	}
	if status not in allowed.get(job.status, set()):
		raise ValueError(f"Cannot change research job from {job.status} to {status}")
	job.status = status
	job.progress = {"stage": status, "sources_found": job.progress.get("sources_found", 0)}
	db.add(ResearchEvent(job_id=job.id, type=f"job_{status}", stage=status, message=f"Research Job 상태가 {status}로 변경되었습니다."))
	db.commit()
	db.refresh(job)
	return job


def run_deep_research_job(db: Session, job: ResearchJob) -> ResearchReport:
	if job.status not in {"approved", "queued"}:
		raise ValueError("Research job must be approved before starting")
	started_at = start_usage()
	job.status = "running"
	job.progress = {"stage": "researching", "sources_found": 0}
	db.add(ResearchEvent(job_id=job.id, type="research_started", stage="researching", message="Deep Research를 실행하고 있습니다."))
	db.commit()

	try:
		if get_settings().llm_provider == "mock":
			mock_response = get_llm_gateway().generate_text(task="research", message=job.query, context={"research_plan": job.plan})
			response = DeepResearchResult(text=mock_response.text, raw=mock_response.artifact_content)
		else:
			response = GeminiDeepResearchProvider().run(job.query, job.plan)
		report = ResearchReport(
			research_job_id=job.id,
			brand_id=job.brand_id,
			title=job.plan.get("title", job.query),
			executive_summary=response.text,
			sections=[
				{"type": "query", "title": "Research Query", "content": job.query},
				{"type": "analysis", "title": "AI Research Analysis", "content": response.raw or {}},
			],
			status="completed",
		)
		db.add(report)
		db.flush()
		for source_result in response.sources:
			db.add(ResearchSource(
				report_id=report.id,
				url=source_result.url,
				title=source_result.title,
				publisher=source_result.publisher,
				summary=source_result.summary,
				source_type="web",
			))
		db.flush()
		source_ids = [source.id for source in get_report_sources(db, report.id)]
		db.add(ResearchFinding(
			report_id=report.id,
			statement="Deep Research 보고서가 생성되었습니다. 핵심 근거와 불확실성은 Report 본문에서 확인하세요.",
			evidence=f"Gemini Google Search grounding에서 {len(source_ids)}개 출처를 수집했습니다.",
			source_ids=source_ids,
			confidence="supported" if source_ids else "uncertain",
			suggested_fields=[],
		))
		job.status = "completed"
		job.progress = {"stage": "completed", "sources_found": len(source_ids)}
		db.add(ResearchEvent(job_id=job.id, type="research_completed", stage="completed", message="Deep Research가 완료되었습니다."))
		db.commit()
		db.refresh(job)
		db.refresh(report)
		record_usage(db, job.created_by, job.brand_id, "deep_research", started_at)
		return report
	except Exception:
		job.status = "failed"
		job.progress = {"stage": "failed", "sources_found": 0}
		db.add(ResearchEvent(job_id=job.id, type="research_failed", stage="failed", message="Deep Research 실행에 실패했습니다."))
		db.commit()
		raise


def run_deep_research_background(job_id: str) -> None:
	db = SessionLocal()
	try:
		job = get_research_job(db, job_id)
		if job is not None:
			run_deep_research_job(db, job)
	finally:
		db.close()


def create_quick_research(
	db: Session,
	brand_id: str,
	user_id: str,
	query: str,
	title: str | None,
	sources: list[ResearchSourceInput],
) -> tuple[ResearchJob, ResearchReport]:
	started_at = start_usage()
	job = ResearchJob(
		brand_id=brand_id,
		created_by=user_id,
		mode="quick",
		status="running",
		query=query,
		plan={"objective": query, "source_count": len(sources)},
		progress={"stage": "source_collection", "sources_found": 0},
	)
	db.add(job)
	db.flush()

	db.add(ResearchEvent(
		job_id=job.id,
		type="research_started",
		stage="source_collection",
		message="Quick Research를 시작했습니다.",
	))

	report = ResearchReport(
		research_job_id=job.id,
		brand_id=brand_id,
		title=title or query[:300],
		executive_summary="제공된 출처를 기준으로 정리한 Quick Research 결과입니다.",
		sections=[{"type": "query", "title": "Research Query", "content": query}],
		status="completed",
	)
	db.add(report)
	db.flush()

	source_ids: list[str] = []
	for source_input in sources:
		source = ResearchSource(
			report_id=report.id,
			url=str(source_input.url),
			title=source_input.title,
			publisher=source_input.publisher,
			summary=source_input.summary,
			source_type=source_input.source_type,
		)
		db.add(source)
		db.flush()
		source_ids.append(source.id)

	if source_ids:
		db.add(ResearchFinding(
			report_id=report.id,
			statement=f"{len(source_ids)}개의 출처가 수집되었습니다.",
			evidence="; ".join(source.title for source in sources),
			source_ids=source_ids,
			confidence="supported",
		))

	job.status = "completed"
	job.progress = {"stage": "completed", "sources_found": len(source_ids)}
	db.add(ResearchEvent(
		job_id=job.id,
		type="research_completed",
		stage="completed",
		message="Quick Research가 완료되었습니다.",
	))
	db.commit()
	db.refresh(job)
	db.refresh(report)
	record_usage(db, user_id, brand_id, "quick_research", started_at)
	return job, report


def get_research_job(db: Session, job_id: str) -> ResearchJob | None:
	return db.get(ResearchJob, job_id)


def get_research_report(db: Session, report_id: str) -> ResearchReport | None:
	return db.get(ResearchReport, report_id)


def get_report_for_job(db: Session, job_id: str) -> ResearchReport | None:
	return db.scalar(select(ResearchReport).where(ResearchReport.research_job_id == job_id))


def get_report_sources(db: Session, report_id: str) -> list[ResearchSource]:
	result = db.execute(
		select(ResearchSource)
		.where(ResearchSource.report_id == report_id)
		.order_by(ResearchSource.accessed_at.asc())
	)
	return list(result.scalars())


def get_report_findings(db: Session, report_id: str) -> list[ResearchFinding]:
	result = db.execute(
		select(ResearchFinding)
		.where(ResearchFinding.report_id == report_id)
		.order_by(ResearchFinding.created_at.asc())
	)
	return list(result.scalars())
