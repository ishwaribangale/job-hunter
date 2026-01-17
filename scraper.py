"""
Personal Job Intelligence System (PJIS)
Playwright-enabled Scraper (Source Expansion Phase)
Author: Ishwari Bangale
"""

import json
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

class JobScraper:
    def __init__(self):
        self.jobs = []

    # =========================================================
    # REMOTIVE (API – KEEP FAST)
    # =========================================================
    def scrape_remotive(self):
        print("\n🌍 Scraping Remotive (API)")

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
                "remote": True,
                "source": "Remotive",
                "applyLink": job.get("url"),
                "postedDate": job.get("publication_date"),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ Remotive jobs added: {count}")

    # =========================================================
    # WE WORK REMOTELY (PLAYWRIGHT)
    # =========================================================
    def scrape_weworkremotely(self, page):
    print("\n🌍 Scraping WeWorkRemotely (Playwright – fixed)")

    page.goto(
        "https://weworkremotely.com/categories/remote-product-jobs",
        timeout=60000,
        wait_until="networkidle"
    )

    page.wait_for_selector("section.jobs", timeout=20000)

    job_links = page.query_selector_all("section.jobs li a")
    print(f"🔎 WeWorkRemotely job links found: {len(job_links)}")

    count = 0
    for job in job_links:
        title_el = job.query_selector("span.title")
        company_el = job.query_selector("span.company")

        if not title_el or not company_el:
            continue

        href = job.get_attribute("href")
        if not href:
            continue

        job_url = "https://weworkremotely.com" + href

        self.jobs.append({
            "id": f"wwr_{hash(job_url)}",
            "title": title_el.inner_text().strip(),
            "company": company_el.inner_text().strip(),
            "location": "Remote",
            "remote": True,
            "source": "WeWorkRemotely",
            "applyLink": job_url,
            "postedDate": self._now(),
            "fetchedAt": self._now()
        })
        count += 1

    print(f"✅ WeWorkRemotely jobs added: {count}")


    # =========================================================
    # WELLFOUND (PLAYWRIGHT – DEEP CRAWL)
    # =========================================================
    def scrape_wellfound(self, page):
        print("\n🌍 Scraping Wellfound (Playwright deep crawl)")

        page.goto("https://wellfound.com/jobs", timeout=60000)
        page.wait_for_timeout(5000)

        job_cards = page.query_selector_all("a[data-test='StartupResult-jobTitle']")
        print(f"🔎 Job cards found: {len(job_cards)}")

        count = 0
        for card in job_cards:
            href = card.get_attribute("href")
            if not href:
                continue

            job_url = "https://wellfound.com" + href

            title = card.inner_text().strip()

            company_el = card.locator(
                "xpath=../../..//a[@data-test='StartupResult-companyName']"
            ).first

            company = company_el.inner_text().strip() if company_el else None

            self.jobs.append({
                "id": f"wellfound_{hash(job_url)}",
                "title": title,
                "company": company,
                "location": None,
                "remote": None,
                "source": "Wellfound",
                "applyLink": job_url,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ Wellfound jobs added: {count}")

    # =========================================================
    # RUNNER (ONE BROWSER FOR ALL)
    # =========================================================
    def run(self):
        print("\n🚀 PJIS SCRAPER STARTED (Playwright Enabled)")

        # API-based (fast)
        self.scrape_remotive()

        # Browser-based (JS-heavy)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=HEADERS["User-Agent"])
            page = context.new_page()

            self.scrape_weworkremotely(page)
            self.scrape_wellfound(page)

            browser.close()

        print("\n==============================")
        print(f"✅ TOTAL JOBS COLLECTED: {len(self.jobs)}")
        print("==============================")

        return self.jobs

    def save(self, filename="data/jobs.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)

        print(f"💾 Jobs saved to {filename}")

    def _now(self):
        return datetime.utcnow().isoformat()


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
