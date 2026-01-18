"""
PJIS – Fetch-First Job Scraper (Production Stable)
Phase: Ingestion + Post-Fetch Filters
"""

import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PJISBot/1.0)"
}

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

# -------------------------------------------------
# FILTERS (POST FETCH)
# -------------------------------------------------
def filter_by_role(jobs):
    keywords = [
        "product", "growth", "platform",
        "business analyst", "systems analyst",
        "strategy", "monetization", "gtm"
    ]
    return [
        j for j in jobs
        if any(k in (j.get("title") or "").lower() for k in keywords)
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
    # REMOTIVE
    # -------------------------------
    def scrape_remotive(self):
        print("🌍 Remotive")
        res = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS, timeout=30)
        for j in res.json().get("jobs", []):
            self._add_job({
                "id": f"remotive_{j['id']}",
                "title": j.get("title"),
                "company": j.get("company_name"),
                "location": j.get("candidate_required_location") or "Remote",
                "source": "Remotive",
                "applyLink": j.get("url"),
                "postedDate": j.get("publication_date"),
                "fetchedAt": self._now(),
            })

    # -------------------------------
    # REMOTEOK
    # -------------------------------
    def scrape_remoteok(self):
        print("🌍 RemoteOK")
        res = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=30)
        for j in res.json()[1:]:
            self._add_job({
                "id": f"remoteok_{j.get('id')}",
                "title": j.get("position"),
                "company": j.get("company"),
                "location": "Remote",
                "source": "RemoteOK",
                "applyLink": j.get("url"),
                "postedDate": self._now(),
                "fetchedAt": self._now(),
            })

    # -------------------------------
    # YC JOBS
    # -------------------------------
    def scrape_yc_jobs(self):
        print("🌍 Y Combinator")
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
                "source": "Y Combinator",
                "applyLink": "https://www.ycombinator.com" + href,
                "postedDate": self._now(),
                "fetchedAt": self._now(),
            })

    # -------------------------------
    # INTERNShala
    # -------------------------------
    def scrape_internshala(self):
        print("🌍 Internshala")
        base = "https://internshala.com"
        urls = [
            f"{base}/jobs/product-manager-jobs",
            f"{base}/jobs/business-analyst-jobs",
            f"{base}/jobs/analytics-jobs",
        ]

        for url in urls:
            try:
                soup = BeautifulSoup(
                    requests.get(url, headers=HEADERS, timeout=30).text,
                    "html.parser"
                )

                for card in soup.select("div.individual_internship"):
                    title = card.select_one("h3.job-internship-name")
                    company = card.select_one("p.company-name")
                    location = card.select_one("span.location_link")
                    link = card.select_one("a.view_detail_button")

                    if not title or not link:
                        continue

                    self._add_job({
                        "id": f"internshala_{hash(link.get('href'))}",
                        "title": title.get_text(strip=True),
                        "company": company.get_text(strip=True) if company else None,
                        "location": location.get_text(strip=True) if location else None,
                        "source": "Internshala",
                        "applyLink": base + link.get("href"),
                        "postedDate": self._now(),
                        "fetchedAt": self._now(),
                    })
            except Exception as e:
                print("⚠️ Internshala error:", e)

    # -------------------------------
    # COMPANY ATS
    # -------------------------------
    def scrape_top_companies(self):
        print("🏢 Company Career Pages")
        for c in TOP_COMPANIES:
            if c["ats"] == "lever":
                url = f"https://jobs.lever.co/{c['slug']}"
                soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
                for a in soup.select("a.posting-title"):
                    self._add_job({
                        "id": f"lever_{hash(a.get('href'))}",
                        "title": a.get_text(strip=True),
                        "company": c["name"],
                        "location": None,
                        "source": "Company Career Page",
                        "applyLink": "https://jobs.lever.co" + a.get("href"),
                        "postedDate": self._now(),
                        "fetchedAt": self._now(),
                    })

            if c["ats"] == "greenhouse":
                url = f"https://boards.greenhouse.io/{c['slug']}"
                soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser")
                for a in soup.select("a[href^='/jobs/']"):
                    self._add_job({
                        "id": f"gh_{hash(a.get('href'))}",
                        "title": a.get_text(strip=True),
                        "company": c["name"],
                        "location": None,
                        "source": "Company Career Page",
                        "applyLink": "https://boards.greenhouse.io" + a.get("href"),
                        "postedDate": self._now(),
                        "fetchedAt": self._now(),
                    })

    # -------------------------------
    # RUN + SAVE
    # -------------------------------
    def run(self):
        self.scrape_remotive()
        self.scrape_remoteok()
        self.scrape_yc_jobs()
        self.scrape_internshala()
        self.scrape_top_companies()

        print("\n📊 SOURCE BREAKDOWN")
        for s, c in self.source_count.items():
            print(f"{s}: {c}")

        print("TOTAL:", len(self.jobs))

    def save(self):
        with open("data/jobs.json", "w") as f:
            json.dump(self.jobs, f, indent=2)

        with open("data/jobs_product.json", "w") as f:
            json.dump(filter_by_role(self.jobs), f, indent=2)

        with open("data/jobs_recent.json", "w") as f:
            json.dump(filter_recent(self.jobs), f, indent=2)

        print("💾 Saved all job views")


if __name__ == "__main__":
    s = JobScraper()
    s.run()
    s.save()
