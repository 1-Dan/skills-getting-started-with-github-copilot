"""Pytest configuration and fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient

# Add src directory to path to import app
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)
