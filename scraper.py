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
from config import HEADERS, TIMEOUT, TOP_COMPANIES, CAREER_PAGES

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
    
        categories = [
            None,
            "software-dev",
            "product",
            "design",
            "marketing",
            "sales",
            "data",
            "customer-support",
            "devops",
            "qa",
            "finance",
        ]
    
        for cat in categories:
            url = "https://remotive.com/api/remote-jobs"
            if cat:
                url += f"?category={cat}"
    
            try:
                r = requests.get(url, headers=HEADERS, timeout=10)
                data = r.json().get("jobs", [])
    
                label = "all" if not cat else cat
                print(f"  Category '{label}': {len(data)} jobs")
    
                for j in data:
                    self.add({
                        "id": f"remotive_{j['id']}",
                        "title": j["title"],
                        "company": j["company_name"],
                        "location": j.get("candidate_required_location", "Remote"),
                        "source": "Remotive",
                        "applyLink": j["url"],
                        "postedDate": j["publication_date"],
                    })
    
            except Exception as e:
                print(f"  ❌ Remotive '{cat}' failed:", e)


    # ----------------------------------
# NODESK (PAGINATED)
# ----------------------------------
    # ----------------------------------
# WELLFOUND (PAGE 1 ONLY)
# ----------------------------------
    def scrape_wellfound(self):
        print("\n[Wellfound]")
    
        url = "https://wellfound.com/jobs"
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        }
    
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
    
            cards = soup.select("a[data-testid='job-title-link']")
    
            print(f"  Jobs found: {len(cards)}")
    
            for a in cards:
                href = a.get("href")
                title = a.get_text(strip=True)
    
                if not href or not title:
                    continue
    
                self.add({
                    "id": f"wellfound_{hash(href)}",
                    "title": title,
                    "company": "Startup (Wellfound)",
                    "location": "Remote / Hybrid",
                    "source": "Wellfound",
                    "applyLink": "https://wellfound.com" + href,
                    "postedDate": self.now(),
                })
    
        except Exception as e:
            print("  ❌ Wellfound failed:", e)


    # ----------------------------------
    def scrape_remoteok(self):
        print("\n[RemoteOK]")
    
        base = "https://remoteok.com/api"
        tags = [
            None,
            "engineer",
            "software-dev",
            "frontend",
            "backend",
            "fullstack",
            "product",
            "design",
            "data",
            "marketing",
            "sales",
            "customer-support",
        ]
    
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)",
            "Accept": "application/json",
        }
    
        for tag in tags:
            if tag is None:
                url = base
                label = "main"
            else:
                url = f"{base}?tag={tag}"
                label = tag
    
            try:
                r = requests.get(url, headers=headers, timeout=6)
    
                if r.status_code != 200:
                    print(f"  ⚠ {label}: HTTP {r.status_code}")
                    continue
    
                data = r.json()
    
                # RemoteOK quirk: first item is metadata
                if not isinstance(data, list) or len(data) < 2:
                    print(f"  ⚠ {label}: invalid payload")
                    continue
    
                jobs = data[1:]
                print(f"  {label}: {len(jobs)} jobs")
    
                for j in jobs:
                    link = j.get("url")
                    if not link:
                        continue
    
                    self.add({
                        "id": f"remoteok_{j.get('id')}",
                        "title": j.get("position"),
                        "company": j.get("company"),
                        "location": "Remote",
                        "source": "RemoteOK",
                        "applyLink": link,
                        "postedDate": self.now(),
                    })
    
            except Exception as e:
                print(f"  ❌ {label} failed:", e)
        

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
    
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)",
            "Accept": "text/html",
        }
    
        MAX_PAGES = 10
        MAX_TIMEOUTS = 2
    
        for cat in categories:
            print(f"\nCategory: {cat}")
    
            page = 1
            timeouts = 0
    
            while page <= MAX_PAGES:
                url = f"{base}/{cat}"
                if page > 1:
                    url += f"?page={page}"
    
                try:
                    r = requests.get(url, headers=headers, timeout=6)
    
                    if r.status_code != 200:
                        print(f"  ⚠ Page {page}: HTTP {r.status_code}")
                        break
    
                    # RSS / bot protection
                    if "<rss" in r.text.lower():
                        print("  ⚠ RSS or bot response detected, stopping category")
                        break
    
                    soup = BeautifulSoup(r.text, "html.parser")
                    cards = soup.select("li.feature")
    
                    if not cards:
                        print(f"  Page {page}: 0 cards")
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
                    timeouts = 0  # reset after success
    
                except requests.exceptions.ReadTimeout:
                    timeouts += 1
                    print(f"  ⏱ Page {page}: timeout ({timeouts}/{MAX_TIMEOUTS})")
    
                    if timeouts >= MAX_TIMEOUTS:
                        print("  ⚠ Too many timeouts, stopping category")
                        break
    
                except Exception as e:
                    print(f"  ❌ Page {page}: failed → {e}")
                    break


   
