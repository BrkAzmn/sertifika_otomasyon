import re
from collections import Counter

from app.schemas.cv import CandidateProfile, CVGenerateResponse

STOPWORDS = {
    "ve",
    "ile",
    "bir",
    "için",
    "olarak",
    "the",
    "and",
    "with",
    "for",
    "to",
    "of",
    "in",
}


def extract_keywords(job_post_text: str, limit: int = 15) -> list[str]:
    tokens = re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü+#.]{2,}", job_post_text.lower())
    filtered = [t for t in tokens if t not in STOPWORDS]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(limit)]


def _normalize(text: str) -> str:
    return text.lower().strip()


def score_profile_against_job(profile: CandidateProfile, keywords: list[str]) -> tuple[int, list[str]]:
    profile_blob = " ".join(
        [
            profile.full_name,
            " ".join(profile.skills),
            " ".join(f"{x.title} {x.summary} {x.company}" for x in profile.experiences),
        ]
    ).lower()

    matched = [kw for kw in keywords if kw in profile_blob]
    missing = [kw for kw in keywords if kw not in profile_blob][:10]

    if not keywords:
        return 0, []

    coverage = len(matched) / len(keywords)
    experience_boost = min(len(profile.experiences) * 5, 20)
    score = min(int(coverage * 80) + experience_boost, 100)
    return score, missing


def compose_cv_markdown(profile: CandidateProfile, job_title: str, matched_keywords: list[str]) -> str:
    experiences_md = "\n".join(
        f"- **{exp.title}**, {exp.company}: {exp.summary}" for exp in profile.experiences
    ) or "- Deneyim bilgisi girilmedi."

    skills = ", ".join(profile.skills) if profile.skills else "Belirtilmedi"
    highlight = ", ".join(matched_keywords[:8]) if matched_keywords else "Belirtilmedi"

    return (
        f"# {profile.full_name}\n\n"
        f"## Hedef Pozisyon\n{job_title}\n\n"
        f"## Profesyonel Özet\n"
        f"{job_title} rolü için profilim, ilan gereksinimleriyle uyumlu teknik ve operasyonel deneyim sunar.\n\n"
        f"## Yetenekler\n{skills}\n\n"
        f"## Deneyim\n{experiences_md}\n\n"
        f"## ATS Anahtar Kelime Eşleşmeleri\n{highlight}\n"
    )


def generate_cv(profile: CandidateProfile, job_title: str, job_post_text: str) -> CVGenerateResponse:
    keywords = extract_keywords(job_post_text)
    ats_score, missing_keywords = score_profile_against_job(profile, keywords)

    profile_blob = _normalize(
        " ".join(
            [
                " ".join(profile.skills),
                " ".join(f"{e.title} {e.summary} {e.company}" for e in profile.experiences),
            ]
        )
    )
    matched_keywords = [kw for kw in keywords if kw in profile_blob]

    return CVGenerateResponse(
        job_title=job_title,
        ats_score=ats_score,
        missing_keywords=missing_keywords,
        cv_markdown=compose_cv_markdown(profile, job_title, matched_keywords),
    )
