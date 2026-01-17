"""
Job Intelligence Scraper - Improved Version
Finds real PM jobs that actually exist
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
from urllib.parse import urljoin, quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

class JobScraper:
    def __init__(self):
        self.jobs = []
        
        self.product_keywords = [
            "product manager",
            "associate product manager",
            "apm",
            "product analyst",
            "product owner",
            "technical product manager",
            "senior product manager",
            "growth product manager"
        ]
        
        # Expanded company list with verified career pages
        self.target_companies = [
            {"name": "Razorpay", "url": "https://razorpay.com/jobs/"},
            {"name": "CRED", "url": "https://careers.cred.club/"},
            {"name": "Swiggy", "url": "https://careers.swiggy.com/"},
            {"name": "Meesho", "url": "https://www.meesho.io/careers"},
            {"name": "PhonePe", "url": "https://www.phonepe.com/careers/"},
            {"name": "Paytm", "url": "https://jobs.lever.co/paytm"},
            {"name": "Flipkart", "url": "https://www.flipkartcareers.com/"},
            {"name": "Zepto", "url": "https://www.zepto.co.in/careers"},
            {"name": "Urban Company", "url": "https://www.urbancompany.com/careers"},
            {"name": "Groww", "url": "https://groww.in/careers"},
        ]

    def normalize(self, text):
        """Clean text for matching"""
        return re.sub(r"\s+", " ", text.lower().strip())

    def is_pm_role(self, text):
        """Check if text contains PM keywords"""
        text = self.normalize(text)
        return any(keyword in text for keyword in self.product_keywords)

    def scrape_leverage_jobs(self):
        """Scrape companies using Lever ATS"""
        print("🔍 Scraping Lever job boards...")
        
        lever_companies = ["paytm", "razorpay"]
        
        for company in lever_companies:
            try:
                url = f"https://jobs.lever.co/{company}"
                res = requests.get(url, headers=HEADERS, timeout=10)
                
                if res.status_code != 200:
                    continue
                
                soup = BeautifulSoup(res.text, "html.parser")
                postings = soup.find_all("a", class_="posting-title")
                
                for posting in postings:
                    title = posting.get_text(strip=True)
                    
                    if not self.is_pm_role(title):
                        continue
                    
                    job_url = posting.get("href", "")
                    if not job_url.startswith("http"):
                        job_url = urljoin(url, job_url)
                    
                    job = {
                        "id": f"lever_{company}_{hash(job_url)}",
                        "title": title,
                        "company": company.capitalize(),
                        "location": "Check job page",
                        "source": "Lever (Career Page)",
                        "applyLink": job_url,
                        "description": f"{title} at {company}",
                        "postedDate": datetime.utcnow().isoformat(),
                        "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                        "matchScore": 72,
                        "deadline": None,
                        "status": None,
                        "fetchedAt": datetime.utcnow().isoformat(),
                        "isManual": False
                    }
                    
                    self.jobs.append(job)
                    print(f"  ✅ Found: {title} at {company}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error with {company}: {e}")
        
        print(f"✅ Lever: Found {len([j for j in self.jobs if 'Lever' in j['source']])} jobs")

    def scrape_greenhouse_jobs(self):
        """Scrape companies using Greenhouse ATS"""
        print("🔍 Scraping Greenhouse job boards...")
        
        greenhouse_companies = [
            {"name": "Cred", "id": "cred"},
            {"name": "Meesho", "id": "meesho"},
        ]
        
        for company in greenhouse_companies:
            try:
                url = f"https://boards.greenhouse.io/{company['id']}"
                res = requests.get(url, headers=HEADERS, timeout=10)
                
                if res.status_code != 200:
                    continue
                
                soup = BeautifulSoup(res.text, "html.parser")
                
                # Greenhouse uses various HTML structures
                job_sections = soup.find_all("section", class_="level-0")
                
                for section in job_sections:
                    jobs_list = section.find_all("div", class_="opening")
                    
                    for job_div in jobs_list:
                        link = job_div.find("a")
                        if not link:
                            continue
                        
                        title = link.get_text(strip=True)
                        
                        if not self.is_pm_role(title):
                            continue
                        
                        job_url = link.get("href", "")
                        if not job_url.startswith("http"):
                            job_url = urljoin(url, job_url)
                        
                        location_div = job_div.find("span", class_="location")
                        location = location_div.get_text(strip=True) if location_div else "Remote"
                        
                        job = {
                            "id": f"greenhouse_{company['id']}_{hash(job_url)}",
                            "title": title,
                            "company": company['name'],
                            "location": location,
                            "source": "Greenhouse (Career Page)",
                            "applyLink": job_url,
                            "description": f"{title} at {company['name']}",
                            "postedDate": datetime.utcnow().isoformat(),
                            "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                            "matchScore": 75,
                            "deadline": None,
                            "status": None,
                            "fetchedAt": datetime.utcnow().isoformat(),
                            "isManual": False
                        }
                        
                        self.jobs.append(job)
                        print(f"  ✅ Found: {title} at {company['name']}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error with {company['name']}: {e}")
        
        print(f"✅ Greenhouse: Found {len([j for j in self.jobs if 'Greenhouse' in j['source']])} jobs")

    def scrape_naukri(self):
        """Scrape Naukri.com"""
        print("🔍 Scraping Naukri...")
        
        search_terms = ["product+manager", "associate+product+manager"]
        
        for term in search_terms:
            try:
                url = f"https://www.naukri.com/{term}-jobs"
                res = requests.get(url, headers=HEADERS, timeout=10)
                
                if res.status_code != 200:
                    continue
                
                soup = BeautifulSoup(res.text, "html.parser")
                job_cards = soup.find_all("article", class_="jobTuple")[:15]
                
                for card in job_cards:
                    try:
                        title_elem = card.find("a", class_="title")
                        company_elem = card.find("a", class_="subTitle")
                        
                        if not title_elem or not company_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        
                        if not self.is_pm_role(title):
                            continue
                        
                        location_elem = card.find("li", class_="location")
                        location = location_elem.get_text(strip=True) if location_elem else "India"
                        
                        job_url = title_elem.get("href", "")
                        if job_url and not job_url.startswith("http"):
                            job_url = "https://www.naukri.com" + job_url
                        
                        job = {
                            "id": f"naukri_{hash(job_url)}_{int(time.time())}",
                            "title": title,
                            "company": company,
                            "location": location,
                            "source": "Naukri",
                            "applyLink": job_url if job_url else url,
                            "description": f"{title} opportunity at {company}",
                            "postedDate": datetime.utcnow().isoformat(),
                            "engagement": {"likes": 0, "comments": 0, "isUnseen": False},
                            "matchScore": 70,
                            "deadline": None,
                            "status": None,
                            "fetchedAt": datetime.utcnow().isoformat(),
                            "isManual": False
                        }
                        
                        self.jobs.append(job)
                        print(f"  ✅ Found: {title} at {company}")
                        
                    except Exception as e:
                        print(f"  ⚠️ Error parsing Naukri card: {e}")
                        continue
                
                time.sleep(3)
                
            except Exception as e:
                print(f"  ❌ Naukri error ({term}): {e}")
        
        print(f"✅ Naukri: Found {len([j for j in self.jobs if j['source'] == 'Naukri'])} jobs")

    def scrape_instahyre(self):
        """Scrape Instahyre"""
        print("🔍 Scraping Instahyre...")
        
        try:
            url = "https://www.instahyre.com/search-jobs/?q=product+manager"
            res = requests.get(url, headers=HEADERS, timeout=10)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                job_cards = soup.find_all("div", class_="opportunity-card")[:10]
                
                for card in job_cards:
                    try:
                        title_elem = card.find("a", class_="job-title")
                        company_elem = card.find("a", class_="employer-name")
                        
                        if title_elem and company_elem:
                            title = title_elem.get_text(strip=True)
                            company = company_elem.get_text(strip=True)
                            
                            if self.is_pm_role(title):
                                job_url = title_elem.get("href", "")
                                if job_url and not job_url.startswith("http"):
                                    job_url = "https://www.instahyre.com" + job_url
                                
                                job = {
                                    "id": f"instahyre_{hash(job_url)}_{int(time.time())}",
                                    "title": title,
                                    "company": company,
                                    "location": "India",
                                    "source": "Instahyre",
                                    "applyLink": job_url if job_url else url,
                                    "description": f"{title} at {company}",
                                    "postedDate": datetime.utcnow().isoformat(),
                                    "engagement": {"likes": 0, "comments": 0, "isUnseen": False},
                                    "matchScore": 73,
                                    "deadline": None,
                                    "status": None,
                                    "fetchedAt": datetime.utcnow().isoformat(),
                                    "isManual": False
                                }
                                
                                self.jobs.append(job)
                                print(f"  ✅ Found: {title} at {company}")
                    
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"  ❌ Instahyre error: {e}")
        
        print(f"✅ Instahyre: Found {len([j for j in self.jobs if j['source'] == 'Instahyre'])} jobs")

    def calculate_match_score(self, job, profile):
        """Calculate match score"""
        score = 60
        
        # Role match
        if any(role.lower() in job["title"].lower() for role in profile["targetRoles"]):
            score += 15
        
        # Location match
        if any(loc.lower() in job["location"].lower() for loc in profile["location"]):
            score += 10
        
        # Skills match
        desc_lower = job["description"].lower()
        skill_matches = sum(1 for skill in profile["skills"] if skill.lower() in desc_lower)
        score += min(skill_matches * 3, 15)
        
        return min(score, 98)

    def dedupe(self):
        """Remove duplicates"""
        seen = set()
        unique = []
        
        for job in self.jobs:
            key = f"{job['title'].lower()}_{job['company'].lower()}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        
        removed = len(self.jobs) - len(unique)
        self.jobs = unique
        
        if removed > 0:
            print(f"🔄 Removed {removed} duplicates")

    def run(self, profile):
        """Run all scrapers"""
        print("🚀 Starting job scraping...")
        print(f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        # Run all scrapers
        self.scrape_leverage_jobs()
        self.scrape_greenhouse_jobs()
        self.scrape_naukri()
        self.scrape_instahyre()
        
        # Clean up
        self.dedupe()
        
        # Update match scores
        for job in self.jobs:
            job["matchScore"] = self.calculate_match_score(job, profile)
        
        print(f"\n✅ TOTAL JOBS FOUND: {len(self.jobs)}")
        print(f"   High match (80%+): {len([j for j in self.jobs if j['matchScore'] >= 80])}")
        print(f"   Good match (70-79%): {len([j for j in self.jobs if 70 <= j['matchScore'] < 80])}")
        
        return self.jobs

    def save(self, filename="jobs_data.json"):
        """Save to file"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {filename}")


if __name__ == "__main__":
    profile = {
        "targetRoles": [
            "Product Manager",
            "Associate Product Manager",
            "Product Analyst",
            "Senior Product Manager"
        ],
        "skills": [
            "SQL", "Python", "A/B Testing",
            "Product Strategy", "Analytics",
            "User Research", "Roadmap"
        ],
        "location": ["Remote", "India", "Bangalore", "Mumbai"]
    }
    
    scraper = JobScraper()
    jobs = scraper.run(profile)
    scraper.save()
    
    print("\n📊 Job Sources Breakdown:")
    sources = {}
    for job in jobs:
        source = job["source"]
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sources.items():
        print(f"   {source}: {count} jobs")
