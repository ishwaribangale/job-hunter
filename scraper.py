# scraper.py
# ----------------------------------
# PJIS – Job Intelligence Scraper
# ----------------------------------

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from config import HEADERS, TIMEOUT, TOP_COMPANIES
from roles import infer_role
from scoring import score_job


class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen = set()
        self.stats = {}

    def now(self):
        return datetime.utcnow().isoformat()

    def add(self, job):
        link = job.get("applyLink")
        if not link or link in self.seen:
            return

        job["role"] = infer_role(job.get("title"))
        job["score"] = score_job(job)
        job["fetchedAt"] = self.now()

        self.seen.add(link)
        self.jobs.append(job)

        src = job["source"]
        self.stats[src] = self.stats.get(src, 0) + 1

    # ----------------------------------
    # REMOTIVE
    # ----------------------------------
    def scrape_remotive(self):
        print("\n[Remotive]")
        try:
            r = requests.get(
                "https://remotive.com/api/remote-jobs",
                headers=HEADERS,
                timeout=TIMEOUT
            )
            data = r.json().get("jobs", [])
        except Exception as e:
            print("Remotive failed:", e)
            return

        for j in data:
            self.add({
                "id": f"remotive_{j['id']}",
                "title": j["title"],
                "company": j["company_name"],
                "location": j.get("candidate_required_location"),
                "source": "Remotive",
                "applyLink": j["url"],
                "postedDate": j["publication_date"]
            })

    # ----------------------------------
    # INTERNShala (Hidden-ish jobs)
    # ----------------------------------
    def scrape_internshala(self):
        print("\n[Internshala]")
        base = "https://internshala.com"
        urls = [
            f"{base}/jobs/product-manager-jobs",
            f"{base}/jobs/business-analyst-jobs",
        ]

        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")

            for c in soup.select("div.individual_internship"):
                title = c.select_one("h3.job-internship-name")
                company = c.select_one("p.company-name")
                link = c.select_one("a.view_detail_button")

                if not title or not company or not link:
                    continue

                self.add({
                    "id": f"internshala_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "India",
                    "source": "Internshala",
                    "applyLink": base + link["href"],
                    "postedDate": self.now()
                })

    # ----------------------------------
    # ATS SCRAPER (Hidden Jobs CORE)
    # ----------------------------------
    def scrape_ats(self):
        print("\n[ATS Jobs]")

        for c in TOP_COMPANIES:
            print(f"Company: {c['name']}")

            if c["ats"] == "lever":
                url = f"https://jobs.lever.co/{c['slug']}?mode=json"
                r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                if "json" not in r.headers.get("Content-Type", ""):
                    continue

                for j in r.json():
                    self.add({
                        "id": f"lever_{j['id']}",
                        "title": j["text"],
                        "company": c["name"],
                        "location": j["categories"].get("location"),
                        "source": f"{c['name']} (Lever)",
                        "applyLink": j["hostedUrl"],
                        "postedDate": self.now()
                    })

            else:
                url = f"https://boards.greenhouse.io/{c['slug']}/jobs.json"
                r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                if r.status_code != 200:
                    continue

                for j in r.json().get("jobs", []):
                    self.add({
                        "id": f"gh_{j['id']}",
                        "title": j["title"],
                        "company": c["name"],
                        "location": j["location"]["name"],
                        "source": f"{c['name']} (Greenhouse)",
                        "applyLink": j["absolute_url"],
                        "postedDate": self.now()
                    })

    # ----------------------------------
    # RUN + SAVE
    # ----------------------------------
    def run(self):
        self.scrape_remotive()
        self.scrape_internshala()
        self.scrape_ats()

        print("\n[SOURCES]")
        for k, v in self.stats.items():
            print(f"{k}: {v}")

        print("TOTAL JOBS:", len(self.jobs))

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(
                sorted(self.jobs, key=lambda x: x["score"], reverse=True),
                f,
                indent=2,
                ensure_ascii=False
            )
        print("Saved → data/jobs.json")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()

