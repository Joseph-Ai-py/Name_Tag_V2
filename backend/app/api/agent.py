from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permissions import require_editor_role
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.schemas.artifact import ArtifactResponse
from app.services.agent_service import run_agent
from app.services.brand_service import get_brand_membership

router = APIRouter(prefix="/api/agent", tags=["agent"])


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
		context=result["context"],
	)
