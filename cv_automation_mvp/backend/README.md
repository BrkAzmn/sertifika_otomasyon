# Backend (FastAPI) - ATS CV Builder MVP

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## First Endpoints

- `GET /health`
- `POST /api/v1/cv/generate`
