import pytest
from pydantic import ValidationError

from src.models import (
    ContactData,
    EspoCRMWebhookPayload,
    ExtractedSkills,
    SkillsExtractionResult,
    WebhookEvent,
)


class TestWebhookEvent:
    def test_webhook_event_creation(self) -> None:
        event = WebhookEvent(id="test123", name="Test Contact")
        assert event.id == "test123"
        assert event.name == "Test Contact"

    def test_webhook_event_missing_id(self) -> None:
        with pytest.raises(ValidationError):
            WebhookEvent(name="Test Contact")

    def test_webhook_event_optional_name(self) -> None:
        event = WebhookEvent(id="test123")
        assert event.id == "test123"
        assert event.name is None


class TestEspoCRMWebhookPayload:
    def test_from_list_single_event(self, sample_webhook_payload: list) -> None:
        single_event = [sample_webhook_payload[0]]
        payload = EspoCRMWebhookPayload.from_list(single_event)

        assert len(payload.events) == 1
        assert payload.events[0].id == "contact1"
        assert payload.events[0].name == "John Doe"

    def test_from_list_multiple_events(self, sample_webhook_payload: list) -> None:
        payload = EspoCRMWebhookPayload.from_list(sample_webhook_payload)

        assert len(payload.events) == 2
        assert payload.events[0].id == "contact1"
        assert payload.events[1].id == "contact2"

    def test_from_list_empty(self) -> None:
        payload = EspoCRMWebhookPayload.from_list([])
        assert len(payload.events) == 0


class TestContactData:
    def test_contact_data_creation(self, sample_contact_data: dict) -> None:
        contact = ContactData(**sample_contact_data)

        assert contact.id == "contact123"
        assert contact.name == "John Doe"
        assert contact.firstName == "John"
        assert contact.lastName == "Doe"
        assert contact.emailAddress == "john.doe@example.com"
        assert contact.skills == "Python, JavaScript"

    def test_contact_data_minimal(self) -> None:
        contact = ContactData(id="minimal123")
        assert contact.id == "minimal123"
        assert contact.name is None
        assert contact.skills is None


class TestExtractedSkills:
    def test_extracted_skills_creation(self) -> None:
        skills = ExtractedSkills(
            skills=["Python", "JavaScript", "React"],
            confidence=0.9,
            source="test_extractor",
        )

        assert skills.skills == ["Python", "JavaScript", "React"]
        assert skills.confidence == 0.9
        assert skills.source == "test_extractor"

    def test_confidence_validation(self) -> None:
        # Valid confidence values
        ExtractedSkills(skills=["Python"], confidence=0.0, source="test")
        ExtractedSkills(skills=["Python"], confidence=1.0, source="test")
        ExtractedSkills(skills=["Python"], confidence=0.5, source="test")

        # Invalid confidence values
        with pytest.raises(ValidationError):
            ExtractedSkills(skills=["Python"], confidence=-0.1, source="test")

        with pytest.raises(ValidationError):
            ExtractedSkills(skills=["Python"], confidence=1.1, source="test")


class TestSkillsExtractionResult:
    def test_successful_result(self) -> None:
        extracted_skills = ExtractedSkills(
            skills=["React", "Node.js"], confidence=0.8, source="test"
        )

        result = SkillsExtractionResult(
            contact_id="contact123",
            extracted_skills=extracted_skills,
            existing_skills=["Python", "JavaScript"],
            new_skills=["React", "Node.js"],
            updated_skills=["Python", "JavaScript", "React", "Node.js"],
            success=True,
        )

        assert result.contact_id == "contact123"
        assert result.success is True
        assert result.error is None
        assert len(result.new_skills) == 2
        assert len(result.updated_skills) == 4

    def test_failed_result(self) -> None:
        extracted_skills = ExtractedSkills(skills=[], confidence=0.0, source="error")

        result = SkillsExtractionResult(
            contact_id="contact123",
            extracted_skills=extracted_skills,
            existing_skills=["Python"],
            new_skills=[],
            updated_skills=["Python"],
            success=False,
            error="Failed to extract skills",
        )

        assert result.success is False
        assert result.error == "Failed to extract skills"
