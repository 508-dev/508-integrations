from unittest.mock import patch

import pytest

from src.settings import Settings


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        espocrm_url="https://test.espocrm.com",
        espocrm_api_key="test_api_key",
        openai_api_key="test_openai_key",
        openai_base_url="https://test.openai.com/v1/",
        openai_model="test-model",
        webhook_secret="test_secret",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def mock_espocrm_client():
    with patch("src.crm.espocrm_client.EspoCRMClient") as mock:
        yield mock


@pytest.fixture
def mock_document_processor():
    with patch("src.crm.document_processor.DocumentProcessor") as mock:
        yield mock


@pytest.fixture
def mock_skills_extractor():
    with patch("src.crm.skills_extractor.SkillsExtractor") as mock:
        yield mock


@pytest.fixture
def sample_resume_text() -> str:
    return """
    John Doe
    Software Engineer

    Experience:
    - Python programming for 5 years
    - FastAPI and Django web development
    - React and JavaScript frontend development
    - Docker containerization
    - AWS cloud services
    - PostgreSQL and MongoDB databases

    Skills:
    Python, JavaScript, React, Django, FastAPI, Docker, AWS, PostgreSQL, MongoDB,
    Git, Linux, Machine Learning, TensorFlow, Kubernetes

    Education:
    Bachelor of Computer Science
    """


@pytest.fixture
def sample_contact_data() -> dict:
    return {
        "id": "contact123",
        "name": "John Doe",
        "firstName": "John",
        "lastName": "Doe",
        "emailAddress": "john.doe@example.com",
        "skills": "Python, JavaScript",
    }


@pytest.fixture
def sample_attachments() -> list:
    return [
        {
            "id": "attachment1",
            "name": "john_doe_resume.pdf",
            "type": "application/pdf",
        },
        {
            "id": "attachment2",
            "name": "cover_letter.docx",
            "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        },
    ]


@pytest.fixture
def sample_webhook_payload() -> list:
    return [
        {"id": "contact1", "name": "John Doe"},
        {"id": "contact2", "name": "Jane Smith"},
    ]
