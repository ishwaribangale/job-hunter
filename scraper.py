"""
Job Intelligence Scraper - Debug Version
Detailed logging to see what's happening
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class JobScraper:
    def __init__(self):
        self.jobs = []

    def test_connection(self):
        """Test if we can reach job sites"""
        print("\n🧪 Testing connections...")
        
        test_urls = [
            "https://jobs.lever.co/paytm",
            "https://www.naukri.com/product-manager-jobs",
            "https://razorpay.com/jobs/"
        ]
        
        for url in test_urls:
            try:
                res = requests.get(url, headers=HEADERS, timeout=10)
                print(f"✅ {url}")
                print(f"   Status: {res.status_code}")
                print(f"   Content length: {len(res.text)} chars")
            except Exception as e:
                print(f"❌ {url}")
                print(f"   Error: {e}")

    def scrape_lever_simple(self):
        """Simple Lever scraper with debug info"""
        print("\n🔍 Scraping Lever (Paytm)...")
        
        try:
            url = "https://jobs.lever.co/paytm"
            print(f"📍 Fetching: {url}")
            
            res = requests.get(url, headers=HEADERS, timeout=15)
            print(f"✅ Status code: {res.status_code}")
            print(f"✅ Response size: {len(res.text)} chars")
            
            if res.status_code != 200:
                print(f"❌ Non-200 status code")
                return
            
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Debug: See what we got
            print(f"✅ Parsed HTML successfully")
            
            # Try multiple selectors
            postings1 = soup.find_all("a", class_="posting-title")
            postings2 = soup.find_all("div", class_="posting")
            postings3 = soup.find_all("a", href=lambda x: x and "/paytm/" in str(x))
            
            print(f"📊 Found posting-title links: {len(postings1)}")
            print(f"📊 Found posting divs: {len(postings2)}")
            print(f"📊 Found paytm links: {len(postings3)}")
            
            # Use whichever works
            postings = postings1 if postings1 else postings3
            
            if not postings:
                print("❌ No job postings found!")
                # Save HTML for debugging
                with open("debug_lever.html", "w") as f:
                    f.write(res.text[:5000])  # First 5000 chars
                print("💾 Saved sample HTML to debug_lever.html")
                return
            
            for posting in postings[:20]:  # Limit to 20
                try:
                    title = posting.get_text(strip=True)
                    href = posting.get("href", "")
                    
                    print(f"  📄 Found: {title[:50]}")
                    
                    # Check for PM keywords
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in ["product", "pm", "apm"]):
                        job_url = href if href.startswith("http") else f"https://jobs.lever.co{href}"
                        
                        job = {
                            "id": f"lever_paytm_{hash(job_url)}",
                            "title": title,
                            "company": "Paytm",
                            "location": "India",
                            "source": "Lever",
                            "applyLink": job_url,
                            "description": f"{title} at Paytm",
                            "postedDate": datetime.utcnow().isoformat(),
                            "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                            "matchScore": 75,
                            "deadline": None,
                            "status": None,
                            "fetchedAt": datetime.utcnow().isoformat(),
                            "isManual": False
                        }
                        
                        self.jobs.append(job)
                        print(f"    ✅ Added to results!")
                
                except Exception as e:
                    print(f"    ⚠️ Error parsing posting: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Lever error: {e}")
            import traceback
            traceback.print_exc()

    def scrape_static_fallback(self):
        """Add some static jobs as fallback"""
        print("\n📦 Adding fallback jobs...")
        
        fallback_jobs = [
            {
                "id": "fallback_razorpay_pm",
                "title": "Product Manager",
                "company": "Razorpay",
                "location": "Bangalore / Remote",
                "source": "Career Page (Manual)",
                "applyLink": "https://razorpay.com/jobs/",
                "description": "Product Manager role at Razorpay. Check career page for current openings.",
                "postedDate": datetime.utcnow().isoformat(),
                "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                "matchScore": 72,
                "deadline": None,
                "status": None,
                "fetchedAt": datetime.utcnow().isoformat(),
                "isManual": False
            },
            {
                "id": "fallback_cred_apm",
                "title": "Associate Product Manager",
                "company": "CRED",
                "location": "Bangalore",
                "source": "Career Page (Manual)",
                "applyLink": "https://careers.cred.club/",
                "description": "APM role at CRED. Check career page for current openings.",
                "postedDate": datetime.utcnow().isoformat(),
                "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                "matchScore": 78,
                "deadline": None,
                "status": None,
                "fetchedAt": datetime.utcnow().isoformat(),
                "isManual": False
            },
            {
                "id": "fallback_swiggy_pm",
                "title": "Product Manager - Growth",
                "company": "Swiggy",
                "location": "Bangalore",
                "source": "Career Page (Manual)",
                "applyLink": "https://careers.swiggy.com/",
                "description": "Growth PM role at Swiggy. Check career page for current openings.",
                "postedDate": datetime.utcnow().isoformat(),
                "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                "matchScore": 75,
                "deadline": None,
                "status": None,
                "fetchedAt": datetime.utcnow().isoformat(),
                "isManual": False
            },
            {
                "id": "fallback_phonepe_pm",
                "title": "Senior Product Manager",
                "company": "PhonePe",
                "location": "Bangalore",
                "source": "Career Page (Manual)",
                "applyLink": "https://www.phonepe.com/careers/",
                "description": "Senior PM role at PhonePe. Check career page for current openings.",
                "postedDate": datetime.utcnow().isoformat(),
                "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                "matchScore": 80,
                "deadline": None,
                "status": None,
                "fetchedAt": datetime.utcnow().isoformat(),
                "isManual": False
            },
            {
                "id": "fallback_meesho_analyst",
                "title": "Product Analyst",
                "company": "Meesho",
                "location": "Bangalore / Remote",
                "source": "Career Page (Manual)",
                "applyLink": "https://www.meesho.io/careers",
                "description": "Product Analyst role at Meesho. Check career page for current openings.",
                "postedDate": datetime.utcnow().isoformat(),
                "engagement": {"likes": 0, "comments": 0, "isUnseen": True},
                "matchScore": 70,
                "deadline": None,
                "status": None,
                "fetchedAt": datetime.utcnow().isoformat(),
                "isManual": False
            }
        ]
        
        self.jobs.extend(fallback_jobs)
        print(f"✅ Added {len(fallback_jobs)} fallback jobs")

    def run(self):
        """Run scraper with debug info"""
        print("=" * 60)
        print("🚀 JOB SCRAPER - DEBUG MODE")
        print("=" * 60)
        print(f"⏰ Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        # Test connections
        self.test_connection()
        
        # Try scraping
        self.scrape_lever_simple()
        
        # Add fallback jobs so dashboard has something to show
        if len(self.jobs) < 5:
            print("\n⚠️ Few jobs found, adding fallback jobs...")
            self.scrape_static_fallback()
        
        print("\n" + "=" * 60)
        print(f"✅ TOTAL JOBS: {len(self.jobs)}")
        print("=" * 60)
        
        if self.jobs:
            print("\n📋 Sample jobs:")
            for job in self.jobs[:3]:
                print(f"  • {job['title']} at {job['company']}")
        
        return self.jobs

    def save(self, filename="jobs_data.json"):
        """Save to JSON"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved to {filename}")
        print(f"📊 File size: {len(json.dumps(self.jobs))} bytes")


if __name__ == "__main__":
    scraper = JobScraper()
    jobs = scraper.run()
    scraper.save()
    
    print("\n✅ Scraper finished!")
    print(f"📦 Ready for dashboard: {len(jobs)} jobs")
