from fastapi import APIRouter

from app.schemas.cv import CVGenerateRequest, CVGenerateResponse
from app.services.cv_generator import generate_cv

router = APIRouter(prefix="/api/v1")


@router.post("/cv/generate", response_model=CVGenerateResponse)
def generate_cv_endpoint(payload: CVGenerateRequest) -> CVGenerateResponse:
    return generate_cv(
        profile=payload.profile,
        job_title=payload.job_title,
        job_post_text=payload.job_post_text,
    )
