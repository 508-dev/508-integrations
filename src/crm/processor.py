import logging

from ..models import ExtractedSkills, SkillsExtractionResult
from .document_processor import DocumentProcessor
from .espocrm_client import EspoCRMClient
from .skills_extractor import SkillsExtractor

logger = logging.getLogger(__name__)


class ContactSkillsProcessor:
    def __init__(self) -> None:
        self.espocrm_client = EspoCRMClient()
        self.document_processor = DocumentProcessor()
        self.skills_extractor = SkillsExtractor()

    def process_contact_skills(self, contact_id: str) -> SkillsExtractionResult:
        try:
            contact = self.espocrm_client.get_contact(contact_id)
            existing_skills = self._parse_existing_skills(contact.skills)

            attachments = self.espocrm_client.get_contact_attachments(contact_id)
            resume_attachments = self._filter_resume_attachments(attachments)

            if not resume_attachments:
                return SkillsExtractionResult(
                    contact_id=contact_id,
                    extracted_skills=ExtractedSkills(
                        skills=[], confidence=0.0, source="no_resume"
                    ),
                    existing_skills=existing_skills,
                    new_skills=[],
                    updated_skills=existing_skills,
                    success=False,
                    error="No resume attachments found",
                )

            all_extracted_skills: list[str] = []
            confidence_sum = 0.0
            processed_count = 0

            for attachment in resume_attachments[:3]:
                try:
                    content = self.espocrm_client.download_attachment(attachment["id"])
                    if content:
                        text = self.document_processor.extract_text(
                            content, attachment["name"]
                        )
                        extracted = self.skills_extractor.extract_skills(text)
                        all_extracted_skills.extend(extracted.skills)
                        confidence_sum += extracted.confidence
                        processed_count += 1

                except Exception as e:
                    logger.warning(
                        f"Failed to process attachment {attachment['id']}: {e}"
                    )
                    continue

            if not all_extracted_skills:
                return SkillsExtractionResult(
                    contact_id=contact_id,
                    extracted_skills=ExtractedSkills(
                        skills=[], confidence=0.0, source="extraction_failed"
                    ),
                    existing_skills=existing_skills,
                    new_skills=[],
                    updated_skills=existing_skills,
                    success=False,
                    error="Failed to extract skills from any attachment",
                )

            unique_extracted_skills = list(set(all_extracted_skills))
            average_confidence = (
                confidence_sum / processed_count if processed_count > 0 else 0.0
            )

            extracted_skills = ExtractedSkills(
                skills=unique_extracted_skills,
                confidence=average_confidence,
                source="document_analysis",
            )

            new_skills = [
                skill
                for skill in unique_extracted_skills
                if skill.lower() not in [s.lower() for s in existing_skills]
            ]

            updated_skills = existing_skills + new_skills

            if new_skills:
                success = self.espocrm_client.update_contact_skills(
                    contact_id, updated_skills
                )
            else:
                success = True

            return SkillsExtractionResult(
                contact_id=contact_id,
                extracted_skills=extracted_skills,
                existing_skills=existing_skills,
                new_skills=new_skills,
                updated_skills=updated_skills,
                success=success,
                error=None if success else "Failed to update contact",
            )

        except Exception as e:
            logger.error(f"Error processing skills for contact {contact_id}: {e}")
            return SkillsExtractionResult(
                contact_id=contact_id,
                extracted_skills=ExtractedSkills(
                    skills=[], confidence=0.0, source="error"
                ),
                existing_skills=[],
                new_skills=[],
                updated_skills=[],
                success=False,
                error=str(e),
            )

    def _parse_existing_skills(self, skills_text: str | None) -> list[str]:
        if not skills_text:
            return []

        skills = [skill.strip() for skill in skills_text.split(",")]
        return [skill for skill in skills if skill]

    def _filter_resume_attachments(self, attachments: list[dict]) -> list[dict]:
        resume_keywords = ["resume", "cv", "curriculum"]
        allowed_extensions = {".pdf", ".doc", ".docx", ".txt"}

        resume_attachments = []
        for attachment in attachments:
            name = attachment.get("name", "").lower()
            file_ext = "." + name.split(".")[-1] if "." in name else ""

            if file_ext in allowed_extensions and any(
                keyword in name for keyword in resume_keywords
            ):
                resume_attachments.append(attachment)

        return resume_attachments
