"""
Pytest fixtures for Governance API tests.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "platform" / "governance"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from models import Base, Policy
from main import app, get_db
from policy import DEFAULT_POLICIES

TEST_DB_URL = "sqlite://"


@pytest.fixture(scope="function")
def client():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(bind=engine)

    db = TestingSessionLocal()
    if db.query(Policy).count() == 0:
        for p in DEFAULT_POLICIES:
            db.add(Policy(**p))
        db.commit()
    db.close()

    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