# Y COMBINATOR (PLAYWRIGHT – JS SAFE)
# ----------------------------------
    def scrape_yc(self):
        print("\n[Y Combinator – Playwright]")
    
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("  ⚠ Playwright not installed, skipping YC")
            return
    
        url = "https://www.ycombinator.com/jobs"
    
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                )
    
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )
    
                page = context.new_page()
                page.goto(url, timeout=30_000, wait_until="networkidle")
    
                # YC hydrates links after JS runs
                page.wait_for_selector("a[href^='/jobs/']", timeout=10_000)
    
                links = page.query_selector_all("a[href^='/jobs/']")
                print(f"  Job links found: {len(links)}")
    
                for a in links:
                    href = a.get_attribute("href")
                    title = a.inner_text().strip()
    
                    if not href or not title:
                        continue
    
                    self.add({
                        "id": f"yc_{hash(href)}",
                        "title": title,
                        "company": "YC Startup",
                        "location": "Various",
                        "source": "YCombinator",
                        "applyLink": "https://www.ycombinator.com" + href,
                        "postedDate": self.now(),
                    })
    
                context.close()
                browser.close()
    
        except Exception as e:
            print("  ❌ YC Playwright failed:", e)

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
        print("Companies configured:", len(TOP_COMPANIES))

    headers = {
        **HEADERS,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "application/json,text/html",
    }

    for c in TOP_COMPANIES:
        print("Company:", c["name"], "| ATS:", c["ats"])

        try:
            if c["ats"] == "lever":
                r = requests.get(
                    f"https://jobs.lever.co/{c['slug']}?mode=json",
                    headers=headers,
                    timeout=TIMEOUT,
                )

                if not r.text.strip().startswith("["):
                    print("  ⚠ Lever blocked:", c["name"])
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

            elif c["ats"] == "greenhouse":
                r = requests.get(
                    f"https://boards.greenhouse.io/{c['slug']}",
                    headers=headers,
                    timeout=TIMEOUT,
                )

                soup = BeautifulSoup(r.text, "html.parser")
                jobs = soup.select("a[href*='/jobs/']")

                print("  Greenhouse jobs found:", len(jobs))

                for a in jobs:
                    self.add({
                        "id": f"gh_{hash(a['href'])}",
                        "title": a.get_text(strip=True),
                        "company": c["name"],
                        "location": "Various",
                        "source": f"{c['name']} (Greenhouse)",
                        "applyLink": "https://boards.greenhouse.io" + a["href"],
                        "postedDate": self.now(),
                    })

        except Exception as e:
            print("  ❌ ATS error:", c["name"], e)
            
    def scrape_career_pages(self):
        print("\n[Career Pages]")

        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0",
        }

        for c in CAREER_PAGES:
            try:
                r = requests.get(c["url"], headers=headers, timeout=TIMEOUT)
                soup = BeautifulSoup(r.text, "html.parser")
    
                links = soup.select(
                    "a[href*='job'], a[href*='career'], a[href*='position']"
                )
    
                print(c["name"], "links found:", len(links))
    
                for a in links:
                    text = a.get_text(strip=True)
                    href = a.get("href")
    
                    if not text or not href or len(text) < 5:
                        continue
    
                    self.add({
                        "id": f"career_{c['name']}_{hash(href)}",
                        "title": text,
                        "company": c["name"],
                        "location": "Various",
                        "source": "Career Page",
                        "applyLink": href if href.startswith("http") else c["url"] + href,
                        "postedDate": self.now(),
                    })
    
            except Exception as e:
                print("❌ Career page failed:", c["name"], e)

     def scrape_remoteco(self):
        print("\n[Remote.co]")

        url = "https://remote.co/remote-jobs"
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0",
        }

        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            cards = soup.select("div.card")
            print(f"  Jobs found: {len(cards)}")

            for c in cards:
                title = c.select_one("h3 a")
                company = c.select_one("p.company")

                if not title or not company:
                    continue

                self.add({
                    "id": f"remoteco_{hash(title['href'])}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "Remote",
                    "source": "Remote.co",
                    "applyLink": title["href"],
                    "postedDate": self.now(),
                })

        except Exception as e:
            print("  ❌ Remote.co failed:", e)
    # ----------------------------------
    # RUN
    # ----------------------------------
    def run(self):
        print(f"\n[MODE] {SCRAPE_MODE}")

        if SCRAPE_MODE == "VOLUME":
            self.scrape_remotive()
            self.scrape_remoteok()
            self.scrape_weworkremotely()
            self.scrape_workingnomads()   # ✅ NEW
            self.scrape_nodesk()          # ✅ NEW
            self.scrape_yc()
            self.scrape_internshala()
            self.scrape_ats()
            self.scrape_career_pages()
            self.scrape_remoteco()
            self.scrape_wellfound()

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
