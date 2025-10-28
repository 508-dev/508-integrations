import json
from unittest.mock import Mock, patch

import pytest

from src.crm.skills_extractor import SkillsExtractor
from src.models import ExtractedSkills


class TestSkillsExtractor:
    @pytest.fixture
    def extractor(self) -> SkillsExtractor:
        with patch("src.crm.skills_extractor.OpenAI"):
            return SkillsExtractor()

    def test_create_skills_extraction_prompt(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        prompt = extractor._create_skills_extraction_prompt(sample_resume_text)

        assert "technical and professional skills" in prompt.lower()
        assert "programming languages" in prompt.lower()
        assert "json" in prompt.lower()
        assert sample_resume_text[:8000] in prompt

    def test_extract_skills_success(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        # Mock OpenAI response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        skills_data = {
            "skills": ["Python", "JavaScript", "React", "Docker", "AWS"],
            "confidence": 0.9,
        }

        mock_message.content = json.dumps(skills_data)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        with patch.object(extractor.client.chat.completions, "create") as mock_create:
            mock_create.return_value = mock_response

            result = extractor.extract_skills(sample_resume_text)

            assert isinstance(result, ExtractedSkills)
            assert result.skills == ["Python", "JavaScript", "React", "Docker", "AWS"]
            assert result.confidence == 0.9
            assert result.source == "gemini-1.5-flash"

    def test_extract_skills_invalid_json(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Invalid JSON response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        with patch.object(extractor.client.chat.completions, "create") as mock_create:
            mock_create.return_value = mock_response

            with pytest.raises(ValueError, match="Invalid JSON response"):
                extractor.extract_skills(sample_resume_text)

    def test_extract_skills_empty_response(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        with patch.object(extractor.client.chat.completions, "create") as mock_create:
            mock_create.return_value = mock_response

            with pytest.raises(ValueError, match="Empty response"):
                extractor.extract_skills(sample_resume_text)

    def test_extract_skills_invalid_skills_format(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        # Skills as string instead of list
        skills_data = {"skills": "Python, JavaScript", "confidence": 0.8}

        mock_message.content = json.dumps(skills_data)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        with patch.object(extractor.client.chat.completions, "create") as mock_create:
            mock_create.return_value = mock_response

            with pytest.raises(ValueError, match="Skills must be a list"):
                extractor.extract_skills(sample_resume_text)

    def test_extract_skills_strips_whitespace(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        skills_data = {
            "skills": ["  Python  ", " JavaScript ", "", "  React  "],
            "confidence": 0.85,
        }

        mock_message.content = json.dumps(skills_data)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        with patch.object(extractor.client.chat.completions, "create") as mock_create:
            mock_create.return_value = mock_response

            result = extractor.extract_skills(sample_resume_text)

            # Should strip whitespace and remove empty strings
            assert result.skills == ["Python", "JavaScript", "React"]

    def test_extract_skills_default_confidence(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        # Missing confidence field
        skills_data = {"skills": ["Python", "JavaScript"]}

        mock_message.content = json.dumps(skills_data)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        with patch.object(extractor.client.chat.completions, "create") as mock_create:
            mock_create.return_value = mock_response

            result = extractor.extract_skills(sample_resume_text)

            assert result.confidence == 0.7  # Default value

    def test_extract_skills_openai_exception(
        self, extractor: SkillsExtractor, sample_resume_text: str
    ) -> None:
        with patch.object(extractor.client.chat.completions, "create") as mock_create:
            mock_create.side_effect = Exception("OpenAI API error")

            with pytest.raises(ValueError, match="Skills extraction failed"):
                extractor.extract_skills(sample_resume_text)
