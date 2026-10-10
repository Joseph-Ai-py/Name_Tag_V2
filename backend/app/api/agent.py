from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import require_editor_role
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.models.agent_run import AgentRun
from app.models.tool_call import ToolCall
from app.models.research_job import ResearchJob
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.services.proposal_service import get_proposal
from app.schemas.agent_run import AgentRunResponse, ToolCallResponse
from app.schemas.meeting import MeetingCreateRequest, MeetingDecisionResponse, MeetingOpinionResponse, MeetingResponse
from app.schemas.artifact import ArtifactResponse
from app.services.agent_service import run_agent
from app.services.brand_service import get_brand_membership
from app.services.meeting_service import get_meeting, get_meeting_decision, get_meeting_opinions, run_meeting
from app.core.permissions import require_editor_role

router = APIRouter(prefix="/api/agent", tags=["agent"])


def run_response(db: Session, run: AgentRun) -> AgentRunResponse:
	calls = db.scalars(
		select(ToolCall)
		.where(ToolCall.agent_run_id == run.id)
		.order_by(ToolCall.created_at.asc())
	).all()
	return AgentRunResponse(
		id=run.id,
		user_id=run.user_id,
		brand_id=run.brand_id,
		conversation_id=run.conversation_id,
		route=run.route,
		message=run.message,
		status=run.status,
		context=run.context,
		result=run.result,
		created_at=run.created_at,
		completed_at=run.completed_at,
		tool_calls=[ToolCallResponse.model_validate(call, from_attributes=True) for call in calls],
	)


def meeting_response(db: Session, meeting) -> MeetingResponse:
	opinions = get_meeting_opinions(db, meeting.id)
	decision = get_meeting_decision(db, meeting.id)
	return MeetingResponse(
		id=meeting.id,
		brand_id=meeting.brand_id,
		created_by=meeting.created_by,
		agenda=meeting.agenda,
		mode=meeting.mode,
		status=meeting.status,
		participants=meeting.participants,
		shared_context=meeting.shared_context,
		critic=meeting.critic,
		created_at=meeting.created_at,
		completed_at=meeting.completed_at,
		opinions=[MeetingOpinionResponse.model_validate(item, from_attributes=True) for item in opinions],
		decision=MeetingDecisionResponse.model_validate(decision, from_attributes=True) if decision else None,
	)


@router.post("/chat", response_model=AgentChatResponse)
def chat(
	payload: AgentChatRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	membership = get_brand_membership(db, payload.brand_id, current_user.id)
	if membership is None:
		raise HTTPException(status_code=404, detail="Brand not found")
	require_editor_role(membership.role)

	try:
		result = run_agent(
			db=db,
			current_user=current_user,
			brand_id=payload.brand_id,
			conversation_id=payload.conversation_id,
			message=payload.message,
		)
	except ValueError as exc:
		raise HTTPException(status_code=404, detail=str(exc)) from exc

	artifact = result["artifact"]
	proposal = get_proposal(db, payload.brand_id, result["proposal_id"]) if result.get("proposal_id") else None
	research_job = None
	pending_resource_id = result["execution"].get("pending_resource_id")
	if pending_resource_id:
		job = db.get(ResearchJob, pending_resource_id)
		if job is not None and job.brand_id == payload.brand_id:
			research_job = {
				"id": job.id,
				"query": job.query,
				"status": job.status,
				"plan": job.plan,
				"progress": job.progress,
			}
	artifact_response = None
	if artifact is not None:
		artifact_response = ArtifactResponse(
			id=artifact.id,
			brand_id=artifact.brand_id,
			created_by=artifact.created_by,
			type=artifact.type,
			title=artifact.title,
			content=artifact.content,
			status=artifact.status,
			created_at=artifact.created_at,
			updated_at=artifact.updated_at,
		)

	return AgentChatResponse(
		conversation_id=result["conversation_id"],
		route=result["route"],
		message=result["message"],
		artifact=artifact_response,
		proposal_id=result.get("proposal_id"),
		proposal={
			"id": proposal.id,
			"title": proposal.title,
			"summary": proposal.summary,
			"changes": proposal.changes,
			"status": proposal.status,
			"base_state_version": proposal.base_state_version,
		} if proposal else None,
		research_job=research_job,
		context=result["context"],
		agent={
			"run_id": result.get("run_id"),
			"mode": result["execution"]["mode"],
			"status": result["execution"]["status"],
		},
		execution=result["execution"],
	)


@router.get("/brands/{brand_id}/runs", response_model=list[AgentRunResponse])
def list_agent_runs(
	brand_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	if get_brand_membership(db, brand_id, current_user.id) is None:
		raise HTTPException(status_code=404, detail="Brand not found")
	runs = db.scalars(
		select(AgentRun)
		.where(AgentRun.brand_id == brand_id)
		.order_by(AgentRun.created_at.desc())
	).all()
	return [run_response(db, run) for run in runs]


@router.post("/meetings", response_model=MeetingResponse, status_code=201)
def create_meeting(
	payload: MeetingCreateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	membership = get_brand_membership(db, payload.brand_id, current_user.id)
	if membership is None:
		raise HTTPException(status_code=404, detail="Brand not found")
	require_editor_role(membership.role)
	try:
		meeting = run_meeting(db, payload.brand_id, current_user.id, payload.agenda, payload.mode)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	return meeting_response(db, meeting)


@router.get("/brands/{brand_id}/meetings/{meeting_id}", response_model=MeetingResponse)
def get_meeting_endpoint(
	brand_id: str,
	meeting_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_database),
):
	if get_brand_membership(db, brand_id, current_user.id) is None:
		raise HTTPException(status_code=404, detail="Brand not found")
	meeting = get_meeting(db, brand_id, meeting_id)
	if meeting is None:
		raise HTTPException(status_code=404, detail="Meeting not found")
	return meeting_response(db, meeting)
