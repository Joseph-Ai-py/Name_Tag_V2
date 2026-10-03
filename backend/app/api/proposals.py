from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.proposal import (
    ProposalCreateRequest,
    ProposalResponse,
)
from app.services.brand_service import get_brand_membership
from app.services.proposal_service import (
    create_proposal,
    get_brand_proposals,
    get_proposal,
    apply_proposal,
)

from app.core.permissions import require_editor_role

router = APIRouter(
    prefix="/api/brands",
    tags=["proposals"],
)


@router.post(
    "/{brand_id}/proposals",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal_endpoint(
    brand_id: str,
    payload: ProposalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    
    require_editor_role(membership.role)

    try:
        proposal = create_proposal(
            db=db,
            brand_id=brand_id,
            user_id=current_user.id,
            title=payload.title,
            summary=payload.summary,
            changes=payload.changes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ProposalResponse(
        id=proposal.id,
        brand_id=proposal.brand_id,
        created_by=proposal.created_by,
        title=proposal.title,
        summary=proposal.summary,
        changes=proposal.changes,
        status=proposal.status,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )


@router.get(
    "/{brand_id}/proposals",
    response_model=list[ProposalResponse],
)
def list_proposals(
    brand_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    proposals = get_brand_proposals(
        db=db,
        brand_id=brand_id,
    )

    return [
        ProposalResponse(
            id=proposal.id,
            brand_id=proposal.brand_id,
            created_by=proposal.created_by,
            title=proposal.title,
            summary=proposal.summary,
            changes=proposal.changes,
            status=proposal.status,
            created_at=proposal.created_at,
            updated_at=proposal.updated_at,
        )
        for proposal in proposals
    ]


@router.get(
    "/{brand_id}/proposals/{proposal_id}",
    response_model=ProposalResponse,
)
def get_proposal_endpoint(
    brand_id: str,
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    
    require_editor_role(membership.role)

    proposal = get_proposal(
        db=db,
        brand_id=brand_id,
        proposal_id=proposal_id,
    )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    return ProposalResponse(
        id=proposal.id,
        brand_id=proposal.brand_id,
        created_by=proposal.created_by,
        title=proposal.title,
        summary=proposal.summary,
        changes=proposal.changes,
        status=proposal.status,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )

@router.post(
    "/{brand_id}/proposals/{proposal_id}/approve",
    response_model=ProposalResponse,
)
def approve_proposal(
    brand_id: str,
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    require_editor_role(membership.role)

    proposal = get_proposal(
        db=db,
        brand_id=brand_id,
        proposal_id=proposal_id,
    )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    if proposal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending proposals can be approved",
        )

    proposal.status = "approved"

    db.commit()
    db.refresh(proposal)

    return ProposalResponse(
        id=proposal.id,
        brand_id=proposal.brand_id,
        created_by=proposal.created_by,
        title=proposal.title,
        summary=proposal.summary,
        changes=proposal.changes,
        status=proposal.status,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )

@router.post(
    "/{brand_id}/proposals/{proposal_id}/apply",
    response_model=ProposalResponse,
)
def apply_proposal_endpoint(
    brand_id: str,
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    require_editor_role(membership.role)

    proposal = get_proposal(
        db=db,
        brand_id=brand_id,
        proposal_id=proposal_id,
    )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    if proposal.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Proposal must be approved before applying",
        )

    try:
        proposal = apply_proposal(
            db=db,
            proposal=proposal,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ProposalResponse(
        id=proposal.id,
        brand_id=proposal.brand_id,
        created_by=proposal.created_by,
        title=proposal.title,
        summary=proposal.summary,
        changes=proposal.changes,
        status=proposal.status,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )

@router.post(
    "/{brand_id}/proposals/{proposal_id}/reject",
    response_model=ProposalResponse,
)
def reject_proposal(
    brand_id: str,
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    membership = get_brand_membership(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    require_editor_role(membership.role)

    proposal = get_proposal(
        db=db,
        brand_id=brand_id,
        proposal_id=proposal_id,
    )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    if proposal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending proposals can be rejected",
        )

    proposal.status = "rejected"

    db.commit()
    db.refresh(proposal)

    return ProposalResponse(
        id=proposal.id,
        brand_id=proposal.brand_id,
        created_by=proposal.created_by,
        title=proposal.title,
        summary=proposal.summary,
        changes=proposal.changes,
        status=proposal.status,
        created_at=proposal.created_at,
        updated_at=proposal.updated_at,
    )