"""
PJIS – Fetch-First Job Scraper (Production Stable)
Phase: Ingestion Only (Filters applied later)
"""

import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# -------------------------------------------------
# CONFIG: CURATED TOP COMPANIES (EXPAND TO 50+)
# -------------------------------------------------
TOP_COMPANIES = [
    # Fintech / Payments
    {"name": "Stripe", "ats": "lever", "slug": "stripe"},
    {"name": "Razorpay", "ats": "lever", "slug": "razorpay"},
    {"name": "Paytm", "ats": "lever", "slug": "paytm"},
    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},
    {"name": "CRED", "ats": "greenhouse", "slug": "cred"},

    # SaaS / Dev Tools
    {"name": "Notion", "ats": "lever", "slug": "notion"},
    {"name": "Figma", "ats": "lever", "slug": "figma"},
    {"name": "Airtable", "ats": "lever", "slug": "airtable"},
    {"name": "Atlassian", "ats": "greenhouse", "slug": "atlassian"},
    {"name": "Freshworks", "ats": "greenhouse", "slug": "freshworks"},

    # Consumer / Marketplaces
    {"name": "Swiggy", "ats": "greenhouse", "slug": "swiggy"},
    {"name": "Zomato", "ats": "greenhouse", "slug": "zomato"},
    {"name": "Meesho", "ats": "greenhouse", "slug": "meesho"},
    {"name": "Flipkart", "ats": "greenhouse", "slug": "flipkart"},
    {"name": "Myntra", "ats": "greenhouse", "slug": "myntra"},
]

# -------------------------------------------------
# SCRAPER
# -------------------------------------------------
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
    # LEVER (COMPANY CAREER PAGES)
    # -------------------------------
    def scrape_lever_company(self, company):
        base = "https://jobs.lever.co"
        url = f"{base}/{company['slug']}"

        print(f"🏢 Scraping Lever: {company['name']}")

        try:
            res = requests.get(url, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
            postings = soup.select("a.posting-title")

            count = 0
            for post in postings:
                href = post.get("href")
                title = post.get_text(strip=True)

                if not href:
                    continue

                self._add_job({
                    "id": f"lever_{company['slug']}_{hash(href)}",
                    "title": title,
                    "company": company["name"],
                    "location": None,
                    "source": "Company Career Page",
                    "applyLink": base + href,
                    "postedDate": self._now(),
                    "fetchedAt": self._now()
                })
                count += 1

            print(f"✅ {company['name']} jobs added: {count}")
        except Exception as e:
            print(f"⚠️ Lever failed for {company['name']}: {e}")

    # -------------------------------
    # GREENHOUSE (COMPANY CAREER PAGES)
    # -------------------------------
    def scrape_greenhouse_company(self, company):
        base = "https://boards.greenhouse.io"
        url = f"{base}/{company['slug']}"

        print(f"🏢 Scraping Greenhouse: {company['name']}")

        try:
            res = requests.get(url, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
            postings = soup.select("a[href*='/jobs/']")

            count = 0
            for post in postings:
                href = post.get("href")
                title = post.get_text(strip=True)

                if not href or not title:
                    continue

                self._add_job({
                    "id": f"gh_{company['slug']}_{hash(href)}",
                    "title": title,
                    "company": company["name"],
                    "location": None,
                    "source": "Company Career Page",
                    "applyLink": base + href,
                    "postedDate": self._now(),
                    "fetchedAt": self._now()
                })
                count += 1

            print(f"✅ {company['name']} jobs added: {count}")
        except Exception as e:
            print(f"⚠️ Greenhouse failed for {company['name']}: {e}")

    # -------------------------------
    # TOP COMPANIES MASTER
    # -------------------------------
    def scrape_top_companies(self):
        print("🏢 Scraping Top Company Career Pages")

        for company in TOP_COMPANIES:
            if company["ats"] == "lever":
                self.scrape_lever_company(company)
            elif company["ats"] == "greenhouse":
                self.scrape_greenhouse_company(company)

    # -------------------------------
    # RUNNER
    # -------------------------------
    def run(self):
        print("🚀 PJIS SCRAPER STARTED (FETCH-FIRST MODE)")

        self.scrape_remotive()
        self.scrape_remoteok()
        self.scrape_yc_jobs()
        self.scrape_top_companies()

        print(f"✅ TOTAL JOBS COLLECTED: {len(self.jobs)}")

    def save(self):
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)

        print("💾 Jobs saved to data/jobs.json")


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
