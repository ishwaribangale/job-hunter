"""
PJIS – Fetch-First Job Scraper (Production Stable)
"""

import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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

def filter_by_role(jobs):
    keys = ["product", "growth", "platform", "analyst", "strategy", "gtm"]
    return [j for j in jobs if any(k in (j["title"] or "").lower() for k in keys)]

def filter_recent(jobs, hours=48):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    out = []
    for j in jobs:
        try:
            if datetime.fromisoformat(j["postedDate"]) >= cutoff:
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
        src = job["source"]
        self.stats[src] = self.stats.get(src, 0) + 1
        return True

    def scrape_remotive(self):
        print("\n[Remotive]")
        r = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS)
        print("HTTP:", r.status_code)
        added = 0
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

    def scrape_remoteok(self):
        print("\n[RemoteOK]")
        r = requests.get("https://remoteok.com/api", headers=HEADERS)
        print("HTTP:", r.status_code)
        added = 0
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

    def scrape_yc(self):
        print("\n[Y Combinator]")
        html = requests.get("https://www.ycombinator.com/jobs", headers=HEADERS).text
        soup = BeautifulSoup(html, "html.parser")
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

    def scrape_internshala(self):
        print("\n[Internshala]")
        base = "https://internshala.com"
        urls = [
            f"{base}/jobs/product-manager-jobs",
            f"{base}/jobs/business-analyst-jobs",
            f"{base}/jobs/analytics-jobs",
        ]
        added = 0
        for url in urls:
            r = requests.get(url, headers=HEADERS)
            print("URL:", url, "HTTP:", r.status_code)
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.individual_internship")
            print("Cards:", len(cards))
            for c in cards:
                t = c.select_one("h3.job-internship-name")
                l = c.select_one("a.view_detail_button")
                if not t or not l:
                    continue
                if self.add({
                    "id": f"internshala_{hash(l['href'])}",
                    "title": t.get_text(strip=True),
                    "company": (c.select_one("p.company-name") or {}).get_text(strip=True) if c.select_one("p.company-name") else None,
                    "location": (c.select_one("span.location_link") or {}).get_text(strip=True) if c.select_one("span.location_link") else None,
                    "source": "Internshala",
                    "applyLink": base + l["href"],
                    "postedDate": self.now(),
                    "fetchedAt": self.now(),
                }):
                    added += 1
        print("Added:", added)

    def scrape_companies(self):
        print("\n[Company Career Pages]")
        for c in TOP_COMPANIES:
            added = 0
            print("Company:", c["name"])
            if c["ats"] == "lever":
                soup = BeautifulSoup(
                    requests.get(f"https://jobs.lever.co/{c['slug']}", headers=HEADERS).text,
                    "html.parser"
                )
                posts = soup.select("a.posting-title")
                print("Lever posts:", len(posts))
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
                print("Greenhouse posts:", len(posts))
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
            print("Added:", added)

    def run(self):
        self.scrape_remotive()
        self.scrape_remoteok()
        self.scrape_yc()
        self.scrape_internshala()
        self.scrape_companies()

        print("\nSOURCE SUMMARY")
        for k, v in self.stats.items():
            print(k, ":", v)
        print("TOTAL:", len(self.jobs))

    def save(self):
        with open("data/jobs.json", "w") as f:
            json.dump(self.jobs, f, indent=2)
        with open("data/jobs_product.json", "w") as f:
            json.dump(filter_by_role(self.jobs), f, indent=2)
        with open("data/jobs_recent.json", "w") as f:
            json.dump(filter_recent(self.jobs), f, indent=2)
        print("Saved JSON files")


if __name__ == "__main__":
    s = JobScraper()
    s.run()
    s.save()
