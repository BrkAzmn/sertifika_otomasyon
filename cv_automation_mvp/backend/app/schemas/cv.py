from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    company: str = Field(..., min_length=2)
    title: str = Field(..., min_length=2)
    summary: str = Field(..., min_length=10)


class CandidateProfile(BaseModel):
    full_name: str = Field(..., min_length=3)
    email: str
    skills: list[str] = Field(default_factory=list)
    experiences: list[ExperienceItem] = Field(default_factory=list)


class CVGenerateRequest(BaseModel):
    job_title: str = Field(..., min_length=2)
    job_post_text: str = Field(..., min_length=50)
    profile: CandidateProfile
    language: str = Field(default="tr", pattern="^(tr|en)$")


class CVGenerateResponse(BaseModel):
    job_title: str
    ats_score: int
    missing_keywords: list[str]
    cv_markdown: str
