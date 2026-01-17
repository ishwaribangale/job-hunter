"""
PJIS – Playwright Scraper (PRODUCTION FIXED)
"""

import json
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright


class JobScraper:
    def __init__(self):
        self.jobs = []

    def _now(self):
        return datetime.utcnow().isoformat()

    # -------------------------------
    # REMOTIVE (API)
    # -------------------------------
    def scrape_remotive(self):
        print("🌍 Scraping Remotive (API)")
        res = requests.get("https://remotive.com/api/remote-jobs", timeout=30)
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
    # WE WORK REMOTELY (RELAXED PARSER)
    # -------------------------------
    def scrape_weworkremotely(self, page):
        print("🌍 Scraping WeWorkRemotely")

        page.goto(
            "https://weworkremotely.com/categories/remote-product-jobs",
            wait_until="networkidle",
            timeout=60000
        )

        items = page.query_selector_all("section.jobs li")
        print(f"🔎 WWR job items found: {len(items)}")

        count = 0
        for li in items:
            link = li.query_selector("a")
            if not link:
                continue

            href = link.get_attribute("href")
            title = link.inner_text().strip()

            company_el = li.query_selector("span.company")
            company = company_el.inner_text().strip() if company_el else "Unknown"

            if not href or not title:
                continue

            self.jobs.append({
                "id": f"wwr_{hash(href)}",
                "title": title,
                "company": company,
                "location": "Remote",
                "source": "WeWorkRemotely",
                "applyLink": "https://weworkremotely.com" + href,
                "postedDate": self._now(),
                "fetchedAt": self._now()
            })
            count += 1

        print(f"✅ WeWorkRemotely jobs added: {count}")

    # -------------------------------
    # WELLFOUND (NETWORK INTERCEPTION)
    # -------------------------------
    def scrape_wellfound(self, page):
        print("🌍 Scraping Wellfound (XHR mode)")

        jobs = []

        def handle_response(response):
            try:
                if "graphql" in response.url and response.request.method == "POST":
                    data = response.json()
                    text = json.dumps(data)
                    if "job" in text.lower():
                        jobs.append(data)
            except Exception:
                pass

        page.on("response", handle_response)
        page.goto("https://wellfound.com/jobs", timeout=60000)
        page.wait_for_timeout(8000)

        print(f"🔎 Wellfound network payloads captured: {len(jobs)}")

        count = 0
        seen = set()

        for payload in jobs:
            text = json.dumps(payload)
            for part in text.split("https://wellfound.com/jobs/"):
                slug = part.split('"')[0]
                if len(slug) > 5 and slug not in seen:
                    seen.add(slug)
                    url = f"https://wellfound.com/jobs/{slug}"

                    self.jobs.append({
                        "id": f"wellfound_{hash(url)}",
                        "title": slug.replace("-", " ").title(),
                        "company": None,
                        "location": None,
                        "source": "Wellfound",
                        "applyLink": url,
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


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
