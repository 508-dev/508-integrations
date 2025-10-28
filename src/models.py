from typing import Any

from pydantic import BaseModel, Field


class WebhookEvent(BaseModel):
    id: str = Field(..., description="Record ID")
    name: str | None = Field(None, description="Record name")


class EspoCRMWebhookPayload(BaseModel):
    events: list[WebhookEvent] = Field(..., description="List of webhook events")

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> "EspoCRMWebhookPayload":
        events = [WebhookEvent(**event) for event in data]
        return cls(events=events)


class ContactData(BaseModel):
    id: str
    name: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    emailAddress: str | None = None
    skills: str | None = None
    attachments: list[dict[str, Any]] | None = None


class ExtractedSkills(BaseModel):
    skills: list[str] = Field(..., description="List of extracted skills")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    source: str = Field(..., description="Source of the extraction")


class SkillsExtractionResult(BaseModel):
    contact_id: str
    extracted_skills: ExtractedSkills
    existing_skills: list[str]
    new_skills: list[str]
    updated_skills: list[str]
    success: bool
    error: str | None = None
