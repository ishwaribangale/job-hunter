"""
Personal Job Intelligence System – Phase 1 Scraper
Author: Ishwari Bangale
Purpose: Discover early, relevant PM jobs from public sources
Runs via GitHub Actions every 2 hours
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
from urllib.parse import quote_plus


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}


class JobScraper:
    def __init__(self):
        self.jobs = []

        # 🔑 PM Keywords
        self.product_keywords = [
            "product manager",
            "associate product manager",
            "apm",
            "product analyst",
            "product owner",
            "product operations",
            "technical product manager",
            "pm"
        ]

        # 🌍 Target Companies (India + Remote-First)
        self.target_companies = [

            # 🇮🇳 Indian Product Startups
            {"name": "Razorpay", "url": "https://razorpay.com/jobs/"},
            {"name": "CRED", "url": "https://careers.cred.club/"},
            {"name": "Meesho", "url": "https://www.meesho.io/careers"},
            {"name": "PhonePe", "url": "https://www.phonepe.com/careers/"},
            {"name": "Swiggy", "url": "https://careers.swiggy.com/"},
            {"name": "Zomato", "url": "https://www.zomato.com/careers"},
            {"name": "Flipkart", "url": "https://www.flipkartcareers.com/"},
            {"name": "Paytm", "url": "https://jobs.lever.co/paytm"},
            {"name": "Ola", "url": "https://www.olacabs.com/careers"},
            {"name": "Zepto", "url": "https://www.zepto.co.in/careers"},
            {"name": "Groww", "url": "https://groww.in/careers"},
            {"name": "Postman", "url": "https://www.postman.com/company/careers/"},
            {"name": "BrowserStack", "url": "https://www.browserstack.com/careers"},

            # 🌐 Remote-First / Global
              {"name": "GitHub", "url": "https://www.github.careers/careers-home"},
                {"name": "HashiCorp", "url": "https://www.hashicorp.com/careers"},
                {"name": "Elastic", "url": "https://jobs.elastic.co/"},
                {"name": "Docker", "url": "https://www.docker.com/career-openings/"},
                {"name": "Netlify", "url": "https://www.netlify.com/careers/"},
                {"name": "Vercel", "url": "https://vercel.com/careers"},
                {"name": "Cloudflare", "url": "https://www.cloudflare.com/careers/"},
                {"name": "Miro", "url": "https://miro.com/careers/"},
                {"name": "Linear", "url": "https://linear.app/careers"},
                {"name": "Intercom", "url": "https://www.intercom.com/careers"},
                {"name": "Calendly", "url": "https://calendly.com/careers"},
                {"name": "Plaid", "url": "https://plaid.com/careers/"},
                {"name": "Brex", "url": "https://www.brex.com/careers"},
                {"name": "Coinbase", "url": "https://www.coinbase.com/careers"},
                {"name": "Revolut", "url": "https://www.revolut.com/careers/"},
                {"name": "Wise", "url": "https://www.wise.jobs/"},
                {"name": "Notion Labs", "url": "https://www.notion.so/careers"},
                {"name": "Webflow", "url": "https://webflow.com/careers"},
                {"name": "Canva", "url": "https://www.canva.com/careers/"},
                {"name": "Spotify", "url": "https://www.spotifyjobs.com/"},
                {"name": "Coursera", "url": "https://www.coursera.org/about/careers"},
                {"name": "Udemy", "url": "https://about.udemy.com/careers/"},
                {"name": "Khan Academy", "url": "https://www.khanacademy.org/careers"},
                {"name": "Duolingo", "url": "https://careers.duolingo.com/"},
                {"name": "Zapier", "url": "https://zapier.com/jobs"},
                {"name": "Hotjar", "url": "https://www.hotjar.com/careers/"},
                {"name": "Doist", "url": "https://doist.com/careers"},
                {"name": "Trello", "url": "https://trello.com/careers"},
                {"name": "Asana", "url": "https://asana.com/jobs"},
                {"name": "Monday.com", "url": "https://monday.com/careers"}
        ]

    # --------------------------------------------------
    # Utility
    # --------------------------------------------------

    def normalize(self, text):
        return re.sub(r"\s+", " ", text.lower().strip())

    def is_pm_role(self, text):
        text = self.normalize(text)
        return any(k in text for k in self.product_keywords)

    # --------------------------------------------------
    # Career Page Scraper (Core Value)
    # --------------------------------------------------

    def scrape_career_pages(self):
        print("🔍 Scraping company career pages...")

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

                    job_url = href if href.startswith("http") else company["url"].rstrip("/") + "/" + href.lstrip("/")

                    job = {
                        "id": f"{company['name']}_{hash(job_url)}",
                        "title": title,
                        "company": company["name"],
                        "location": "Remote / As per JD",
                        "source": "Company Career Page",
                        "applyLink": job_url,
                        "description": title,
                        "postedDate": datetime.utcnow().isoformat(),
                        "engagement": {
                            "likes": 0,
                            "comments": 0,
                            "isUnseen": True
                        },
                        "matchScore": 0,
                        "fetchedAt": datetime.utcnow().isoformat(),
                        "isManual": False
                    }

                    self.jobs.append(job)

                time.sleep(1)

            except Exception as e:
                print(f"❌ {company['name']} error: {e}")

        print(f"✅ Career pages jobs: {len(self.jobs)}")

    # --------------------------------------------------
    # Google Jobs (Discovery Layer)
    # --------------------------------------------------

    def scrape_google_jobs(self):
        print("🔍 Scraping Google Jobs...")

        queries = [
            "associate product manager remote",
            "product analyst india startup",
            "product manager early stage hiring"
        ]

        for q in queries:
            try:
                url = f"https://www.google.com/search?q={quote_plus(q)}&ibp=htl;jobs"
                res = requests.get(url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")

                cards = soup.select(".PwjeAc")[:5]

                for card in cards:
                    title = card.select_one(".BjJfJf")
                    company = card.select_one(".vNEEBe")

                    if not title:
                        continue

                    self.jobs.append({
                        "id": f"google_{hash(title.text)}",
                        "title": title.text,
                        "company": company.text if company else "Unknown",
                        "location": "India / Remote",
                        "source": "Google Jobs",
                        "applyLink": url,
                        "description": title.text,
                        "postedDate": datetime.utcnow().isoformat(),
                        "engagement": {"likes": 0, "comments": 0, "isUnseen": False},
                        "matchScore": 0,
                        "fetchedAt": datetime.utcnow().isoformat(),
                        "isManual": False
                    })

                time.sleep(2)

            except:
                continue

    # --------------------------------------------------
    # Resume Matching
    # --------------------------------------------------

    def calculate_match_score(self, job, profile):
        score = 60

        if any(r.lower() in job["title"].lower() for r in profile["targetRoles"]):
            score += 15

        if any(loc.lower() in job["location"].lower() for loc in profile["location"]):
            score += 10

        skill_hits = sum(1 for s in profile["skills"] if s.lower() in job["description"].lower())
        score += min(skill_hits * 3, 15)

        return min(score, 95)

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

    # --------------------------------------------------
    # Run
    # --------------------------------------------------

    def run(self, user_profile):
        print("🚀 Starting scrape...")

        self.scrape_career_pages()
        self.scrape_google_jobs()
        self.dedupe()

        for job in self.jobs:
            job["matchScore"] = self.calculate_match_score(job, user_profile)

        print(f"✅ Total jobs after scoring: {len(self.jobs)}")
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
        "targetRoles": ["Product Manager", "Associate Product Manager", "Product Analyst"],
        "skills": ["SQL", "Python", "A/B Testing", "Product Strategy", "Analytics"],
        "location": ["Remote", "Bangalore", "India"]
    }

    scraper = JobScraper()
    jobs = scraper.run(profile)
    scraper.save()

