"""
Personal Job Intelligence System (PJIS)
STABLE WORKING SCRAPER (Remote Jobs)
Author: Ishwari Bangale
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}


class JobScraper:
    def __init__(self):
        self.jobs = []

    # =========================================================
    # REMOTIVE (API – PRIMARY & RELIABLE)
    # =========================================================
    def scrape_remotive(self):
        print("\n🌍 Scraping Remotive (API – reliable)")

        url = "https://remotive.com/api/remote-jobs"

        try:
            res = requests.get(url, timeout=30)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            print("❌ Remotive API failed:", e)
            return

        print(f"🔎 Total jobs received from API: {len(data.get('jobs', []))}")

        for job in data.get("jobs", []):
            title = job.get("title", "").lower()

            # Relaxed but safe PM filter
            if not any(k in title for k in [
                "product",
                "pm",
                "apm",
                "product manager",
                "product analyst",
                "product owner"
            ]):
                continue

            location = job.get("candidate_required_location", "")
            remote_type = self._infer_remote_type(location)

            if remote_type not in ["global", "india"]:
                continue

            self.jobs.append({
                "id": f"remotive_{job['id']}",
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": location or "Remote",
                "remote": True,
                "remoteType": remote_type,
                "role": self._infer_role(job.get("title")),
                "source": "Remotive",
                "applyLink": job.get("url"),
                "postedDate": job.get("publication_date"),
                "fetchedAt": self._now()
            })

        print(f"✅ Remotive jobs added: {len(self.jobs)}")

    # =========================================================
    # WE WORK REMOTELY (HTML – SECONDARY)
    # =========================================================
    def scrape_weworkremotely(self):
        print("\n🌍 Scraping WeWorkRemotely")

        url = "https://weworkremotely.com/categories/remote-product-jobs"

        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print("❌ WWR failed:", e)
            return

        count = 0

        for li in soup.select("section.jobs li a"):
            title_el = li.find("span", class_="title")
            company_el = li.find("span", class_="company")

            if not title_el or not company_el:
                continue

            title = title_el.get_text(strip=True)

            if not any(k in title.lower() for k in ["product", "pm", "analyst"]):
                continue

            job_url = "https://weworkremotely.com" + li.get("href")

            self.jobs.append({
                "id": f"wwr_{hash(job_url)}",
                "title": title,
                "company": company_el.get_text(strip=True),
                "location": "Remote",
                "remote": True,
                "remoteType": "global",
                "role": self._infer_role(title),
                "source": "WeWorkRemotely",
                "applyLink": job_url,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })

            count += 1

        print(f"✅ WeWorkRemotely jobs added: {count}")

    # =========================================================
    # HELPERS
    # =========================================================
    def _infer_role(self, title):
        t = title.lower()
        if "analyst" in t:
            return "Product Analyst"
        if "apm" in t or "associate" in t:
            return "APM"
        return "Product Manager"

    def _infer_remote_type(self, location):
        if not location:
            return "global"

        text = location.lower()
        if "india" in text:
            return "india"
        if "remote" in text or "anywhere" in text or "global" in text:
            return "global"

        return "unknown"

    def _now(self):
        return datetime.utcnow().isoformat()

    # =========================================================
    # RUNNER
    # =========================================================
    def run(self):
        print("\n🚀 PJIS SCRAPER STARTED\n")

        self.scrape_remotive()
        self.scrape_weworkremotely()

        print("\n==============================")
        print(f"✅ TOTAL JOBS FOUND: {len(self.jobs)}")
        print("==============================\n")

        return self.jobs

    def save(self, filename="jobs_data.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(self.jobs)} jobs to {filename}")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
