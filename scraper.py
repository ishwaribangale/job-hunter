"""
PJIS – Fetch-First Job Scraper (Stable, CI-Compatible)
Phase: Ingestion Only (No Filtering)
"""

import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup


class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen_urls = set()

    # -------------------------------
    # UTIL
    # -------------------------------
    def _now(self):
        return datetime.utcnow().isoformat()

    def _add_job(self, job):
        """Deduplicate by apply link"""
        url = job.get("applyLink")
        if not url or url in self.seen_urls:
            return
        self.seen_urls.add(url)
        self.jobs.append(job)

    # -------------------------------
    # REMOTIVE (API – BROAD)
    # -------------------------------
    def scrape_remotive(self):
        print("🌍 Scraping Remotive (API)")
        res = requests.get("https://remotive.com/api/remote-jobs", timeout=30)
        data = res.json()

        count = 0
        for job in data.get("jobs", []):
            self._add_job({
                "id": f"remotive_{job['id']}",
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location") or "Remote",
                "source": "Remotive",
                "applyLink": job.get("url"),
                "postedDate": job.get("publication_date"),
                "fetchedAt": self._now(),
                "raw": job
            })
            count += 1

        print(f"✅ Remotive jobs added: {count}")

    # -------------------------------
    # REMOTEOK (JSON – BROAD)
    # -------------------------------
    def scrape_remoteok(self):
        print("🌍 Scraping RemoteOK")
        res = requests.get("https://remoteok.com/api", timeout=30)
        data = res.json()

        count = 0
        for job in data[1:]:
            self._add_job({
                "id": f"remoteok_{job.get('id')}",
                "title": job.get("position"),
                "company": job.get("company"),
                "location": "Remote",
                "source": "RemoteOK",
                "applyLink": job.get("url"),
                "postedDate": self._now(),
                "fetchedAt": self._now(),
                "raw": job
            })
            count += 1

        print(f"✅ RemoteOK jobs added: {count}")

    # -------------------------------
    # YC JOBS (STATIC HTML – BROAD)
    # -------------------------------
    def scrape_yc_jobs(self):
        print("🌍 Scraping Y Combinator Jobs")
        res = requests.get("https://www.ycombinator.com/jobs", timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("a[href^='/jobs/']")
        count = 0

        for a in links:
            href = a.get("href")
            title = a.get_text(strip=True)

            if not href or not title:
                continue

            self._add_job({
                "id": f"yc_{hash(href)}",
                "title": title,
                "company": None,
                "location": None,
                "source": "YCombinator",
                "applyLink": "https://www.ycombinator.com" + href,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ YC jobs added: {count}")

    # -------------------------------
    # LEVER (GLOBAL ATS – BROAD)
    # -------------------------------
    def scrape_lever(self):
        print("🌍 Scraping Lever (Global)")
        base = "https://jobs.lever.co"
        companies = ["stripe", "notion", "figma", "airtable", "coinbase"]

        count = 0
        for company in companies:
            try:
                res = requests.get(f"{base}/{company}", timeout=20)
                soup = BeautifulSoup(res.text, "html.parser")
                links = soup.select("a.posting-title")

                for a in links:
                    href = a.get("href")
                    title = a.get_text(strip=True)

                    if not href:
                        continue

                    self._add_job({
                        "id": f"lever_{company}_{hash(href)}",
                        "title": title,
                        "company": company.title(),
                        "location": None,
                        "source": "Lever",
                        "applyLink": base + href,
                        "postedDate": self._now(),
                        "fetchedAt": self._now()
                    })
                    count += 1
            except Exception:
                continue

        print(f"✅ Lever jobs added: {count}")

    # -------------------------------
    # RUNNER
    # -------------------------------
    def run(self):
        print("🚀 PJIS SCRAPER STARTED (FETCH-FIRST MODE)")

        self.scrape_remotive()
        self.scrape_remoteok()
        self.scrape_yc_jobs()
        self.scrape_lever()

        print(f"✅ TOTAL JOBS COLLECTED: {len(self.jobs)}")

    def save(self):
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)

        print("💾 Jobs saved to data/jobs.json")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
