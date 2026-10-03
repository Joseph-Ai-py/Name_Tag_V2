from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import get_settings
from app.db.base import Base

from app.models.user import User  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.brand import Brand  # noqa: F401
from app.models.brand_member import BrandMember  # noqa: F401
from app.models.brand_state import BrandState  # noqa: F401
from app.models.proposal import Proposal  # noqa: F401
from app.models.snapshot import Snapshot  # noqa: F401
from app.models.history import History  # noqa: F401
from app.models.conversation import Conversation  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.artifact import Artifact  # noqa: F401
from app.models.research_job import ResearchJob  # noqa: F401
from app.models.research_report import ResearchReport  # noqa: F401
from app.models.research_source import ResearchSource  # noqa: F401
from app.models.research_finding import ResearchFinding  # noqa: F401
from app.models.research_event import ResearchEvent  # noqa: F401
from app.models.asset import Asset  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_block import DocumentBlock  # noqa: F401
from app.models.usage_event import UsageEvent  # noqa: F401
from app.models.agent_run import AgentRun  # noqa: F401
from app.models.tool_call import ToolCall  # noqa: F401
from app.models.employee_meeting import EmployeeMeeting  # noqa: F401
from app.models.meeting_opinion import MeetingOpinion  # noqa: F401
from app.models.meeting_decision import MeetingDecision  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    configuration["sqlalchemy.url"] = settings.database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
