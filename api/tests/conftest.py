import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from mixer.backend.sqlalchemy import Mixer
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db import get_session
from src.db.models import *

@pytest.fixture(scope="function")
def session():
    """Create a test database session with in-memory SQLite"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(session) -> TestClient:
    """Create a test client with database dependency override"""
    def override_get_session():
        try:
            yield session
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def mixer(session: Session):
    yield Mixer(session=session)
    session.expunge_all()