from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestWebhookEndpoints:
    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    def test_root_endpoint(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "508 Integrations Service"
        assert data["version"] == "0.1.0"

    def test_health_endpoint_healthy(self, client: TestClient) -> None:
        with patch("src.main.EspoCRMClient") as mock_client_class:
            mock_client = Mock()
            mock_client.health_check.return_value = True
            mock_client_class.return_value = mock_client

            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["espocrm"] == "connected"

    def test_health_endpoint_degraded(self, client: TestClient) -> None:
        with patch("src.main.EspoCRMClient") as mock_client_class:
            mock_client = Mock()
            mock_client.health_check.return_value = False
            mock_client_class.return_value = mock_client

            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["espocrm"] == "disconnected"

    def test_espocrm_webhook_success(
        self, client: TestClient, sample_webhook_payload: list
    ) -> None:
        with patch("src.main.BackgroundTasks.add_task") as mock_add_task:
            response = client.post("/webhooks/espocrm", json=sample_webhook_payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["events_processed"] == 2

            # Should queue background tasks for each event
            assert mock_add_task.call_count == 2

    def test_espocrm_webhook_invalid_payload(self, client: TestClient) -> None:
        # Send non-array payload
        invalid_payload = {"id": "contact1", "name": "John Doe"}

        response = client.post("/webhooks/espocrm", json=invalid_payload)

        assert response.status_code == 400
        assert "must be an array" in response.json()["detail"]

    def test_espocrm_webhook_empty_payload(self, client: TestClient) -> None:
        response = client.post("/webhooks/espocrm", json=[])

        assert response.status_code == 200
        data = response.json()
        assert data["events_processed"] == 0

    def test_process_contact_manual(self, client: TestClient) -> None:
        with patch("src.main.BackgroundTasks.add_task") as mock_add_task:
            response = client.post("/process-contact/contact123")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["contact_id"] == "contact123"

            mock_add_task.assert_called_once()


class TestBackgroundProcessing:
    def test_process_contact_skills_background_success(self) -> None:
        with patch("src.main.ContactSkillsProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_result = Mock()
            mock_result.success = True
            mock_result.new_skills = ["React", "Node.js"]
            mock_result.updated_skills = ["Python", "JavaScript", "React", "Node.js"]
            mock_processor.process_contact_skills.return_value = mock_result
            mock_processor_class.return_value = mock_processor

            from src.main import process_contact_skills_background

            # Should not raise exception
            process_contact_skills_background("contact123")

            mock_processor.process_contact_skills.assert_called_once_with("contact123")

    def test_process_contact_skills_background_failure(self) -> None:
        with patch("src.main.ContactSkillsProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_result = Mock()
            mock_result.success = False
            mock_result.error = "Processing failed"
            mock_processor.process_contact_skills.return_value = mock_result
            mock_processor_class.return_value = mock_processor

            from src.main import process_contact_skills_background

            # Should not raise exception even on failure
            process_contact_skills_background("contact123")

            mock_processor.process_contact_skills.assert_called_once_with("contact123")

    def test_process_contact_skills_background_exception(self) -> None:
        with patch("src.main.ContactSkillsProcessor") as mock_processor_class:
            mock_processor_class.side_effect = Exception("Unexpected error")

            from src.main import process_contact_skills_background

            # Should not raise exception
            process_contact_skills_background("contact123")
