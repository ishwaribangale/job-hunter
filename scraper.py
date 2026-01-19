"""
PJIS – Job Intelligence Scraper (Greenhouse – Corrected)
"""

import os
import json
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 12

# -------------------------------------------------
# VERIFIED GREENHOUSE SLUGS
# -------------------------------------------------
TOP_COMPANIES = [
    {"name": "Stripe", "slug": "stripeinc"},
    {"name": "Razorpay", "slug": "razorpaysoftware"},
    {"name": "Atlassian", "slug": "atlassian"},
    {"name": "PhonePe", "slug": "phonepe"},
    {"name": "CRED", "slug": "cred"},
]

# -------------------------------------------------
class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen = set()
        self.stats = {}

    def now(self):
        return datetime.utcnow().isoformat()

    def add(self, job):
        url = job.get("applyLink")
        if not url or url in self.seen:
            return
        self.seen.add(url)
        self.jobs.append(job)
        self.stats[job["source"]] = self.stats.get(job["source"], 0) + 1

    # -------------------------------------------------
    def scrape_greenhouse(self):
        print("\n[Greenhouse ATS]")

        for c in TOP_COMPANIES:
            print(f"\nCompany: {c['name']}")

            url = f"https://boards.greenhouse.io/{c['slug']}/jobs.json"

            try:
                res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                res.raise_for_status()

                data = res.json().get("jobs", [])
                print(f"Jobs found: {len(data)}")

                for j in data:
                    self.add({
                        "id": f"gh_{j.get('id')}",
                        "title": j.get("title"),
                        "company": c["name"],
                        "
