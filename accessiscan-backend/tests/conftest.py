"""
AUTOMATED TEST ENVIRONMENT CONFIGURATION MATRIX (Pytest Conftest)
---------------------------------------------------------------------
Purpose:
    Establishes the global execution fixture context, mock perimeters, 
    and connection pooling rules for validating the API Backend.

Architecture:
    1. Isolated Runtime: Deploys in-memory SQLite (StaticPool) to ensure 
       database writes remain contained and do not pollute workspaces.
    2. Dependency Injection Override: Dynamically swaps production database 
       sessions for isolated test-memory sessions.
    3. Infrastructure Mocking: Stubs out heavy machine learning inference 
       tasks to ensure rapid, deterministic unit testing.
"""

import os
import sys
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# Import models to ensure registration in SQLModel metadata
from app.models.image import Image
from app.models.detection import Detection
from app.models.inspection import Inspection
from app.models.report import Report
from app.models.user import User

# --- 1. ENVIRONMENT BOUNDARY DEFINITION ---
# Purpose: Dynamically resolve filesystem anchors to ensure module imports 
# function correctly across independent development and test environments.
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(TEST_DIR, ".."))
AI_ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, "..", "accessiscan-ai-1"))

for path_gateway in [BACKEND_ROOT, AI_ROOT]:
    if path_gateway not in sys.path:
        sys.path.append(path_gateway)

from main import app
from app.db.session import get_session

# --- 2. TEST ENGINE INITIALIZATION ---
# Purpose: Configure a thread-safe, in-memory engine to provide 
# high-performance database state resets between test cycles.
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# --- 3. TEST FIXTURE DEFINITIONS ---
@pytest.fixture(name="session", scope="function")
def session_fixture() -> Generator[Session, None, None]:
    """
    Provides an isolated transactional boundary per test execution.
    Metadata initialization ensures all schemas are present in the test instance.
    """
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Injects the test session override into the FastAPI dependency graph
    and returns a clean TestClient for endpoint validation.
    """
    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()