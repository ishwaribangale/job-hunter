"""
PJIS – Fetch-First Job Scraper (Production Stable)
"""

import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)"
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
]

def filter_product(jobs):
    keys = ["product", "growth", "platform", "gtm", "strategy", "analyst"]
    return [j for j in jobs if any(k in (j["title"] or "").lower() for k in keys)]

def filter_recent(jobs, hours=48):
    cut = datetime.utcnow() - timedelta(hours=hours)
    out = []
    for j in jobs:
        try:
            if datetime.fromisoformat(j["postedDate"]) >= cut:
                out.append(j)
        except:
            pass
    return out


class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen = set()
        self.stats = {}

    def now(self):
        return datetime.utcnow().isoformat()

    def add(self, job):
        if not job.get("applyLink") or job["applyLink"] in self.seen:
            return False
        self.seen.add(job["applyLink"])
        self.jobs.append(job)
        self.stats[job["source"]] = self.stats.get(job["source"], 0) + 1
        return True

    # ---------------- REMOTIVE ----------------
    def scrape_remotive(self):
        print("\n[Remotive]")
        added = 0
        r = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS)
        for j in r.json().get("jobs", []):
            if self.add({
                "id": f"remotive_{j['id']}",
                "title": j["title"],
                "company": j["company_name"],
                "location": j.get("candidate_required_location") or "Remote",
                "source": "Remotive",
                "applyLink": j["url"],
                "postedDate": j["publication_date"],
                "fetchedAt": self.now(),
            }):
                added += 1
        print("Added:", added)

    # ---------------- REMOTEOK ----------------
    def scrape_remoteok(self):
        print("\n[RemoteOK]")
        added = 0
        r = requests.get("https://remoteok.com/api", headers=HEADERS)
        for j in r.json()[1:]:
            if self.add({
                "id": f"remoteok_{j['id']}",
                "title": j["position"],
                "company": j["company"],
                "location": "Remote",
                "source": "RemoteOK",
                "applyLink": j["url"],
                "postedDate": self.now(),
                "fetchedAt": self.now(),
            }):
                added += 1
        print("Added:", added)

    # ---------------- YC JOBS ----------------
    def scrape_yc(self):
        print("\n[Y Combinator]")
        soup = BeautifulSoup(
            requests.get("https://www.ycombinator.com/jobs", headers=HEADERS).text,
            "html.parser"
        )
        links = soup.select("a[href^='/jobs/']")
        print("Found:", len(links))
        added = 0
        for a in links:
            if self.add({
                "id": f"yc_{hash(a['href'])}",
                "title": a.get_text(strip=True),
                "company": None,
                "location": None,
                "source": "Y Combinator",
                "applyLink": "https://www.ycombinator.com" + a["href"],
                "postedDate": self.now(),
                "fetchedAt": self.now(),
            }):
                added += 1
        print("Added:", added)

    # ---------------- INTERNSHALA (RESTORED) ----------------
    def scrape_internshala(self):
        print("\n[Internshala]")
        base = "https://internshala.com"
        urls = [
            f"{base}/jobs/product-manager-jobs",
            f"{base}/jobs/business-analyst-jobs",
            f"{base}/jobs/analytics-jobs",
        ]

        added = 0
        cards_seen = 0

        for url in urls:
            soup = BeautifulSoup(
                requests.get(url, headers=HEADERS).text,
                "html.parser"
            )
            cards = soup.select("div.individual_internship")
            cards_seen += len(cards)

            for c in cards:
                title = c.select_one("h3.job-internship-name")
                link = c.select_one("a.view_detail_button")
                company = c.select_one("p.company-name")
                location = c.select_one("span.location_link")

                if not title or not link:
                    continue

                if self.add({
                    "id": f"internshala_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True) if company else None,
                    "location": location.get_text(strip=True) if location else None,
                    "source": "Internshala",
                    "applyLink": base + link["href"],
                    "postedDate": self.now(),
                    "fetchedAt": self.now(),
                }):
                    added += 1

        print("Cards found:", cards_seen)
        print("Added:", added)

    # ---------------- COMPANY PAGES ----------------
    def scrape_companies(self):
        print("\n[Company Career Pages]")
        for c in TOP_COMPANIES:
            print("Company:", c["name"])
            added = 0

            if c["ats"] == "lever":
                soup = BeautifulSoup(
                    requests.get(f"https://jobs.lever.co/{c['slug']}", headers=HEADERS).text,
                    "html.parser"
                )
                posts = soup.select("a.posting-title")
                print(" Lever found:", len(posts))
                for a in posts:
                    if self.add({
                        "id": f"lever_{hash(a['href'])}",
                        "title": a.get_text(strip=True),
                        "company": c["name"],
                        "location": None,
                        "source": "Company Career Page",
                        "applyLink": "https://jobs.lever.co" + a["href"],
                        "postedDate": self.now(),
                        "fetchedAt": self.now(),
                    }):
                        added += 1

            if c["ats"] == "greenhouse":
                soup = BeautifulSoup(
                    requests.get(f"https://boards.greenhouse.io/{c['slug']}", headers=HEADERS).text,
                    "html.parser"
                )
                posts = soup.select("a[href^='/jobs/']")
                print(" Greenhouse found:", len(posts))
                for a in posts:
                    if self.add({
                        "id": f"gh_{hash(a['href'])}",
                        "title": a.get_text(strip=True),
                        "company": c["name"],
                        "location": None,
                        "source": "Company Career Page",
                        "applyLink": "https://boards.greenhouse.io" + a["href"],
                        "postedDate": self.now(),
                        "fetchedAt": self.now(),
                    }):
                        added += 1

            print(" Added:", added)

    # ---------------- RUN ----------------
    def run(self):
        self.scrape_remotive()
        self.scrape_remoteok()
        self.scrape_yc()
        self.scrape_internshala()
        self.scrape_companies()

        print("\nSOURCE SUMMARY")
        for k, v in self.stats.items():
            print(k, ":", v)
        print("TOTAL JOBS:", len(self.jobs))

    def save(self):
        with open("data/jobs.json", "w") as f:
            json.dump(self.jobs, f, indent=2)

        with open("data/jobs_product.json", "w") as f:
            json.dump(filter_product(self.jobs), f, indent=2)

        with open("data/jobs_recent.json", "w") as f:
            json.dump(filter_recent(self.jobs), f, indent=2)

        print("Saved all files")


if __name__ == "__main__":
    s = JobScraper()
    s.run()
    s.save()


