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
    # WORKING NOMADS (PAGINATED)
    # ----------------------------------
        # ----------------------------------
    # WORKING NOMADS (ROBUST, CI-SAFE)
    # ----------------------------------
    def scrape_workingnomads(self):
        print("\n[Working Nomads]")
    
        base = "https://www.workingnomads.com/jobs"
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)",
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.9",
        }
    
        MAX_PAGES = 5
        MAX_FAILURES = 2
    
        page = 1
        failures = 0
        total = 0
    
        while page <= MAX_PAGES:
            url = base if page == 1 else f"{base}?page={page}"
    
            try:
                r = requests.get(url, headers=headers, timeout=6)
    
                if r.status_code != 200:
                    print(f"  ⚠ Page {page}: HTTP {r.status_code}")
                    break
    
                soup = BeautifulSoup(r.text, "html.parser")
    
                # Try multiple known patterns
                cards = (
                    soup.select("li.job") or
                    soup.select("div.job-listing") or
                    soup.select("article.job")
                )
    
                if not cards:
                    failures += 1
                    print(f"  ⚠ Page {page}: no jobs found ({failures}/{MAX_FAILURES})")
    
                    # Likely bot-block or JS-required
                    if failures >= MAX_FAILURES:
                        print("  ⚠ Likely blocked or JS-only, stopping Working Nomads")
                        break
    
                    page += 1
                    continue
    
                print(f"  Page {page}: {len(cards)} cards")
                failures = 0
    
                for c in cards:
                    title = c.select_one("a")
                    company = c.select_one(".company, span.company")
    
                    if not title or not company:
                        continue
    
                    href = title.get("href")
                    if not href:
                        continue
    
                    self.add({
                        "id": f"wn_{hash(href)}",
                        "title": title.get_text(strip=True),
                        "company": company.get_text(strip=True),
                        "location": "Remote",
                        "source": "Working Nomads",
                        "applyLink": (
                            href if href.startswith("http")
                            else "https://www.workingnomads.com" + href
                        ),
                        "postedDate": self.now(),
                    })
    
                    total += 1
    
                page += 1
    
            except requests.exceptions.ReadTimeout:
                failures += 1
                print(f"  ⏱ Page {page}: timeout ({failures}/{MAX_FAILURES})")
    
                if failures >= MAX_FAILURES:
                    print("  ⚠ Too many timeouts, stopping Working Nomads")
                    break
    
            except Exception as e:
                print(f"  ❌ Page {page}: failed → {e}")
                break
    
        print(f"Total Working Nomads jobs fetched: {total}")

    # ----------------------------------
    # REMOTEOK (TAG EXPANSION)
    # ----------------------------------
    def scrape_remoteok(self):
        print("\n[RemoteOK]")
    
        base = "https://remoteok.com/api"
        tags = [
            None,
            "dev",
            "product",
            "design",
            "marketing",
            "data",
        ]
    
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)",
            "Accept": "application/json",
        }
    
        for tag in tags:
            url = base if tag is None else f"{base}?tag={tag}"
            label = "main" if tag is None else tag
    
            try:
                r = requests.get(url, headers=headers, timeout=6)
    
                if r.status_code != 200:
                    print(f"  ⚠ Tag '{label}': HTTP {r.status_code}")
                    continue
    
                data = r.json()
    
                # RemoteOK API quirk: first item is metadata
                if not isinstance(data, list) or len(data) < 2:
                    print(f"  ⚠ Tag '{label}': invalid payload")
                    continue
    
                jobs = data[1:]
                print(f"  Tag '{label}': {len(jobs)} cards")
    
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
    
            except requests.exceptions.ReadTimeout:
                print(f"  ⏱ Tag '{label}': timeout, skipped")
                continue
    
            except Exception as e:
                print(f"  ❌ Tag '{label}': failed → {e}")
                continue

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


    # ----------------------------------
    # Y COMBINATOR
    # ----------------------------------
    # ----------------------------------
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
        # ----------------------------------
    # NODESK (ROBUST, CI-SAFE)
    # ----------------------------------
    def scrape_nodesk(self):
        print("\n[NoDesk]")

        base = "https://nodesk.co/remote-jobs"
        page = 1
        total = 0

        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        while page <= 20:
            url = base if page == 1 else f"{base}/page/{page}/"
            r = requests.get(url, headers=headers, timeout=TIMEOUT)

            soup = BeautifulSoup(r.text, "html.parser")

            # CI-safe selector fallback
            cards = soup.select("article.job") or soup.select("div.job-list article")

            if not cards:
                print(f"  Page {page}: 0 cards (blocked or markup changed)")
                break

            print(f"  Page {page}: {len(cards)} cards")

            for c in cards:
                title = c.select_one("h2 a, h3 a")
                company = c.select_one(".company, span.company")

                if not title or not company:
                    continue

                href = title.get("href")
                if not href:
                    continue

                self.add({
                    "id": f"nodesk_{hash(href)}",
                    "title": title.get_text(strip=True),
                    "company": company.get_text(strip=True),
                    "location": "Remote",
                    "source": "NoDesk",
                    "applyLink": href,
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
