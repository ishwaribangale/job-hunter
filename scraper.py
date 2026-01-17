"""
PJIS – Playwright Scraper (STABLE + FIXED)
"""

import json
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright


class JobScraper:
    def __init__(self):
        self.jobs = []

    # -------------------------------
    # UTIL
    # -------------------------------
    def _now(self):
        return datetime.utcnow().isoformat()

    # -------------------------------
    # REMOTIVE (API)
    # -------------------------------
    def scrape_remotive(self):
        print("🌍 Scraping Remotive (API)")
        url = "https://remotive.com/api/remote-jobs"

        res = requests.get(url, timeout=30)
        data = res.json()

        count = 0
        for job in data.get("jobs", []):
            self.jobs.append({
                "id": f"remotive_{job['id']}",
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("candidate_required_location") or "Remote",
                "source": "Remotive",
                "applyLink": job.get("url"),
                "postedDate": job.get("publication_date"),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ Remotive jobs added: {count}")

    # -------------------------------
    # WE WORK REMOTELY (PLAYWRIGHT – FIXED)
    # -------------------------------
    def scrape_weworkremotely(self, page):
        print("🌍 Scraping WeWorkRemotely")

        page.goto(
            "https://weworkremotely.com/categories/remote-product-jobs",
            wait_until="networkidle",
            timeout=60000
        )

        page.wait_for_selector("section.jobs", timeout=20000)

        items = page.query_selector_all("section.jobs li")
        print(f"🔎 WWR job items found: {len(items)}")

        count = 0
        for li in items:
            link = li.query_selector("a")
            title_el = li.query_selector("span.title")
            company_el = li.query_selector("span.company")

            if not link or not title_el:
                continue

            href = link.get_attribute("href")
            if not href:
                continue

            self.jobs.append({
                "id": f"wwr_{hash(href)}",
                "title": title_el.inner_text().strip(),
                "company": company_el.inner_text().strip() if company_el else "Unknown",
                "location": "Remote",
                "source": "WeWorkRemotely",
                "applyLink": "https://weworkremotely.com" + href,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ WeWorkRemotely jobs added: {count}")

    # -------------------------------
    # WELLFOUND (PLAYWRIGHT – FIXED)
    # -------------------------------
    def scrape_wellfound(self, page):
        print("🌍 Scraping Wellfound")

        page.goto("https://wellfound.com/jobs", timeout=60000)
        page.wait_for_timeout(5000)

        # Target the actual virtualized results container
        container = page.query_selector("div[data-test='JobSearchResults']")
        if not container:
            print("❌ Wellfound job container not found")
            return

        # Scroll INSIDE the container to trigger React rendering
        for _ in range(8):
            page.evaluate("(el) => el.scrollBy(0, 3000)", container)
            page.wait_for_timeout(2000)

        links = page.query_selector_all("a[href^='/jobs/']")
        print(f"🔎 Wellfound job links found: {len(links)}")

        count = 0
        for link in links:
            href = link.get_attribute("href")
            title = link.inner_text().strip()

            if not href or not title:
                continue

            self.jobs.append({
                "id": f"wellfound_{hash(href)}",
                "title": title,
                "company": None,
                "location": None,
                "source": "Wellfound",
                "applyLink": "https://wellfound.com" + href,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ Wellfound jobs added: {count}")

    # -------------------------------
    # RUNNER
    # -------------------------------
    def run(self):
        print("🚀 PJIS SCRAPER STARTED")

        # API-based sources
        self.scrape_remotive()

        # Playwright-based sources
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            self.scrape_weworkremotely(page)
            self.scrape_wellfound(page)

            browser.close()

        print(f"✅ TOTAL JOBS: {len(self.jobs)}")

    def save(self):
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)

        print("💾 Jobs saved to data/jobs.json")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()

