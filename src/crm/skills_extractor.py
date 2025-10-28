import json
import logging

from openai import OpenAI

from .models import ExtractedSkills
from .settings import settings

logger = logging.getLogger(__name__)


class SkillsExtractor:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.model = settings.openai_model

    def extract_skills(self, resume_text: str) -> ExtractedSkills:
        prompt = self._create_skills_extraction_prompt(resume_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume analyzer. Extract technical and professional skills from resumes accurately. Return only valid JSON with no additional text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")

            result = json.loads(content)

            skills = result.get("skills", [])
            confidence = result.get("confidence", 0.7)

            if not isinstance(skills, list):
                raise ValueError("Skills must be a list")

            skills = [skill.strip() for skill in skills if skill.strip()]

            return ExtractedSkills(
                skills=skills,
                confidence=confidence,
                source="gemini-1.5-flash",
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            raise ValueError(f"Skills extraction failed: {e}")

    def _create_skills_extraction_prompt(self, resume_text: str) -> str:
        return f"""
Analyze the following resume text and extract all technical and professional skills.
Focus on:
- Programming languages (Python, Java, JavaScript, etc.)
- Frameworks and libraries (React, Django, TensorFlow, etc.)
- Tools and technologies (Docker, AWS, Git, etc.)
- Professional skills (Project Management, Leadership, etc.)
- Certifications and qualifications
- Domain expertise (Machine Learning, DevOps, etc.)

Return ONLY a JSON object with this exact structure:
{{
    "skills": ["skill1", "skill2", "skill3"],
    "confidence": 0.85
}}

Where:
- skills: array of extracted skills (strings only)
- confidence: float between 0.0 and 1.0 representing extraction confidence

Resume text:
{resume_text[:8000]}
"""
