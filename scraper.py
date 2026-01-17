"""
PJIS – Playwright Scraper (STABLE VERSION)
"""

import json
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright


class JobScraper:
    def __init__(self):
        self.jobs = []

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
    # WE WORK REMOTELY (PLAYWRIGHT)
    # -------------------------------
    def scrape_weworkremotely(self, page):
        print("🌍 Scraping WeWorkRemotely")

        page.goto(
            "https://weworkremotely.com/categories/remote-product-jobs",
            wait_until="networkidle",
            timeout=60000
        )

        page.wait_for_selector("section.jobs", timeout=20000)

        links = page.query_selector_all("section.jobs li a")
        print(f"🔎 WWR links found: {len(links)}")

        count = 0
        for link in links:
            title_el = link.query_selector("span.title")
            company_el = link.query_selector("span.company")
            href = link.get_attribute("href")

            if not title_el or not company_el or not href:
                continue

            self.jobs.append({
                "id": f"wwr_{hash(href)}",
                "title": title_el.inner_text().strip(),
                "company": company_el.inner_text().strip(),
                "location": "Remote",
                "source": "WeWorkRemotely",
                "applyLink": "https://weworkremotely.com" + href,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ WeWorkRemotely jobs added: {count}")

    # -------------------------------
    # WELLFOUND (PLAYWRIGHT + SCROLL)
    # -------------------------------
    def scrape_wellfound(self, page):
        print("🌍 Scraping Wellfound")

        page.goto("https://wellfound.com/jobs", timeout=60000)
        page.wait_for_timeout(4000)

        for _ in range(6):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)

        links = page.query_selector_all("a[href^='/jobs/']")
        print(f"🔎 Wellfound links found: {len(links)}")

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
    # RUNNER (ONLY PLACE PAGE EXISTS)
    # -------------------------------
    def run(self):
        print("🚀 PJIS SCRAPER STARTED")

        self.scrape_remotive()

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

    def _now(self):
        return datetime.utcnow().isoformat()


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
