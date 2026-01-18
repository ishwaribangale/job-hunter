"""
PJIS – Job Intelligence Scraper (ATS API Edition)
Reliable • Logged • Production Safe
"""

import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (PJISBot/1.0)"
}

# -------------------------------------------------
# COMPANY CONFIG (ATS APIs)
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

# -------------------------------------------------
# SCRAPER
# -------------------------------------------------
class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen = set()
        self.stats = {}

    def now(self):
        return datetime.utcnow().isoformat()

    def add(self, job):
        url = job.get("applyLink")
        if not url or url in self.seen:
            return
        self.seen.add(url)
        self.jobs.append(job)

        src = job["source"]
        self.stats[src] = self.stats.get(src, 0) + 1

    # -------------------------------------------------
    # REMOTIVE (API)
    # -------------------------------------------------
    def scrape_remotive(self):
        print("\n[Remotive]")
        res = requests.get("https://remotive.com/api/remote-jobs", headers=HEADERS)
        data = res.json().get("jobs", [])
        print(f"Cards found: {len(data)}")

        for j in data:
            self.add({
                "id": f"remotive_{j['id']}",
                "title": j.get("title"),
                "company": j.get("company_name"),
                "location": j.get("candidate_required_location", "Remote"),
                "source": "Remotive",
                "applyLink": j.get("url"),
                "postedDate": j.get("publication_date"),
                "fetchedAt": self.now(),
            })

    # -------------------------------------------------
    # REMOTEOK (API)
    # -------------------------------------------------
    def scrape_remoteok(self):
        print("\n[RemoteOK]")
        data = requests.get("https://remoteok.com/api", headers=HEADERS).json()[1:]
        print(f"Cards found: {len(data)}")

        for j in data:
            self.add({
                "id": f"remoteok_{j.get('id')}",
                "title": j.get("position"),
                "company": j.get("company"),
                "location": "Remote",
                "source": "RemoteOK",
                "applyLink": j.get("url"),
                "postedDate": self.now(),
                "fetchedAt": self.now(),
            })

    # -------------------------------------------------
    # YC JOBS
    # -------------------------------------------------
    def scrape_yc(self):
        print("\n[Y Combinator]")
        soup = BeautifulSoup(
            requests.get("https://www.ycombinator.com/jobs", headers=HEADERS).text,
            "html.parser"
        )
        cards = soup.select("a[href^='/jobs/']")
        print(f"Cards found: {len(cards)}")

        for a in cards:
            self.add({
                "id": f"yc_{hash(a['href'])}",
                "title": a.get_text(strip=True),
                "company": "YC Startup",
                "location": None,
                "source": "YCombinator",
                "applyLink": "https://www.ycombinator.com" + a["href"],
                "postedDate": self.now(),
                "fetchedAt": self.now(),
            })

    # -------------------------------------------------
    # INTERNShala (HTML – WORKING)
    # -------------------------------------------------
    def scrape_internshala(self):
        print("\n[Internshala]")
        base = "https://internshala.com"
        urls = [
            f"{base}/jobs/product-manager-jobs",
            f"{base}/jobs/business-analyst-jobs",
        ]

        total_cards = 0
        added = 0

        for url in urls:
            soup = BeautifulSoup(
                requests.get(url, headers=HEADERS).text,
                "html.parser"
            )
            cards = soup.select("div.individual_internship")
            total_cards += len(cards)

            for c in cards:
                title = c.select_one("h3.job-internship-name")
                link = c.select_one("a.view_detail_button")

                if not title or not link:
                    continue

                before = len(self.jobs)
                self.add({
                    "id": f"internshala_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": c.select_one("p.company-name").get_text(strip=True),
                    "location": c.select_one("span.location_link").get_text(strip=True),
                    "source": "Internshala",
                    "applyLink": base + link["href"],
                    "postedDate": self.now(),
                    "fetchedAt": self.now(),
                })
                if len(self.jobs) > before:
                    added += 1

        print(f"Cards found: {total_cards}")
        print(f"Added: {added}")

    # -------------------------------------------------
    # ATS APIs (THE FIX)
    # -------------------------------------------------
    def scrape_ats(self):
        print("\n[Company Career Pages – ATS APIs]")

        for c in TOP_COMPANIES:
            print(f"\nCompany: {c['name']}")

            if c["ats"] == "lever":
                url = f"https://jobs.lever.co/{c['slug']}?mode=json"
                data = requests.get(url, headers=HEADERS).json()
                print(f"Lever jobs: {len(data)}")

                for j in data:
                    self.add({
                        "id": f"lever_{j['id']}",
                        "title": j["text"],
                        "company": c["name"],
                        "location": j.get("categories", {}).get("location"),
                        "source": f"{c['name']} (Lever)",
                        "applyLink": j["hostedUrl"],
                        "postedDate": self.now(),
                        "fetchedAt": self.now(),
                    })

            if c["ats"] == "greenhouse":
                url = f"https://boards.greenhouse.io/{c['slug']}/jobs.json"
                data = requests.get(url, headers=HEADERS).json().get("jobs", [])
                print(f"Greenhouse jobs: {len(data)}")

                for j in data:
                    self.add({
                        "id": f"gh_{j['id']}",
                        "title": j["title"],
                        "company": c["name"],
                        "location": j.get("location", {}).get("name"),
                        "source": f"{c['name']} (Greenhouse)",
                        "applyLink": j["absolute_url"],
                        "postedDate": self.now(),
                        "fetchedAt": self.now(),
                    })

    # -------------------------------------------------
    # RUN + SAVE
    # -------------------------------------------------
    def run(self):
        self.scrape_remotive()
        self.scrape_remoteok()
        self.scrape_yc()
        self.scrape_internshala()
        self.scrape_ats()

        print("\n[SOURCE SUMMARY]")
        for s, c in self.stats.items():
            print(f"{s}: {c}")

        print("\nTOTAL JOBS:", len(self.jobs))

    def save(self):
        with open("data/jobs.json", "w") as f:
            json.dump(self.jobs, f, indent=2)
        print("Saved → data/jobs.json")


if __name__ == "__main__":
    s = JobScraper()
    s.run()
    s.save()



