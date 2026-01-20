# scraper.py
# ----------------------------------
# PJIS – Job Intelligence Scraper
# Phase 1: Completeness (STABLE)
# ----------------------------------

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT, TOP_COMPANIES
from roles import infer_role
from scoring import score_job

SCRAPE_MODE = "VOLUME"  # VOLUME | INTELLIGENCE


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
        print(f"API jobs returned: {len(data)}")

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
    # REMOTEOK (TAG EXPANSION)
    # ----------------------------------
    def scrape_remoteok(self):
        print("\n[RemoteOK]")

        base = "https://remoteok.com/api"
        tags = [
            None,
            "dev",
            "software-dev",
            "product",
            "design",
            "marketing",
            "sales",
            "data",
            "customer-support",
        ]

        for tag in tags:
            url = base if tag is None else f"{base}?tag={tag}"
            label = "main" if tag is None else tag

            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            data = r.json()[1:]

            print(f"  Tag '{label}': {len(data)} cards")

            for j in data:
                self.add({
                    "id": f"remoteok_{j.get('id')}",
                    "title": j.get("position"),
                    "company": j.get("company"),
                    "location": "Remote",
                    "source": "RemoteOK",
                    "applyLink": j.get("url"),
                    "postedDate": self.now(),
                })

    # ----------------------------------
    # WEWORKREMOTELY (RSS-SAFE)
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

        headers = {**HEADERS, "Accept": "text/html"}

        for cat in categories:
            print(f"\nCategory: {cat}")
            page = 1

            while page <= 20:
                url = f"{base}/{cat}"
                if page > 1:
                    url += f"?page={page}"

                r = requests.get(url, headers=headers, timeout=TIMEOUT)

                # RSS protection
                if "<rss" in r.text.lower():
                    print("  ⚠ RSS feed detected, stopping category")
                    break

                soup = BeautifulSoup(r.text, "html.parser")
                cards = soup.select("li.feature")

                if not cards:
                    break

                print(f"  Page {page}: {len(cards)} cards")

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
                        "postedDate": self.now(),
                    })

                page += 1

    # ----------------------------------
    # Y COMBINATOR
    # ----------------------------------
    def scrape_yc(self):
        print("\n[Y Combinator]")

        base = "https://www.ycombinator.com"
        r = requests.get(f"{base}/jobs", headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.select("a[href^='/jobs/']")
        print(f"Job links found: {len(links)}")

        for a in links:
            href = a.get("href")
            if not href:
                continue

            self.add({
                "id": f"yc_{hash(href)}",
                "title": a.get_text(strip=True),
                "company": "YC Startup",
                "location": "Various",
                "source": "YCombinator",
                "applyLink": base + href,
                "postedDate": self.now(),
            })
    # ----------------------------------
# WORKING NOMADS (PAGINATED)
# ----------------------------------
    def scrape_workingnomads(self):
        print("\n[Working Nomads]")
    
        base = "https://www.workingnomads.com/jobs"
        page = 1
        total = 0
    
        while page <= 20:  # safety cap
            url = base if page == 1 else f"{base}?page={page}"
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")
    
            cards = soup.select("div.job-listing")
    
            if not cards:
                break
    
            print(f"  Page {page}: {len(cards)} cards")
    
            for c in cards:
                title = c.select_one("h3 a")
                company = c.select_one("span.company")
                link = c.select_one("h3 a")
    
                if not title or not company or not link:
                    continue
    
                self.add({
                    "id": f"wn_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "Remote",
                    "source": "Working Nomads",
                    "applyLink": "https://www.workingnomads.com" + link["href"],
                    "postedDate": self.now(),
                })
    
                total += 1
    
            page += 1
    
        print(f"Total Working Nomads jobs fetched: {total}")
    
        # ----------------------------------
    # NODESK (PAGINATED)
    # ----------------------------------
    def scrape_nodesk(self):
        print("\n[NoDesk]")
    
        base = "https://nodesk.co/remote-jobs"
        page = 1
        total = 0
    
        while page <= 20:
            url = base if page == 1 else f"{base}/page/{page}/"
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")
    
            cards = soup.select("article.job")
    
            if not cards:
                break
    
            print(f"  Page {page}: {len(cards)} cards")
    
            for c in cards:
                title = c.select_one("h2 a")
                company = c.select_one("span.company")
                link = c.select_one("h2 a")
    
                if not title or not company or not link:
                    continue
    
                self.add({
                    "id": f"nodesk_{hash(link['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "Remote",
                    "source": "NoDesk",
                    "applyLink": link["href"],
                    "postedDate": self.now(),
                })
    
                total += 1
    
            page += 1
    
        print(f"Total NoDesk jobs fetched: {total}")
    
        
        # ----------------------------------
        # INTERNSHALA
        # ----------------------------------
    def scrape_internshala(self):
        print("\n[Internshala]")

        base = "https://internshala.com"
        paths = [
            "jobs/product-manager-jobs",
            "jobs/business-analyst-jobs",
            "jobs/software-developer-jobs",
            "jobs/frontend-developer-jobs",
            "jobs/backend-developer-jobs",
            "jobs/ui-ux-designer-jobs",
            "jobs/data-analyst-jobs",
            "jobs/product-intern-jobs",
        ]

        for path in paths:
            url = f"{base}/{path}"
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")

            cards = soup.select("div.individual_internship")
            print(f"{path}: {len(cards)} cards")

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
                    "postedDate": self.now(),
                })

    # ----------------------------------
    # ATS (FAIL-SAFE)
    # ----------------------------------
    def scrape_ats(self):
        print("\n[ATS Jobs]")

        for c in TOP_COMPANIES:
            if c["ats"] == "lever":
                r = requests.get(
                    f"https://jobs.lever.co/{c['slug']}?mode=json",
                    headers=HEADERS,
                    timeout=TIMEOUT,
                )

                if "json" not in r.headers.get("Content-Type", ""):
                    continue

                for j in r.json():
                    self.add({
                        "id": f"lever_{j['id']}",
                        "title": j["text"],
                        "company": c["name"],
                        "location": j["categories"].get("location"),
                        "source": f"{c['name']} (Lever)",
                        "applyLink": j["hostedUrl"],
                        "postedDate": self.now(),
                    })

            else:
                r = requests.get(
                    f"https://boards.greenhouse.io/{c['slug']}/jobs.json",
                    headers=HEADERS,
                    timeout=TIMEOUT,
                )

                if r.status_code != 200:
                    continue

                if "json" not in r.headers.get("Content-Type", ""):
                    print(f"❌ Greenhouse non-JSON: {c['name']}")
                    continue

                for j in r.json().get("jobs", []):
                    self.add({
                        "id": f"gh_{j['id']}",
                        "title": j["title"],
                        "company": c["name"],
                        "location": j["location"]["name"],
                        "source": f"{c['name']} (Greenhouse)",
                        "applyLink": j["absolute_url"],
                        "postedDate": self.now(),
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
                ensure_ascii=False,
            )

        print("Saved → data/jobs.json")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
