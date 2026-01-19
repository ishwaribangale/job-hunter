# PJIS - Job Intelligence Scraper (Greenhouse - Corrected)
# Safe for GitHub Actions, CI, and production use

import os
import json
import requests
from datetime import datetime

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
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
# SCRAPER
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
        if not url:
            return
        if url in self.seen:
            return

        self.seen.add(url)
        self.jobs.append(job)

        source = job.get("source", "unknown")
        self.stats[source] = self.stats.get(source, 0) + 1

    # -------------------------------------------------
    # GREENHOUSE SCRAPER
    # -------------------------------------------------
    def scrape_greenhouse(self):
        print("\n[Greenhouse ATS]")

        for company in TOP_COMPANIES:
            name = company["name"]
            slug = company["slug"]

            print(f"\nCompany: {name}")

            url = f"https://boards.greenhouse.io/{slug}/jobs.json"

            try:
                response = requests.get(
                    url,
                    headers=HEADERS,
                    timeout=TIMEOUT
                )
                response.raise_for_status()

                payload = response.json()
                jobs = payload.get("jobs", [])

                print(f"Jobs found: {len(jobs)}")

                for job in jobs:
                    self.add({
                        "id": f"gh_{job.get('id')}",
                        "title": job.get("title"),
                        "company": name,
                        "location": job.get("location", {}).get("name"),
                        "source": f"{name} (Greenhouse)",
                        "applyLink": job.get("absolute_url"),
                        "postedDate": self.now(),
                        "fetchedAt": self.now(),
                    })

            except requests.exceptions.HTTPError as e:
                print("HTTP error:", e)
            except requests.exceptions.RequestException as e:
                print("Network error:", e)
            except ValueError as e:
                print("JSON decode error:", e)
            except Exception as e:
                print("Unexpected error:", e)

    # -------------------------------------------------
    def run(self):
        self.scrape_greenhouse()

        print("\n[SOURCE SUMMARY]")
        for source, count in self.stats.items():
            print(f"{source}: {count}")

        print("\nTOTAL JOBS:", len(self.jobs))

    def save(self):
        os.makedirs("data", exist_ok=True)

        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)

        print("Saved -> data/jobs.json")

# -------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------
if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
