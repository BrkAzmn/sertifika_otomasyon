# Backend (FastAPI) - ATS CV Builder MVP

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uygulamayı Başlat

```bash
./run_backend.sh
```

veya:

```bash
uvicorn app.main:app --reload
```

## Test

```bash
PYTHONPATH=. pytest -q
```

## Örnek istek

```bash
curl -X POST http://127.0.0.1:8000/api/v1/cv/generate   -H "Content-Type: application/json"   -d '{
    "job_title": "Python Developer",
    "job_post_text": "We need python fastapi postgresql docker and api design.",
    "profile": {
      "full_name": "Ali Veli",
      "email": "ali@example.com",
      "skills": ["python", "fastapi", "docker"],
      "experiences": [{
        "company": "ABC Tech",
        "title": "Backend Developer",
        "summary": "Built REST API services with FastAPI and Docker."
      }]
    },
    "language": "tr"
  }'
```
