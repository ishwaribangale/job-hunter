"""
PJIS – Fetch-First Job Scraper (Production Stable)
Phase: Ingestion + Post-Fetch Filters (FIXED)
"""

import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# -------------------------------------------------
# CONFIG: CURATED TOP COMPANIES
# -------------------------------------------------
TOP_COMPANIES = [
    {"name": "Stripe", "ats": "lever", "slug": "stripe"},
    {"name": "Razorpay", "ats": "lever", "slug": "razorpay"},
    {"name": "Paytm", "ats": "lever", "slug": "paytm"},
    {"name": "Notion", "ats": "lever", "slug": "notion"},
    {"name": "Figma", "ats": "lever", "slug": "figma"},
    {"name": "Airtable", "ats": "lever", "slug": "airtable"},

    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},
    {"name": "CRED", "ats": "greenhouse", "slug": "cred"},
    {"name": "Atlassian", "ats": "greenhouse", "slug": "atlassian"},
    {"name": "Freshworks", "ats": "greenhouse", "slug": "freshworks"},
    {"name": "Swiggy", "ats": "greenhouse", "slug": "swiggy"},
    {"name": "Zomato", "ats": "greenhouse", "slug": "zomato"},
    {"name": "Meesho", "ats": "greenhouse", "slug": "meesho"},
    {"name": "Flipkart", "ats": "greenhouse", "slug": "flipkart"},
    {"name": "Myntra", "ats": "greenhouse", "slug": "myntra"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PJISBot/1.0)"
}

# -------------------------------------------------
# FILTERS (POST FETCH)
# -------------------------------------------------
def filter_by_role(jobs):
    roles = [
        "product manager",
        "associate product manager",
        "apm",
        "product analyst",
        "business analyst",
        "product owner",
    ]
    return [
        j for j in jobs
        if any(r in (j.get("title") or "").lower() for r in roles)
    ]


def filter_remote(jobs):
    return [
        j for j in jobs
        if "remote" in (j.get("location") or "").lower()
    ]


def filter_top_companies(jobs):
    names = {c["name"].lower() for c in TOP_COMPANIES}
    return [
        j for j in jobs
        if (j.get("company") or "").lower() in names
    ]


def filter_recent(jobs, hours=48):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    out = []
    for j in jobs:
        try:
            dt = datetime.fromisoformat(j["postedDate"].replace("Z", ""))
            if dt >= cutoff:
                out.append(j)
        except Exception:
            pass
    return out


# -------------------------------------------------
# SCRAPER
# -------------------------------------------------
class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen_urls = set()
        self.source_count = {}

    def _now(self):
        return datetime.utcnow().isoformat()

    def _add_job(self, job):
        url = job.get("applyLink")
        if not url or url in self.seen_urls:
            return

        self.seen_urls.add(url)
        self.jobs.append(job)

        src = job.get("source", "Unknown")
        self.source_count[src] = self.source_count.get(src, 0) + 1

    # -------------------------------
    # SOURCES
    # -------------------------------
    def scrape_remotive(self):
        print("🌍 Scraping Remotive")
        res = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS, timeout=30)
        for job in res.json().get("jobs", []):
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

    def scrape_remoteok(self):
        print("🌍 Scraping RemoteOK")
        res = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=30)
        for job in res.json()[1:]:
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

    def scrape_yc_jobs(self):
        print("🌍 Scraping YC Jobs")
        html = requests.get("https://www.ycombinator.com/jobs", headers=HEADERS, timeout=30).text
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.select("a[href^='/jobs/']"):
            href = a.get("href")
            if not href:
                continue

            self._add_job({
                "id": f"yc_{hash(href)}",
                "title": a.get_text(strip=True),
                "company": None,
                "location": None,
                "source": "YCombinator",
                "applyLink": "https://www.ycombinator.com" + href,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })

    # -------------------------------
    # LEVER (FIXED)
    # -------------------------------
    def scrape_lever_company(self, company):
        base = "https://jobs.lever.co"
        url = f"{base}/{company['slug']}"

        print(f"🏢 [Lever] {company['name']}")

        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")

        postings = soup.select(
            "a.posting-title, div.posting a, a[data-qa='posting-name']"
        )

        print(f"   ↳ Found {len(postings)} postings")

        for a in postings:
            href = a.get("href")
            title = a.get_text(strip=True)

            if not href or not title:
                continue

            if not href.startswith("http"):
                href = base + href

            self._add_job({
                "id": f"lever_{company['slug']}_{hash(href)}",
                "title": title,
                "company": company["name"],
                "location": None,
                "source": "Company Career Page",
                "applyLink": href,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })

    # -------------------------------
    # GREENHOUSE
    # -------------------------------
    def scrape_greenhouse_company(self, company):
        base = "https://boards.greenhouse.io"
        url = f"{base}/{company['slug']}"

        print(f"🏢 [Greenhouse] {company['name']}")

        soup = BeautifulSoup(
            requests.get(url, headers=HEADERS, timeout=20).text,
            "html.parser"
        )

        for a in soup.select("a[href^='/jobs/']"):
            href = a.get("href")
            title = a.get_text(strip=True)

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

    def scrape_top_companies(self):
        print("🏢 Scraping Top Companies")
        for c in TOP_COMPANIES:
            if c["ats"] == "lever":
                self.scrape_lever_company(c)
            else:
                self.scrape_greenhouse_company(c)

    # -------------------------------
    # RUN + SAVE
    # -------------------------------
    def run(self):
        print("🚀 PJIS SCRAPER STARTED")

        self.scrape_remotive()
        self.scrape_remoteok()
        self.scrape_yc_jobs()
        self.scrape_top_companies()

        print("\n📊 SOURCE BREAKDOWN")
        for k, v in self.source_count.items():
            print(f"   {k}: {v}")

        print(f"\n✅ TOTAL JOBS: {len(self.jobs)}")

    def save(self):
        with open("data/jobs.json", "w") as f:
            json.dump(self.jobs, f, indent=2)

        with open("data/jobs_pm.json", "w") as f:
            json.dump(filter_by_role(self.jobs), f, indent=2)

        with open("data/jobs_remote.json", "w") as f:
            json.dump(filter_remote(self.jobs), f, indent=2)

        with open("data/jobs_recent.json", "w") as f:
            json.dump(filter_recent(self.jobs), f, indent=2)

        with open("data/jobs_top_companies.json", "w") as f:
            json.dump(filter_top_companies(self.jobs), f, indent=2)

        print("💾 Jobs saved (raw + filtered)")


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    s = JobScraper()
    s.run()
    s.save()
