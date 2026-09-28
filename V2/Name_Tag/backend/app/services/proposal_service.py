from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.proposal import Proposal
from app.models.history import History
from app.models.snapshot import Snapshot
from app.services.mutation_service import apply_changes
from app.services.brand_state_service import get_brand_state

from copy import deepcopy


def create_proposal(
    db: Session,
    brand_id: str,
    user_id: str,
    title: str,
    summary: str,
    changes: dict,
) -> Proposal:
    proposal = Proposal(
        brand_id=brand_id,
        created_by=user_id,
        title=title.strip(),
        summary=summary.strip(),
        changes=changes,
        status="pending",
    )

    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return proposal


def get_proposal(
    db: Session,
    brand_id: str,
    proposal_id: str,
) -> Proposal | None:
    result = db.execute(
        select(Proposal).where(
            Proposal.id == proposal_id,
            Proposal.brand_id == brand_id,
        )
    )

    return result.scalar_one_or_none()


def get_brand_proposals(
    db: Session,
    brand_id: str,
) -> list[Proposal]:
    result = db.execute(
        select(Proposal)
        .where(
            Proposal.brand_id == brand_id,
        )
        .order_by(Proposal.created_at.desc())
    )

    return list(result.scalars().all())

def apply_proposal(
    db: Session,
    proposal: Proposal,
    user_id: str,
) -> Proposal:
    if proposal.status != "approved":
        raise ValueError(
            "Only approved proposals can be applied"
        )

    brand_state = get_brand_state(
        db=db,
        brand_id=proposal.brand_id,
    )

    if brand_state is None:
        raise ValueError(
            "Brand state not found"
        )

    previous_state = deepcopy(brand_state.state)
    previous_version = brand_state.version

    snapshot = Snapshot(
    brand_id=proposal.brand_id,
    version=previous_version,
    state=previous_state,
    created_by=user_id,
)

    db.add(snapshot)

    current_state, next_state = apply_changes(
        brand_state=brand_state,
        changes=proposal.changes,
    )

    brand_state.state = next_state
    brand_state.version = previous_version + 1

    history = History(
        brand_id=proposal.brand_id,
        user_id=user_id,
        action="proposal_applied",
        proposal_id=proposal.id,
        details={
            "from_version": previous_version,
            "to_version": brand_state.version,
            "changes": proposal.changes,
        },
    )

    db.add(history)
    proposal.status = "applied"

    db.commit()
    db.refresh(proposal)

    return proposal