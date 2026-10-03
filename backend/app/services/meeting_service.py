from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee_meeting import EmployeeMeeting
from app.models.meeting_decision import MeetingDecision
from app.models.meeting_opinion import MeetingOpinion
from app.services.brand_state_service import get_brand_state
from app.services.proposal_service import create_proposal
from app.skills.executor import SkillExecutor

EMPLOYEE_SKILLS = {
    "business_strategist": "business",
    "market_researcher": "research",
    "customer_researcher": "customer",
    "brand_strategist": "brand",
    "visual_director": "visual",
}


def select_employees(agenda: str) -> list[str]:
    normalized = agenda.lower()
    selected = ["brand_strategist"]
    if any(keyword in normalized for keyword in ("사업", "비즈니스", "문제", "service")):
        selected.append("business_strategist")
    if any(keyword in normalized for keyword in ("시장", "경쟁", "market", "조사")):
        selected.append("market_researcher")
    if any(keyword in normalized for keyword in ("고객", "타겟", "customer")):
        selected.append("customer_researcher")
    if any(keyword in normalized for keyword in ("비주얼", "디자인", "visual")):
        selected.append("visual_director")
    if len(selected) == 1:
        selected.extend(["customer_researcher", "business_strategist"])
    return selected


def get_meeting(db: Session, brand_id: str, meeting_id: str) -> EmployeeMeeting | None:
    return db.scalar(
        select(EmployeeMeeting).where(
            EmployeeMeeting.id == meeting_id,
            EmployeeMeeting.brand_id == brand_id,
        )
    )


def get_meeting_opinions(db: Session, meeting_id: str) -> list[MeetingOpinion]:
    return list(
        db.scalars(
            select(MeetingOpinion)
            .where(MeetingOpinion.meeting_id == meeting_id)
            .order_by(MeetingOpinion.created_at.asc())
        ).all()
    )


def get_meeting_decision(db: Session, meeting_id: str) -> MeetingDecision | None:
    return db.scalar(select(MeetingDecision).where(MeetingDecision.meeting_id == meeting_id))


def run_meeting(db: Session, brand_id: str, user_id: str, agenda: str, mode: str) -> EmployeeMeeting:
    participants = select_employees(agenda)
    brand_state = get_brand_state(db, brand_id)
    shared_context = {
        "brand_state": brand_state.state if brand_state else {},
        "agenda": agenda,
        "opinions": [],
    }
    meeting = EmployeeMeeting(
        brand_id=brand_id,
        created_by=user_id,
        agenda=agenda,
        mode=mode,
        status="planning",
        participants=participants,
        shared_context=shared_context,
        critic={},
    )
    db.add(meeting)
    db.flush()

    meeting.status = "collecting_opinions"
    proposed_changes: dict[str, str] = {}
    for employee in participants:
        skill_name = EMPLOYEE_SKILLS[employee]
        response = SkillExecutor().execute(
            skill_name=skill_name,
            message=agenda,
            context=shared_context,
        )
        opinion = MeetingOpinion(
            meeting_id=meeting.id,
            employee=employee,
            skill=skill_name,
            opinion=response.text,
            evidence={"shared_context": shared_context, "artifact_type": response.artifact_type},
            agreements=[item["employee"] for item in shared_context["opinions"]],
            conflicts=[],
        )
        db.add(opinion)
        shared_context["opinions"].append({"employee": employee, "opinion": response.text})
        if not proposed_changes and response.proposed_changes:
            proposed_changes = response.proposed_changes

    meeting.status = "discussion" if mode == "full" else "critique"
    critic = {
        "summary": f"{len(participants)}명의 전문가 의견을 비교했습니다.",
        "agreements": ["모든 전문가는 사용자 승인 전 BrandState를 변경하지 않습니다."],
        "conflicts": [],
        "discussion_rounds": 1 if mode == "full" else 0,
    }
    meeting.status = "critique"
    meeting.critic = critic
    meeting.shared_context = shared_context

    meeting.status = "decision"
    if not proposed_changes:
        proposed_changes = {"brand.positioning": agenda}
    proposal = create_proposal(
        db=db,
        brand_id=brand_id,
        user_id=user_id,
        title="Brand Manager 회의 결정",
        summary=critic["summary"],
        changes=proposed_changes,
    )
    decision = MeetingDecision(
        meeting_id=meeting.id,
        decision="사용자 검토를 위한 통합 제안을 생성했습니다.",
        rationale=critic["summary"],
        changes=proposed_changes,
        proposal_id=proposal.id,
    )
    db.add(decision)
    meeting.status = "completed"
    meeting.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(meeting)
    return meeting
