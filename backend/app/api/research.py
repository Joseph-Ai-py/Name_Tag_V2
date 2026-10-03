from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import require_editor_role
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.research import (
	DeepResearchJobRequest,
	QuickResearchRequest,
	QuickResearchResponse,
	ResearchPlanRequest,
	ResearchPlanResponse,
	ResearchFindingResponse,
	FindingProposalResponse,
	ResearchJobResponse,
	ResearchReportResponse,
	ResearchSourceResponse,
)
from app.services.brand_service import get_brand_membership
from app.services.research_service import (
	create_deep_research_job,
	create_research_plan,
	create_quick_research,
	get_report_findings,
	get_report_sources,
	get_research_job,
	get_research_report,
	get_report_for_job,
	run_deep_research_job,
	run_deep_research_background,
	update_research_job_status,
	build_research_proposal_changes,
)
from app.services.proposal_service import create_proposal, get_proposal

router = APIRouter(prefix="/api/research", tags=["research"])


def job_response(job) -> ResearchJobResponse:
	return ResearchJobResponse.model_validate(job, from_attributes=True)


def report_response(db: Session, report) -> ResearchReportResponse:
	return ResearchReportResponse(
		id=report.id,
		research_job_id=report.research_job_id,
		brand_id=report.brand_id,
		title=report.title,
		executive_summary=report.executive_summary,
		sections=report.sections,
		status=report.status,
		sources=[ResearchSourceResponse.model_validate(item, from_attributes=True) for item in get_report_sources(db, report.id)],
		findings=[ResearchFindingResponse.model_validate(item, from_attributes=True) for item in get_report_findings(db, report.id)],
		created_at=report.created_at,
		updated_at=report.updated_at,
	)


def require_brand_member(db: Session, brand_id: str, user_id: str):
	membership = get_brand_membership(db, brand_id, user_id)
	if membership is None:
		raise HTTPException(status_code=404, detail="Brand not found")
	return membership


@router.post("/quick", response_model=QuickResearchResponse, status_code=status.HTTP_201_CREATED)
def run_quick_research(
	payload: QuickResearchRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	membership = require_brand_member(db, payload.brand_id, current_user.id)
	require_editor_role(membership.role)
	job, report = create_quick_research(
		db=db,
		brand_id=payload.brand_id,
		user_id=current_user.id,
		query=payload.query,
		title=payload.title,
		sources=payload.sources,
	)
	return QuickResearchResponse(job=job_response(job), report=report_response(db, report))


@router.post("/plan", response_model=ResearchPlanResponse)
def create_plan(
	payload: ResearchPlanRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	membership = require_brand_member(db, payload.brand_id, current_user.id)
	require_editor_role(membership.role)
	return ResearchPlanResponse(**create_research_plan(payload.query))


@router.post("/jobs", response_model=ResearchJobResponse, status_code=status.HTTP_201_CREATED)
def create_deep_job(
	payload: DeepResearchJobRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	membership = require_brand_member(db, payload.brand_id, current_user.id)
	require_editor_role(membership.role)
	job = create_deep_research_job(db, payload.brand_id, current_user.id, payload.query, payload.plan.model_dump())
	return job_response(job)


@router.get("/jobs/{job_id}", response_model=ResearchJobResponse)
def get_job(
	job_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	job = get_research_job(db, job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="Research job not found")
	require_brand_member(db, job.brand_id, current_user.id)
	return job_response(job)


@router.post("/jobs/{job_id}/approve", response_model=ResearchJobResponse)
def approve_job(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	job = get_research_job(db, job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="Research job not found")
	membership = require_brand_member(db, job.brand_id, current_user.id)
	require_editor_role(membership.role)
	try:
		return job_response(update_research_job_status(db, job, "approved"))
	except ValueError as exc:
		raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/cancel", response_model=ResearchJobResponse)
def cancel_job(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	job = get_research_job(db, job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="Research job not found")
	membership = require_brand_member(db, job.brand_id, current_user.id)
	require_editor_role(membership.role)
	try:
		return job_response(update_research_job_status(db, job, "cancelled"))
	except ValueError as exc:
		raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/start", response_model=ResearchJobResponse)
def start_job(job_id: str, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	job = get_research_job(db, job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="Research job not found")
	membership = require_brand_member(db, job.brand_id, current_user.id)
	require_editor_role(membership.role)
	try:
		job = update_research_job_status(db, job, "queued")
		background_tasks.add_task(run_deep_research_background, job.id)
		return job_response(job)
	except ValueError as exc:
		raise HTTPException(status_code=409, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=502, detail="Deep Research provider failed") from exc


@router.post("/jobs/{job_id}/retry", response_model=ResearchJobResponse)
def retry_job(job_id: str, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	job = get_research_job(db, job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="Research job not found")
	membership = require_brand_member(db, job.brand_id, current_user.id)
	require_editor_role(membership.role)
	try:
		job = update_research_job_status(db, job, "queued")
		background_tasks.add_task(run_deep_research_background, job.id)
		return job_response(job)
	except ValueError as exc:
		raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/reports/{report_id}", response_model=ResearchReportResponse)
def get_report(
	report_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	report = get_research_report(db, report_id)
	if report is None:
		raise HTTPException(status_code=404, detail="Research report not found")
	require_brand_member(db, report.brand_id, current_user.id)
	return report_response(db, report)


@router.get("/jobs/{job_id}/report", response_model=ResearchReportResponse)
def get_job_report(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
	job = get_research_job(db, job_id)
	if job is None:
		raise HTTPException(status_code=404, detail="Research job not found")
	require_brand_member(db, job.brand_id, current_user.id)
	report = get_report_for_job(db, job_id)
	if report is None:
		raise HTTPException(status_code=404, detail="Research report not found")
	return report_response(db, report)


@router.post("/reports/{report_id}/findings/{finding_id}/propose", response_model=FindingProposalResponse, status_code=status.HTTP_201_CREATED)
def propose_finding_application(
	report_id: str,
	finding_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	report = get_research_report(db, report_id)
	if report is None:
		raise HTTPException(status_code=404, detail="Research report not found")
	membership = require_brand_member(db, report.brand_id, current_user.id)
	require_editor_role(membership.role)
	finding = next((item for item in get_report_findings(db, report_id) if item.id == finding_id), None)
	if finding is None:
		raise HTTPException(status_code=404, detail="Research finding not found")
	proposal = create_proposal(
		db=db,
		brand_id=report.brand_id,
		user_id=current_user.id,
		title="Research Finding 적용 제안",
		summary=finding.statement,
		changes=build_research_proposal_changes(finding),
	)
	return FindingProposalResponse(
		proposal_id=proposal.id,
		finding_id=finding.id,
		status=proposal.status,
	)
