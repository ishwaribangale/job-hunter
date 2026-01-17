"""
Personal Job Intelligence System (PJIS)
Final Scraper – Remote Jobs Only
Author: Ishwari Bangale
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}


class JobScraper:
    def __init__(self):
        self.jobs = []

    # =========================================================
    # REMOTIVE (API – REMOTE ONLY)
    # =========================================================
    def scrape_remotive(self):
        print("\n🌍 Scraping Remotive (remote-only)")
        url = "https://remotive.com/api/remote-jobs"

        try:
            res = requests.get(url, timeout=20)
            data = res.json()
        except Exception as e:
            print("❌ Remotive failed:", e)
            return

        for job in data.get("jobs", []):
            title = job.get("title", "")
            if not self._is_pm_role(title):
                continue

            location = job.get("candidate_required_location", "")
            remote_type = self._infer_remote_type(location)

            if not self._is_remote_allowed(remote_type):
                continue

            self.jobs.append(self._build_job(
                source="Remotive",
                job_id=f"remotive_{job['id']}",
                title=title,
                company=job.get("company_name"),
                location=location or "Remote",
                apply_link=job.get("url"),
                role=self._infer_role(title),
                remote_type=remote_type,
                posted_date=job.get("publication_date")
            ))

    # =========================================================
    # WE WORK REMOTELY (HTML – GLOBAL REMOTE)
    # =========================================================
    def scrape_weworkremotely(self):
        print("\n🌍 Scraping WeWorkRemotely (global remote)")
        url = "https://weworkremotely.com/categories/remote-product-jobs"

        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print("❌ WeWorkRemotely failed:", e)
            return

        for li in soup.select("section.jobs li a"):
            title_el = li.find("span", class_="title")
            company_el = li.find("span", class_="company")

            if not title_el or not company_el:
                continue

            title = title_el.get_text(strip=True)
            if not self._is_pm_role(title):
                continue

            job_url = "https://weworkremotely.com" + li.get("href")

            self.jobs.append(self._build_job(
                source="WeWorkRemotely",
                job_id=f"wwr_{hash(job_url)}",
                title=title,
                company=company_el.get_text(strip=True),
                location="Remote",
                apply_link=job_url,
                role=self._infer_role(title),
                remote_type="global",
                posted_date=self._now()
            ))

    # =========================================================
    # GOOGLE-INDEXED LINKEDIN HIRING POSTS (REMOTE ONLY)
    # =========================================================
    def scrape_linkedin_google(self):
        print("\n🌍 Scanning Google-indexed LinkedIn hiring posts")

        query = 'site:linkedin.com/posts ("hiring" OR "we are hiring") "product" remote'
        url = f"https://www.google.com/search?q={query}"

        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print("❌ LinkedIn Google scan failed:", e)
            return

        for a in soup.select("a"):
            href = a.get("href", "")
            if "linkedin.com/posts" not in href:
                continue

            clean_url = href.split("&")[0].replace("/url?q=", "")
            if not clean_url.startswith("http"):
                continue

            self.jobs.append(self._build_job(
                source="LinkedIn (Public Post)",
                job_id=f"linkedin_{hash(clean_url)}",
                title="Hiring – Product Role (Remote)",
                company=None,
                location="Remote",
                apply_link=clean_url,
                role="Product",
                remote_type="global",
                posted_date=self._now()
            ))

    # =========================================================
    # HELPERS
    # =========================================================
    def _build_job(self, source, job_id, title, company, location,
                   apply_link, role, remote_type, posted_date):

        return {
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "remote": True,
            "remoteType": remote_type,
            "role": role,
            "source": source,
            "applyLink": apply_link,
            "postedDate": posted_date,
            "fetchedAt": self._now()
        }

    def _is_pm_role(self, title):
        keywords = ["product", "apm", "pm", "product analyst", "product ops"]
        return any(k in title.lower() for k in keywords)

    def _infer_role(self, title):
        t = title.lower()
        if "analyst" in t:
            return "Product Analyst"
        if "associate" in t or "apm" in t:
            return "APM"
        return "Product Manager"

    def _infer_remote_type(self, location_text):
        if not location_text:
            return "global"

        text = location_text.lower()
        if "india" in text:
            return "india"
        if "remote" in text or "anywhere" in text or "global" in text:
            return "global"

        return "unknown"

    def _is_remote_allowed(self, remote_type):
        return remote_type in ["global", "india"]

    def _now(self):
        return datetime.utcnow().isoformat()

    # =========================================================
    # RUNNER
    # =========================================================
    def run(self):
        print("\n🚀 PJIS SCRAPER STARTED\n")

        self.scrape_remotive()
        self.scrape_weworkremotely()
        self.scrape_linkedin_google()

        print(f"\n✅ TOTAL REMOTE JOBS FOUND: {len(self.jobs)}")
        return self.jobs

    def save(self, filename="jobs_data.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(self.jobs)} jobs to {filename}")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()

