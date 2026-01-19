import os

# Set dummy env vars for Pydantic Settings
os.environ["SECRET_KEY"] = "test_secret"
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "password"
os.environ["POSTGRES_DB"] = "test_db"
os.environ["S3_BUCKET"] = "test-bucket"
os.environ["OPENAI_API_KEY"] = "sk-test"
os.environ["PINECONE_API_KEY"] = "pc-test"
os.environ["PINECONE_ENVIRONMENT"] = "us-east-1"
os.environ["REDIS_HOST"] = "localhost"

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from services.database import get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_s3():
    return MagicMock()

@pytest.fixture
def mock_vector_store():
    return MagicMock()

@pytest.fixture
def mock_llm_response():
    mock = MagicMock()
    mock.content = "Mocked LLM Response"
    return mock
