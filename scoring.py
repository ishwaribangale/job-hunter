# scoring.py
# ----------------------------------
# Job Quality & Freshness Scoring
# ----------------------------------

from datetime import datetime, timedelta


def score_job(job: dict) -> int:
    score = 0

    # 1️⃣ Freshness
    try:
        posted = datetime.fromisoformat(job["postedDate"])
        if posted > datetime.utcnow() - timedelta(days=3):
            score += 3
        elif posted > datetime.utcnow() - timedelta(days=7):
            score += 1
    except Exception:
        pass

    # 2️⃣ Role importance
    if job.get("role") in {"product", "design", "software"}:
        score += 2

    # 3️⃣ Source quality
    source = job.get("source", "").lower()
    if "greenhouse" in source or "lever" in source:
        score += 2

    # 4️⃣ Direct apply link
    if job.get("applyLink"):
        score += 1

    return score
