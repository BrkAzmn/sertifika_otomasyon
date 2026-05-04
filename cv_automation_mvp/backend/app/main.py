from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="ATS CV Builder API",
    version="0.1.0",
    description="Job-post tailored and ATS-friendly CV generation API skeleton.",
)

app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
