from fastapi import APIRouter

from app.schemas.cv import CVGenerateRequest, CVGenerateResponse

router = APIRouter(prefix="/api/v1")


@router.post("/cv/generate", response_model=CVGenerateResponse)
def generate_cv(payload: CVGenerateRequest) -> CVGenerateResponse:
    # TODO: Parse job post, match profile, optimize ATS keywords, render PDF.
    return CVGenerateResponse(
        job_title=payload.job_title,
        ats_score=0,
        missing_keywords=[],
        cv_markdown="TODO: generated CV content",
    )
