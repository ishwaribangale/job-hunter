"""
PJIS – DEBUG SCRAPER (LOUD LOGGING)
Purpose: Identify why jobs = 0
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import traceback

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

class JobScraper:
    def __init__(self):
        self.jobs = []

    # =========================================================
    # REMOTIVE DEBUG SCRAPER
    # =========================================================
    def scrape_remotive(self):
        print("\n==============================")
        print("🌍 REMOTIVE SCRAPER START")
        print("==============================")

        url = "https://remotive.com/api/remote-jobs"
        print(f"➡️ Requesting: {url}")

        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            print(f"✅ HTTP status: {res.status_code}")
        except Exception as e:
            print("❌ REQUEST FAILED")
            print(e)
            return

        print(f"📦 Response size: {len(res.text)} chars")

        try:
            data = res.json()
            print("✅ JSON parsed successfully")
        except Exception as e:
            print("❌ JSON PARSE FAILED")
            print(e)
            print(res.text[:500])
            return

        jobs_list = data.get("jobs", [])
        print(f"🔎 Jobs received from API: {len(jobs_list)}")

        added = 0
        skipped = 0

        for job in jobs_list[:50]:  # inspect first 50
            title = job.get("title", "")
            location = job.get("candidate_required_location", "")

            print("\n--- JOB ---")
            print(f"Title: {title}")
            print(f"Company: {job.get('company_name')}")
            print(f"Location: {location}")

            # TEMPORARILY DISABLE FILTERS
            self.jobs.append({
                "id": f"remotive_{job.get('id')}",
                "title": title,
                "company": job.get("company_name"),
                "location": location,
                "remote": True,
                "remoteType": "unknown",
                "role": "Unknown",
                "source": "Remotive",
                "applyLink": job.get("url"),
                "postedDate": job.get("publication_date"),
                "fetchedAt": self._now()
            })
            added += 1

        print(f"\n✅ REMOTIVE JOBS ADDED (NO FILTERS): {added}")
        print("==============================")

    # =========================================================
    # WE WORK REMOTELY DEBUG SCRAPER
    # =========================================================
    def scrape_weworkremotely(self):
        print("\n==============================")
        print("🌍 WE WORK REMOTELY SCRAPER START")
        print("==============================")

        url = "https://weworkremotely.com/categories/remote-product-jobs"
        print(f"➡️ Requesting: {url}")

        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            print(f"✅ HTTP status: {res.status_code}")
            print(f"📦 HTML size: {len(res.text)} chars")
        except Exception as e:
            print("❌ REQUEST FAILED")
            print(e)
            return

        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("section.jobs li a")

        print(f"🔎 Job link elements found: {len(links)}")

        added = 0

        for li in links[:20]:
            title_el = li.find("span", class_="title")
            company_el = li.find("span", class_="company")

            if not title_el or not company_el:
                print("⚠️ Missing title or company")
                continue

            title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True)
            job_url = "https://weworkremotely.com" + li.get("href")

            print("\n--- JOB ---")
            print(f"Title: {title}")
            print(f"Company: {company}")
            print(f"URL: {job_url}")

            self.jobs.append({
                "id": f"wwr_{hash(job_url)}",
                "title": title,
                "company": company,
                "location": "Remote",
                "remote": True,
                "remoteType": "global",
                "role": "Unknown",
                "source": "WeWorkRemotely",
                "applyLink": job_url,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })
            added += 1

        print(f"\n✅ WWR JOBS ADDED (NO FILTERS): {added}")
        print("==============================")

    def _now(self):
        return datetime.utcnow().isoformat()

    # =========================================================
    # RUNNER
    # =========================================================
    def run(self):
        print("\n🚀 PJIS DEBUG SCRAPER STARTED")
        print("====================================")

        try:
            self.scrape_remotive()
        except Exception:
            print("🔥 REMOTIVE CRASHED")
            traceback.print_exc()

        try:
            self.scrape_weworkremotely()
        except Exception:
            print("🔥 WWR CRASHED")
            traceback.print_exc()

        print("\n====================================")
        print(f"✅ TOTAL JOBS COLLECTED: {len(self.jobs)}")
        print("====================================")

        return self.jobs

    def save(self, filename="jobs_data.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved {len(self.jobs)} jobs to {filename}")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
