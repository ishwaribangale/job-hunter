"""
Personal Job Intelligence System – Clean Scraper
Author: Ishwari Bangale
Purpose: Discover valid, live PM jobs only
Runs via GitHub Actions
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}


class JobScraper:
    def __init__(self):
        self.jobs = []

        # ✅ STRICT PM KEYWORDS ONLY
        self.product_keywords = [
            "product manager",
            "associate product manager",
            "apm",
            "product analyst",
            "product owner",
            "technical product manager",
            "growth product"
        ]

        # 🌍 Companies (India + Remote-first)
        self.target_companies = [
            {"name": "Razorpay", "url": "https://razorpay.com/jobs/"},
            {"name": "CRED", "url": "https://careers.cred.club/"},
            {"name": "PhonePe", "url": "https://www.phonepe.com/careers/"},
            {"name": "Swiggy", "url": "https://careers.swiggy.com/"},
            {"name": "Flipkart", "url": "https://www.flipkartcareers.com/"},
            {"name": "Postman", "url": "https://www.postman.com/company/careers/"},
            {"name": "BrowserStack", "url": "https://www.browserstack.com/careers"},
            {"name": "Vercel", "url": "https://vercel.com/careers"},
            {"name": "Notion", "url": "https://www.notion.so/careers"},
            {"name": "Canva", "url": "https://www.canva.com/careers/"},
            {"name": "GitLab", "url": "https://about.gitlab.com/jobs/"},
            {"name": "Zapier", "url": "https://zapier.com/jobs"},
            {"name": "Doist", "url": "https://doist.com/careers"},
            {"name": "Hotjar", "url": "https://www.hotjar.com/careers/"}
        ]

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def normalize(self, text):
        return re.sub(r"\s+", " ", text.lower().strip())

    def is_pm_role(self, text):
        text = self.normalize(text)
        return any(k in text for k in self.product_keywords)

    def is_real_job_url(self, url):
        url = url.lower()
        allowed = [
                # core job paths
                "job", "jobs", "career", "careers", "position", "positions",
                "role", "roles", "opening", "openings", "opportunity", "opportunities",
            
                # ATS / hiring systems
                "lever", "greenhouse", "ashby", "workday", "smartrecruiters",
                "icims", "successfactors", "bamboohr",
            
                # startup / custom hiring pages
                "hiring", "join-us", "joinus", "join", "work-with-us",
                "vacancy", "vacancies", "apply", "apply-now", "application",
            
                # role-specific pages
                "product-manager", "product", "pm", "apm"
            ]

        blocked = ["blog", "about", "privacy", "terms", "medium"]

        if any(b in url for b in blocked):
            return False
        return any(a in url for a in allowed)

    def is_valid_apply_link(self, url):
        try:
            r = requests.get(
                url,
                headers=HEADERS,
                timeout=10,
                allow_redirects=True
            )
            if r.status_code in [404, 410]:
                return False


            text = r.text.lower()
            invalid_markers = [
                "job not found",
                "position closed",
                "no longer accepting",
                "404",
                "page not found"
            ]

            return not any(m in text for m in invalid_markers)
        except:
            return False

    # --------------------------------------------------
    # Core Scraper
    # --------------------------------------------------

    def scrape_career_pages(self):
        print("🔍 Scraping career pages...")

        for company in self.target_companies:
            try:
                res = requests.get(company["url"], headers=HEADERS, timeout=12)
                if res.status_code != 200:
                    continue

                soup = BeautifulSoup(res.text, "html.parser")
                links = soup.find_all("a", href=True)

                for link in links:
                    title = link.get_text(strip=True)
                    href = link["href"]

                    if not title or not self.is_pm_role(title):
                        continue

                    job_url = (
                        href if href.startswith("http")
                        else urljoin(company["url"], href)
                    )

                    if not self.is_real_job_url(job_url):
                        continue

                    if not self.is_valid_apply_link(job_url):
                        continue

                    job = {
                        "id": f"{company['name']}_{hash(job_url)}",
                        "title": title,
                        "company": company["name"],
                        "location": "Remote / As per JD",
                        "source": "Company Career Page",
                        "applyLink": job_url,
                        "description": title,
                        "postedDate": datetime.utcnow().isoformat(),
                        "matchScore": 0,
                        "fetchedAt": datetime.utcnow().isoformat(),
                        "isManual": False
                    }

                    self.jobs.append(job)

                time.sleep(1)

            except Exception as e:
                print(f"❌ Error scraping {company['name']}: {e}")

        print(f"✅ Jobs collected: {len(self.jobs)}")

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    def dedupe(self):
        seen = set()
        unique = []

        for job in self.jobs:
            key = f"{job['title'].lower()}_{job['company'].lower()}"
            if key not in seen:
                seen.add(key)
                unique.append(job)

        self.jobs = unique

    def remove_expired(self, days=7):
        fresh = []
        for job in self.jobs:
            posted = datetime.fromisoformat(job["postedDate"])
            if (datetime.utcnow() - posted).days <= days:
                fresh.append(job)
        self.jobs = fresh

    # --------------------------------------------------
    # Match Scoring
    # --------------------------------------------------

    def calculate_match_score(self, job, profile):
        score = 50

        if any(r.lower() in job["title"].lower() for r in profile["targetRoles"]):
            score += 20

        if any(loc.lower() in job["location"].lower() for loc in profile["location"]):
            score += 10

        skill_hits = sum(
            1 for s in profile["skills"]
            if s.lower() in job["description"].lower()
        )
        score += min(skill_hits * 3, 15)

        return min(score, 95)

    # --------------------------------------------------
    # Run
    # --------------------------------------------------

    def run(self, profile):
        print("🚀 Starting job scrape...")
        self.scrape_career_pages()
        print(f"🧪 Jobs before validation: {len(self.jobs)}")
        self.dedupe()
        print(f"🧪 Jobs after dedupe: {len(self.jobs)}")

        for job in self.jobs:
            job["matchScore"] = self.calculate_match_score(job, profile)

        print(f"🎯 Final jobs: {len(self.jobs)}")
        return self.jobs

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(self, path="data/jobs.json"):
        with open(path, "w") as f:
            json.dump(self.jobs, f, indent=2)
        print(f"💾 Saved → {path}")


# --------------------------------------------------
# Entry
# --------------------------------------------------

if __name__ == "__main__":
    profile = {
        "targetRoles": [
            "Product Manager",
            "Associate Product Manager",
            "Product Analyst"
        ],
        "skills": [
            "SQL",
            "Python",
            "A/B Testing",
            "Product Strategy",
            "Analytics"
        ],
        "location": ["Remote", "India"]
    }

    scraper = JobScraper()
    scraper.run(profile)
    scraper.save()
