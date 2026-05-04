from app.schemas.cv import CVGenerateRequest
from app.services.cv_generator import generate_cv


def test_generate_cv_returns_score_and_markdown() -> None:
    payload = CVGenerateRequest(
        job_title="Python Developer",
        job_post_text=(
            "We need python, fastapi, postgresql, docker experience and api design skills "
            "for backend development and cloud deployment."
        ),
        profile={
            "full_name": "Ali Veli",
            "email": "ali@example.com",
            "skills": ["python", "fastapi", "docker"],
            "experiences": [
                {
                    "company": "ABC Tech",
                    "title": "Backend Developer",
                    "summary": "Built REST API services with FastAPI and Docker on cloud infrastructure.",
                }
            ],
        },
    )

    result = generate_cv(payload.profile, payload.job_title, payload.job_post_text)

    assert result.ats_score >= 1
    assert "Ali Veli" in result.cv_markdown
    assert result.job_title == "Python Developer"
