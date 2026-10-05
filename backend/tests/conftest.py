import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Force testing configuration
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-key-32-chars-long-minimum-for-unit-tests"
os.environ["DEMO_MODE"] = "false"

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import get_password_hash, create_access_token
from app.services.protection_service import ProtectionService

# Create test SQLite engine with StaticPool so in-memory DB persists across threads
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session() -> Generator:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session) -> User:
    user = db_session.query(User).filter(User.email == "test@maskit.dev").first()
    if not user:
        user = User(
            email="test@maskit.dev",
            hashed_password=get_password_hash("ValidPass123!"),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        ProtectionService.get_or_create_default_policy(db_session, user.id)
    return user

@pytest.fixture
def auth_headers(test_user) -> dict:
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}
