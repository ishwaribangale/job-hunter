# scraper.py
# ----------------------------------
# PJIS – Job Intelligence Scraper
# ----------------------------------

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from config import HEADERS, TIMEOUT, TOP_COMPANIES
from roles import infer_role
from scoring import score_job

# ----------------------------------
# MODE SWITCH
# ----------------------------------
SCRAPE_MODE = "VOLUME"
# options: "VOLUME" | "INTELLIGENCE"


class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen = set()
        self.stats = {}

    def now(self):
        return datetime.utcnow().isoformat()

    def add(self, job):
        link = job.get("applyLink")
        if not link or link in self.seen:
            return

        job["role"] = infer_role(job.get("title"))
        job["score"] = score_job(job)
        job["fetchedAt"] = self.now()

        self.seen.add(link)
        self.jobs.append(job)

        src = job["source"]
        self.stats[src] = self.stats.get(src, 0) + 1

    # ----------------------------------
    # REMOTIVE
    # ----------------------------------
    def scrape_remotive(self):
        print("\n[Remotive]")
        r = requests.get(
            "https://remotive.com/api/remote-jobs",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        data = r.json().get("jobs", [])
        print("Cards:", len(data))

        for j in data:
            self.add({
                "id": f"remotive_{j['id']}",
                "title": j["title"],
                "company": j["company_name"],
                "location": j.get("candidate_required_location", "Remote"),
                "source": "Remotive",
                "applyLink": j["url"],
                "postedDate": j["publication_date"]
            })

    # ----------------------------------
    # REMOTEOK
    # ----------------------------------
    def scrape_remoteok(self):
        print("\n[RemoteOK]")
        r = requests.get(
            "https://remoteok.com/api",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        data = r.json()[1:]
        print("Cards:", len(data))

        for j in data:
            self.add({
                "id": f"remoteok_{j.get('id')}",
                "title": j.get("position"),
                "company": j.get("company"),
                "location": "Remote",
                "source": "RemoteOK",
                "applyLink": j.get("url"),
                "postedDate": self.now()
            })

    # ----------------------------------
    # WEWORKREMOTELY (BROAD)
    # ----------------------------------
    def scrape_weworkremotely(self):
        print("\n[WeWorkRemotely]")
        base = "https://weworkremotely.com/categories"
        categories = [
            "remote-programming-jobs",
            "remote-design-jobs",
            "remote-product-jobs",
            "remote-sales-and-marketing-jobs",
            "remote-customer-support-jobs",
        ]

        total_cards = 0

        for cat in categories:
            url = f"{base}/{cat}"
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")

            cards = soup.select("section.jobs article")
            print(f"{cat}: {len(cards)} cards")
            total_cards += len(cards)

            for c in cards:
                title = c.select_one("span.title")
                company = c.select_one("span.company")
                link = c.select_one("a")

                if not title or not company or not link:
                    continue

                self.add({
                    "id": f"wwr_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "Remote",
                    "source": "WeWorkRemotely",
                    "applyLink": "https://weworkremotely.com" + link["href"],
                    "postedDate": self.now()
                })

        print("Total WWR cards:", total_cards)

    # ----------------------------------
    # Y COMBINATOR
    # ----------------------------------
    def scrape_yc(self):
        print("\n[Y Combinator]")
        r = requests.get(
            "https://www.ycombinator.com/jobs",
            headers=HEADERS,
            timeout=TIMEOUT
        )
        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.select("a[href^='/jobs/']")
        print("Cards:", len(cards))

        for a in cards:
            self.add({
                "id": f"yc_{hash(a['href'])}",
                "title": a.get_text(strip=True),
                "company": "YC Startup",
                "location": "Various",
                "source": "YCombinator",
                "applyLink": "https://www.ycombinator.com" + a["href"],
                "postedDate": self.now()
            })

    # ----------------------------------
    # INTERNSHALA (EXPANDED)
    # ----------------------------------
    def scrape_internshala(self):
        print("\n[Internshala]")
        base = "https://internshala.com"
        urls = [
            f"{base}/jobs/product-manager-jobs",
            f"{base}/jobs/business-analyst-jobs",
            f"{base}/jobs/software-developer-jobs",
            f"{base}/jobs/frontend-developer-jobs",
            f"{base}/jobs/backend-developer-jobs",
            f"{base}/jobs/ui-ux-designer-jobs",
            f"{base}/jobs/data-analyst-jobs",
            f"{base}/jobs/product-intern-jobs",
        ]

        total_cards = 0

        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")

            cards = soup.select("div.individual_internship")
            print(f"{url}: {len(cards)} cards")
            total_cards += len(cards)

            for c in cards:
                title = c.select_one("h3.job-internship-name")
                company = c.select_one("p.company-name")
                link = c.select_one("a.view_detail_button, a.job-title-href")

                if not title or not company or not link:
                    continue

                self.add({
                    "id": f"internshala_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "India",
                    "source": "Internshala",
                    "applyLink": base + link["href"],
                    "postedDate": self.now()
                })

        if total_cards == 0:
            print("⚠ Internshala returned 0 cards (likely blocked)")

    # ----------------------------------
    # ATS (LEVER + GREENHOUSE)
    # ----------------------------------
    def scrape_ats(self):
        print("\n[ATS Jobs]")

        for c in TOP_COMPANIES:
            print(f"Company: {c['name']}")

            if c["ats"] == "lever":
                r = requests.get(
                    f"https://jobs.lever.co/{c['slug']}?mode=json",
                    headers=HEADERS,
                    timeout=TIMEOUT
                )

                if "json" not in r.headers.get("Content-Type", ""):
                    print("❌ Lever returned non-JSON for", c["name"])
                    continue

                for j in r.json():
                    self.add({
                        "id": f"lever_{j['id']}",
                        "title": j["text"],
                        "company": c["name"],
                        "location": j["categories"].get("location"),
                        "source": f"{c['name']} (Lever)",
                        "applyLink": j["hostedUrl"],
                        "postedDate": self.now()
                    })

            else:
                r = requests.get(
                    f"https://boards.greenhouse.io/{c['slug']}/jobs.json",
                    headers=HEADERS,
                    timeout=TIMEOUT
                )

                if r.status_code != 200:
                    print("❌ Greenhouse failed for", c["name"], "status:", r.status_code)
                    continue

                for j in r.json().get("jobs", []):
                    self.add({
                        "id": f"gh_{j['id']}",
                        "title": j["title"],
                        "company": c["name"],
                        "location": j["location"]["name"],
                        "source": f"{c['name']} (Greenhouse)",
                        "applyLink": j["absolute_url"],
                        "postedDate": self.now()
                    })

    # ----------------------------------
    # RUN
    # ----------------------------------
    def run(self):
        print(f"\n[MODE] {SCRAPE_MODE}")

        if SCRAPE_MODE == "VOLUME":
            self.scrape_remotive()
            self.scrape_remoteok()
            self.scrape_weworkremotely()
            self.scrape_yc()
            self.scrape_internshala()
            self.scrape_ats()
        else:
            self.scrape_ats()
            self.scrape_yc()

        print("\n[SOURCE SUMMARY]")
        for k, v in self.stats.items():
            print(f"{k}: {v}")

        print("\nTOTAL JOBS:", len(self.jobs))

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(
                sorted(self.jobs, key=lambda x: x["score"], reverse=True),
                f,
                indent=2,
                ensure_ascii=False
            )
        print("Saved → data/jobs.json")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
