# scraper_enhanced.py
# ----------------------------------
# Enhanced scraper with better company job detection
# ----------------------------------

import os
import json
import re
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT, TOP_COMPANIES, CAREER_PAGES
from roles import infer_role
from scoring import score_job

SCRAPE_MODE = "VOLUME"


class EnhancedJobScraper:
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

    # ===================================================================
    # ENHANCED ATS DETECTION
    # ===================================================================

    def detect_ats_system(self, url, company_name):
        """
        Advanced ATS detection by checking redirects and page content
        """
        print(f"  🔍 Detecting ATS for {company_name}...")
        
        headers = {
            **HEADERS,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        
        try:
            # Follow redirects to find actual job board
            r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            final_url = r.url.lower()
            content = r.text.lower()
            
            # Check URL patterns
            if "greenhouse.io" in final_url or "boards.greenhouse" in final_url:
                # Extract slug from URL
                match = re.search(r'greenhouse\.io/(?:embed/job_board\?for=)?([^/?&]+)', final_url)
                if match:
                    return ("greenhouse", match.group(1))
                return ("greenhouse", None)
            
            if "lever.co" in final_url or "jobs.lever" in final_url:
                match = re.search(r'lever\.co/([^/?&]+)', final_url)
                if match:
                    return ("lever", match.group(1))
                return ("lever", None)
            
            if "ashbyhq.com" in final_url or "jobs.ashbyhq" in final_url:
                match = re.search(r'ashbyhq\.com/([^/?&]+)', final_url)
                if match:
                    return ("ashbyhq", match.group(1))
                return ("ashbyhq", None)
            
            if "workday" in final_url or "myworkdayjobs" in final_url:
                return ("workday", None)
            
            if "jobvite.com" in final_url:
                return ("jobvite", None)
            
            if "bamboohr.com" in final_url:
                return ("bamboohr", None)
            
            # Check page content for embedded ATS
            if "greenhouse.io" in content[:10000]:
                # Look for embedded Greenhouse board
                match = re.search(r'greenhouse\.io/(?:embed/job_board\?for=)?([^"\'&]+)', content)
                if match:
                    return ("greenhouse", match.group(1))
            
            if "lever.co" in content[:10000]:
                match = re.search(r'lever\.co/([^"\'&/]+)', content)
                if match:
                    return ("lever", match.group(1))
            
            if "ashbyhq.com" in content[:10000]:
                match = re.search(r'jobs\.ashbyhq\.com/([^"\'&/]+)', content)
                if match:
                    return ("ashbyhq", match.group(1))
            
            # Check for common patterns in content
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Look for job links to infer ATS
            job_links = soup.find_all('a', href=True)
            for link in job_links[:50]:  # Check first 50 links
                href = link.get('href', '').lower()
                if 'greenhouse.io' in href:
                    match = re.search(r'greenhouse\.io/([^/?&]+)', href)
                    if match:
                        return ("greenhouse", match.group(1))
                if 'lever.co' in href:
                    match = re.search(r'lever\.co/([^/?&]+)', href)
                    if match:
                        return ("lever", match.group(1))
                if 'ashbyhq.com' in href:
                    match = re.search(r'ashbyhq\.com/([^/?&]+)', href)
                    if match:
                        return ("ashbyhq", match.group(1))
            
            return ("generic", None)
            
        except Exception as e:
            print(f"  ⚠ Detection error: {e}")
            return ("generic", None)

    # ===================================================================
    # IMPROVED ATS SCRAPERS
    # ===================================================================

    def scrape_greenhouse(self, company_name, slug):
        """Scrape Greenhouse job board"""
        url = f"https://boards.greenhouse.io/{slug}"
        
        headers = {
            **HEADERS,
            "Accept": "text/html",
        }
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code != 200:
                print(f"  ⚠ HTTP {r.status_code}")
                return
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Try multiple selectors for Greenhouse
            jobs = (
                soup.select("div.opening a") or
                soup.select("a[href*='/jobs/']") or
                soup.select("div.job a") or
                soup.select("section a[href*='/jobs/']")
            )
            
            # Filter valid jobs
            job_id_pattern = r'/jobs/(\d+)'
            valid_jobs = []
            
            for a in jobs:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not href or not title or len(title) < 5:
                    continue
                
                if not re.search(job_id_pattern, href):
                    continue
                
                skip_keywords = [
                    "all jobs", "view all", "departments",
                    "locations", "teams", "browse", "filter"
                ]
                if any(word in title.lower() for word in skip_keywords):
                    continue
                
                valid_jobs.append((href, title, a))
            
            print(f"  ✓ Greenhouse: {len(valid_jobs)} jobs")
            
            for href, title, elem in valid_jobs:
                location = "Various"
                
                # Try to find location
                parent = elem.find_parent("div", class_="opening")
                if parent:
                    loc_elem = parent.select_one("span.location")
                    if loc_elem:
                        location = loc_elem.get_text(strip=True)
                
                full_url = href if href.startswith("http") else f"https://boards.greenhouse.io{href}"
                
                job_id_match = re.search(job_id_pattern, href)
                job_id = job_id_match.group(1) if job_id_match else str(hash(href))
                
                self.add({
                    "id": f"gh_{company_name}_{job_id}",
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "source": f"{company_name} (Greenhouse)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Greenhouse error: {e}")

    def scrape_lever(self, company_name, slug):
        """Scrape Lever job board"""
        api_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        
        headers = {
            **HEADERS,
            "Accept": "application/json",
        }
        
        try:
            # Try API first
            r = requests.get(api_url, headers=headers, timeout=10)
            
            if r.status_code == 200 and r.text.strip().startswith("["):
                jobs = r.json()
                print(f"  ✓ Lever API: {len(jobs)} jobs")
                
                for j in jobs:
                    self.add({
                        "id": f"lever_{company_name}_{j.get('id', hash(j.get('text', '')))}",
                        "title": j.get("text", ""),
                        "company": company_name,
                        "location": j.get("categories", {}).get("location", "Various"),
                        "source": f"{company_name} (Lever)",
                        "applyLink": j.get("hostedUrl", ""),
                        "postedDate": self.now(),
                    })
                return
            
            # Fallback to HTML
            print("  ⚠ Lever API failed, trying HTML...")
            html_url = f"https://jobs.lever.co/{slug}"
            r = requests.get(html_url, headers={**HEADERS, "Accept": "text/html"}, timeout=10)
            
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = soup.select("a.posting-title")
            
            print(f"  ✓ Lever HTML: {len(jobs)} jobs")
            
            for a in jobs:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not href or not title:
                    continue
                
                self.add({
                    "id": f"lever_{company_name}_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Lever)",
                    "applyLink": href,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Lever error: {e}")

    def scrape_ashby(self, company_name, slug):
        """Scrape Ashby job board"""
        url = f"https://jobs.ashbyhq.com/{slug}"
        
        headers = {
            **HEADERS,
            "Accept": "text/html",
        }
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Ashby uses specific patterns
            jobs = soup.select("a[href*='/jobs/']")
            
            uuid_pattern = r'/[a-f0-9-]{36}'
            valid_jobs = []
            
            for a in jobs:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not re.search(uuid_pattern, href):
                    continue
                
                if not title or len(title) < 5:
                    continue
                
                valid_jobs.append((href, title))
            
            print(f"  ✓ Ashby: {len(valid_jobs)} jobs")
            
            for href, title in valid_jobs:
                full_url = href if href.startswith("http") else f"https://jobs.ashbyhq.com{href}"
                
                self.add({
                    "id": f"ashby_{company_name}_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Ashby)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Ashby error: {e}")

    def scrape_generic_improved(self, company_name, url):
        """
        Improved generic scraper with better pattern matching
        """
        headers = {
            **HEADERS,
            "Accept": "text/html",
        }
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Comprehensive selectors for job listings
            selectors = [
                # Common class-based selectors
                "a.job-title",
                "a.position-title",
                "a.posting-title",
                "a[class*='job']",
                "a[class*='position']",
                "a[class*='opening']",
                "a[class*='role']",
                
                # Href-based selectors (more flexible)
                "a[href*='/jobs/'][href*='-']",
                "a[href*='/job/']",
                "a[href*='/careers/'][href*='job']",
                "a[href*='/positions/']",
                "a[href*='/openings/']",
                "a[href*='/roles/']",
                "a[href*='apply']",
                
                # Container-based
                "div[class*='job'] a",
                "div[class*='position'] a",
                "div[class*='opening'] a",
                "li[class*='job'] a",
            ]
            
            all_jobs = []
            for selector in selectors:
                found = soup.select(selector)
                all_jobs.extend(found)
            
            # Remove duplicates
            seen_hrefs = set()
            unique_jobs = []
            for a in all_jobs:
                href = a.get("href", "")
                if href and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    unique_jobs.append(a)
            
            # Filter valid jobs
            skip_patterns = [
                r'^/$',
                r'^/careers/?$',
                r'^/jobs/?$',
                r'/departments',
                r'/locations',
                r'/teams',
                r'/about',
                r'/contact',
            ]
            
            skip_keywords = [
                "all jobs", "view all", "see all", "departments",
                "locations", "open positions", "browse",
                "filter", "search", "apply now", "learn more"
            ]
            
            valid_jobs = []
            for a in unique_jobs:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not href or not title or len(title) < 5:
                    continue
                
                # Skip navigation links
                if any(re.search(pattern, href, re.I) for pattern in skip_patterns):
                    continue
                
                # Skip generic text
                if any(word in title.lower() for word in skip_keywords):
                    continue
                
                # Must have some job-like characteristics
                job_indicators = [
                    '/job/', '/position/', '/opening/', '/role/',
                    'apply', 'posting', '-' in href
                ]
                if not any(indicator in href.lower() for indicator in job_indicators):
                    continue
                
                valid_jobs.append((href, title))
            
            print(f"  ✓ Generic: {len(valid_jobs)} jobs")
            
            for href, title in valid_jobs:
                # Build full URL
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    base = url.split("/careers")[0].split("/jobs")[0]
                    full_url = base + href
                else:
                    full_url = url.rstrip("/") + "/" + href
                
                self.add({
                    "id": f"generic_{company_name}_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Career)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Generic scraper error: {e}")

    # ===================================================================
    # MAIN COMPANY SCRAPER
    # ===================================================================

    def scrape_companies(self):
        """
        Main method to scrape all companies with smart ATS detection
        """
        print("\n[COMPANY JOBS - Enhanced Detection]")
        print(f"Total companies: {len(CAREER_PAGES)}")
        
        for company in CAREER_PAGES:
            company_name = company.get("name", "Unknown")
            company_url = company.get("url", "")
            
            print(f"\n{'='*60}")
            print(f"[{company_name}]")
            print(f"URL: {company_url}")
            
            if not company_url:
                print("  ⚠ No URL provided")
                continue
            
            try:
                # Detect ATS system
                ats_type, slug = self.detect_ats_system(company_url, company_name)
                print(f"  📋 Detected: {ats_type}" + (f" (slug: {slug})" if slug else ""))
                
                # Scrape using appropriate method
                if ats_type == "greenhouse" and slug:
                    self.scrape_greenhouse(company_name, slug)
                elif ats_type == "lever" and slug:
                    self.scrape_lever(company_name, slug)
                elif ats_type == "ashby" and slug:
                    self.scrape_ashby(company_name, slug)
                elif ats_type == "workday":
                    print("  ⚠ Workday requires JavaScript - skipping")
                else:
                    # Fallback to generic scraper
                    self.scrape_generic_improved(company_name, company_url)
                
                time.sleep(0.5)  # Be respectful
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")

    # ===================================================================
    # TOP COMPANIES (from config)
    # ===================================================================

    def scrape_top_companies(self):
        """Scrape TOP_COMPANIES with known ATS systems"""
        print("\n[TOP COMPANIES - Known ATS]")
        print(f"Companies configured: {len(TOP_COMPANIES)}")
        
        for company in TOP_COMPANIES:
            company_name = company.get("name", "Unknown")
            ats = company.get("ats", "")
            slug = company.get("slug", "")
            
            print(f"\n[{company_name}] ATS: {ats}")
            
            try:
                if ats == "greenhouse":
                    self.scrape_greenhouse(company_name, slug)
                elif ats == "lever":
                    self.scrape_lever(company_name, slug)
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")

    # ===================================================================
    # SAVE & STATS
    # ===================================================================

    def save(self):
        os.makedirs("data", exist_ok=True)
        
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(
                sorted(self.jobs, key=lambda x: x["score"], reverse=True),
                f,
                indent=2,
                ensure_ascii=False,
            )
        
        print("\n" + "="*60)
        print("[SOURCE SUMMARY]")
        for k, v in sorted(self.stats.items()):
            print(f"  {k}: {v}")
        
        print(f"\n✅ TOTAL JOBS: {len(self.jobs)}")
        print(f"💾 Saved → data/jobs.json")


# ===================================================================
# USAGE
# ===================================================================

if __name__ == "__main__":
    scraper = EnhancedJobScraper()
    
    # Test with a few companies first
    print("\n🧪 TESTING MODE - Top 5 companies")
    test_companies = CAREER_PAGES[:5]
    
    for company in test_companies:
        company_name = company.get("name", "Unknown")
        company_url = company.get("url", "")
        
        print(f"\n{'='*60}")
        print(f"[{company_name}]")
        
        try:
            ats_type, slug = scraper.detect_ats_system(company_url, company_name)
            print(f"  Detected: {ats_type}" + (f" (slug: {slug})" if slug else ""))
            
            if ats_type == "greenhouse" and slug:
                scraper.scrape_greenhouse(company_name, slug)
            elif ats_type == "lever" and slug:
                scraper.scrape_lever(company_name, slug)
            elif ats_type == "ashby" and slug:
                scraper.scrape_ashby(company_name, slug)
            else:
                scraper.scrape_generic_improved(company_name, company_url)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    scraper.save()
    
    # Uncomment to run on all companies:
    # scraper.scrape_companies()
    # scraper.save()
