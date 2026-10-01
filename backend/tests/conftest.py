from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.dependencies import get_database
from app.main import app
from app.db.base import Base
from app.models.brand import Brand
from app.models.artifact import Artifact
from app.models.brand_member import BrandMember
from app.models.brand_state import BrandState
from app.models.conversation import Conversation
from app.models.history import History
from app.models.message import Message
from app.models.proposal import Proposal
from app.models.session import Session as UserSession
from app.models.snapshot import Snapshot
from app.models.user import User


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_database() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_database] = override_get_database
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def signup(client: TestClient, email: str) -> None:
    response = client.post(
        "/api/auth/signup",
        json={"email": email, "password": "Password123!"},
    )
    assert response.status_code == 201, response.text
