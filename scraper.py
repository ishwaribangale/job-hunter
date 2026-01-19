"""
PJIS – Job Intelligence Scraper (Stable ATS Edition)
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 12

# -------------------------------------------------
# VERIFIED ATS CONFIG
# -------------------------------------------------
TOP_COMPANIES = [
    {"name": "Stripe", "ats": "greenhouse", "slug": "stripe"},
    {"name": "Razorpay", "ats": "greenhouse", "slug": "razorpay"},
    {"name": "Paytm", "ats": "greenhouse", "slug": "paytm"},
    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},
    {"name": "CRED", "ats": "greenhouse", "slug": "cred"},
    {"name": "Atlassian", "ats": "greenhouse", "slug": "atlassian"},
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
    # GREENHOUSE
    # -------------------------------------------------
    def scrape_greenhouse(self):
        print("\n[Greenhouse ATS]")

        for c in TOP_COMPANIES:
            print(f"\nCompany: {c['name']}")

            url = f"https://boards.greenhouse.io/{c['slug']}/jobs.json"

            try:
                res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                if res.status_code != 200:
                    print("Request blocked or not found")
                    continue

                data = res.json().get("jobs", [])
                print(f"Jobs found: {len(data)}")

                for j in data:
                    self.add({
                        "id": f"gh_{j.get('id')}",
                        "title": j.get("title"),
                        "company": c["name"],
                        "location": j.get("location", {}).get("name"),
                        "source": f"{c['name']} (Greenhouse)",
                        "applyLink": j.get("absolute_url"),
                        "postedDate": self.now(),
                        "fetchedAt": self.now(),
                    })

            except Exception as e:
                print("Failed:", e)

    # -------------------------------------------------
    def run(self):
        self.scrape_greenhouse()

        print("\n[SOURCE SUMMARY]")
        for s, c in self.stats.items():
            print(f"{s}: {c}")

        print("\nTOTAL JOBS:", len(self.jobs))

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print("Saved → data/jobs.json")

# -------------------------------------------------
if __name__ == "__main__":
    s = JobScraper()
    s.run()
    s.save()
