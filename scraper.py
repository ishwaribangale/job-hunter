# PJIS - Job Intelligence Scraper (ATS API Edition)
# Reliable • Logged • Production Safe

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# -------------------------------------------------
# GLOBAL CONFIG
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
# COMPANY CONFIG (FIXED SLUGS)
# -------------------------------------------------
TOP_COMPANIES = [
    # Lever
    {"name": "Notion", "ats": "lever", "slug": "notion"},
    {"name": "Figma", "ats": "lever", "slug": "figma"},
    {"name": "Airtable", "ats": "lever", "slug": "airtable"},

    # Greenhouse
    {"name": "Stripe", "ats": "greenhouse", "slug": "stripeinc"},
    {"name": "Razorpay", "ats": "greenhouse", "slug": "razorpaysoftware"},
    {"name": "Atlassian", "ats": "greenhouse", "slug": "atlassian"},
    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},
    {"name": "CRED", "ats": "greenhouse", "slug": "cred"},
    {"name": "Freshworks", "ats": "greenhouse", "slug": "freshworks"},
    {"name": "Swiggy", "ats": "greenhouse", "slug": "swiggy"},
    {"name": "Zomato", "ats": "greenhouse", "slug": "zomato"},
    {"name": "Meesho", "ats": "greenhouse", "slug": "meesho"},
    {"name": "Flipkart", "ats": "greenhouse", "slug": "flipkart"},
    {"name": "Myntra", "ats": "greenhouse", "slug": "myntra"},
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
    # INTERNShala (SAFE)
    # -------------------------------------------------
    def scrape_internshala(self):
        print("\n[Internshala]")
        base = "https://internshala.com"
        urls = [
            f"{base}/jobs/product-manager-jobs",
            f"{base}/jobs/business-analyst-jobs",
        ]

        total = added = 0

        for url in urls:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(res.text, "html.parser")

            cards = soup.select(
                "div.individual_internship, div.container-fluid.individual_internship"
            )
            total += len(cards)

            for c in cards:
                title = c.select_one("h3.job-internship-name")
                link = c.select_one("a.view_detail_button, a.job-title-href")
                company = c.select_one("p.company-name")
                loc = c.select_one("span.location_link")

                if not title or not link or not company:
                    continue

                location = loc.get_text(strip=True) if loc else "Remote / Not specified"

                before = len(self.jobs)

                self.add({
                    "id": f"internshala_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": location,
                    "source": "Internshala",
                    "applyLink": base + link["href"],
                    "postedDate": self.now(),
                    "fetchedAt": self.now(),
                })

                if len(self.jobs) > before:
                    added += 1

        print(f"Cards found: {total}")
        print(f"Added: {added}")

    # -------------------------------------------------
    # ATS APIs (LEVER + GREENHOUSE)
    # -------------------------------------------------
    def scrape_ats(self):
        print("\n[Company Career Pages – ATS APIs]")

        for c in TOP_COMPANIES:
            print(f"\nCompany: {c['name']}")

            if c["ats"] == "lever":
                url = f"https://jobs.lever.co/{c['slug']}?mode=json"
                res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

                if "application/json" not in res.headers.get("Content-Type", ""):
                    print("Lever request failed (non-JSON)")
                    continue

                data = res.json()
                print(f"Lever jobs: {len(data)}")

                for j in data:
                    self.add({
                        "id": f"lever_{j.get('id')}",
                        "title": j.get("text"),
                        "company": c["name"],
                        "location": j.get("categories", {}).get("location"),
                        "source": f"{c['name']} (Lever)",
                        "applyLink": j.get("hostedUrl"),
                        "postedDate": self.now(),
                        "fetchedAt": self.now(),
                    })

            else:
                url = f"https://boards.greenhouse.io/{c['slug']}/jobs.json"
                res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

                if res.status_code != 200:
                    print("Greenhouse request failed")
                    continue

                data = res.json().get("jobs", [])
                print(f"Greenhouse jobs: {len(data)}")

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

    # -------------------------------------------------
    def run(self):
        self.scrape_internshala()
        self.scrape_ats()

        print("\n[SOURCE SUMMARY]")
        for s, c in self.stats.items():
            print(f"{s}: {c}")

        print("\nTOTAL JOBS:", len(self.jobs))

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print("Saved -> data/jobs.json")

# -------------------------------------------------
if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
