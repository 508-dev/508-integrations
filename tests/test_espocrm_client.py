from unittest.mock import patch

import pytest

from src.crm.espocrm_client import EspoAPIError, EspoCRMClient
from src.models import ContactData


class TestEspoCRMClient:
    @pytest.fixture
    def client(self) -> EspoCRMClient:
        with patch("src.crm.espocrm_client.settings") as mock_settings:
            mock_settings.espocrm_url = "https://test.espocrm.com"
            mock_settings.espocrm_api_key = "test_api_key"
            return EspoCRMClient()

    def test_get_contact_success(
        self, client: EspoCRMClient, sample_contact_data: dict
    ) -> None:
        with patch.object(client.api, "request") as mock_request:
            mock_request.return_value = sample_contact_data

            result = client.get_contact("contact123")

            assert isinstance(result, ContactData)
            assert result.id == "contact123"
            assert result.name == "John Doe"
            assert result.skills == "Python, JavaScript"
            mock_request.assert_called_once_with("GET", "Contact/contact123")

    def test_get_contact_api_error(self, client: EspoCRMClient) -> None:
        with patch.object(client.api, "request") as mock_request:
            mock_request.side_effect = EspoAPIError("API error")

            with pytest.raises(ValueError, match="Failed to get contact"):
                client.get_contact("contact123")

    def test_get_contact_attachments_success(
        self, client: EspoCRMClient, sample_attachments: list
    ) -> None:
        with patch.object(client.api, "request") as mock_request:
            mock_request.return_value = {"list": sample_attachments}

            result = client.get_contact_attachments("contact123")

            assert result == sample_attachments
            mock_request.assert_called_once_with(
                "GET", "Contact/contact123/attachments"
            )

    def test_get_contact_attachments_empty(self, client: EspoCRMClient) -> None:
        with patch.object(client.api, "request") as mock_request:
            mock_request.return_value = {}

            result = client.get_contact_attachments("contact123")

            assert result == []

    def test_get_contact_attachments_api_error(self, client: EspoCRMClient) -> None:
        with patch.object(client.api, "request") as mock_request:
            mock_request.side_effect = EspoAPIError("API error")

            result = client.get_contact_attachments("contact123")

            assert result == []

    def test_download_attachment_success(self, client: EspoCRMClient) -> None:
        expected_content = b"fake attachment content"

        with patch.object(client.api, "download_file") as mock_download:
            mock_download.return_value = expected_content

            result = client.download_attachment("attachment123")

            assert result == expected_content
            mock_download.assert_called_once_with("Attachment/attachment123/download")

    def test_download_attachment_api_error(self, client: EspoCRMClient) -> None:
        with patch.object(client.api, "download_file") as mock_download:
            mock_download.side_effect = EspoAPIError("Download failed")

            result = client.download_attachment("attachment123")

            assert result is None

    def test_update_contact_skills_success(self, client: EspoCRMClient) -> None:
        skills = ["Python", "JavaScript", "React"]

        with patch.object(client.api, "request") as mock_request:
            mock_request.return_value = {"id": "contact123"}

            result = client.update_contact_skills("contact123", skills)

            assert result is True
            mock_request.assert_called_once_with(
                "PATCH", "Contact/contact123", {"skills": "Python, JavaScript, React"}
            )

    def test_update_contact_skills_api_error(self, client: EspoCRMClient) -> None:
        skills = ["Python", "JavaScript"]

        with patch.object(client.api, "request") as mock_request:
            mock_request.side_effect = EspoAPIError("Update failed")

            result = client.update_contact_skills("contact123", skills)

            assert result is False

    def test_health_check_success(self, client: EspoCRMClient) -> None:
        with patch.object(client.api, "request") as mock_request:
            mock_request.return_value = {"status": "ok"}

            result = client.health_check()

            assert result is True
            mock_request.assert_called_once_with("GET", "")

    def test_health_check_failure(self, client: EspoCRMClient) -> None:
        with patch.object(client.api, "request") as mock_request:
            mock_request.side_effect = Exception("Connection failed")

            result = client.health_check()

            assert result is False
