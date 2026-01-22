# scraper.py
# ----------------------------------
# PJIS – Job Intelligence Scraper
# ENHANCED - Fixed Company Scraping
# ----------------------------------

import os
import json
import re
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT, TOP_COMPANIES, CAREER_PAGES, ASHBY_COMPANIES
from roles import infer_role
from scoring import score_job

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

    def scrape_remoteco(self):
        print("\n[Remote.co]")
        url = "https://remote.co/remote-jobs"
        headers = {**HEADERS, "User-Agent": "Mozilla/5.0", "Accept": "text/html"}
    
        for attempt in range(2):
            try:
                r = requests.get(url, headers=headers, timeout=(5, 10))
                if r.status_code != 200:
                    print(f"  ⚠ HTTP {r.status_code}")
                    return
    
                soup = BeautifulSoup(r.text, "html.parser")
                cards = soup.select("div.card")
                print(f"  Jobs found: {len(cards)}")
    
                for c in cards:
                    title = c.select_one("h3 a")
                    company = c.select_one("p.company")
                    if not title or not company:
                        continue
    
                    self.add({
                        "id": f"remoteco_{hash(title['href'])}",
                        "title": title.get_text(strip=True),
                        "company": company.get_text(strip=True),
                        "location": "Remote",
                        "source": "Remote.co",
                        "applyLink": title["href"],
                        "postedDate": self.now(),
                    })
                return
    
            except requests.exceptions.ReadTimeout:
                print(f"  ⏱ Timeout (attempt {attempt + 1}/2)")
            except Exception as e:
                print(f"  ❌ Remote.co failed: {e}")
                return
    
        print("  ⚠ Remote.co skipped after retries")

    def scrape_remotive(self):
        print("\n[Remotive]")
        categories = [None, "software-dev", "product", "design", "marketing", 
                     "sales", "data", "customer-support", "devops", "qa", "finance"]
    
        for cat in categories:
            url = "https://remotive.com/api/remote-jobs"
            if cat:
                url += f"?category={cat}"
    
            try:
                r = requests.get(url, headers=HEADERS, timeout=10)
                data = r.json().get("jobs", [])
                label = "all" if not cat else cat
                print(f"  Category '{label}': {len(data)} jobs")
    
                for j in data:
                    self.add({
                        "id": f"remotive_{j['id']}",
                        "title": j["title"],
                        "company": j["company_name"],
                        "location": j.get("candidate_required_location", "Remote"),
                        "source": "Remotive",
                        "applyLink": j["url"],
                        "postedDate": j["publication_date"],
                    })
            except Exception as e:
                print(f"  ❌ Remotive '{cat}' failed: {e}")

    def scrape_wellfound(self):
        print("\n[Wellfound]")
        url = "https://wellfound.com/jobs"
        headers = {**HEADERS, "User-Agent": "Mozilla/5.0", "Accept": "text/html"}
    
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ HTTP {r.status_code}")
                return
    
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("a[href^='/company/'][href*='/jobs/']")
            print(f"  Jobs found: {len(cards)}")
    
            for a in cards:
                href = a.get("href")
                title = a.get_text(strip=True)
                if not href or not title:
                    continue
    
                self.add({
                    "id": f"wellfound_{hash(href)}",
                    "title": title,
                    "company": "Startup (Wellfound)",
                    "location": "Remote / Hybrid",
                    "source": "Wellfound",
                    "applyLink": "https://wellfound.com" + href,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ Wellfound failed: {e}")

    def scrape_remoteok(self):
        print("\n[RemoteOK]")
        base = "https://remoteok.com/api"
        tags = [None, "engineer", "software-dev", "frontend", "backend", "fullstack",
                "product", "design", "data", "marketing", "sales", "customer-support"]
    
        headers = {**HEADERS, "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)", 
                  "Accept": "application/json"}
    
        for tag in tags:
            url = base if tag is None else f"{base}?tag={tag}"
            label = "main" if tag is None else tag
    
            try:
                r = requests.get(url, headers=headers, timeout=6)
                if r.status_code != 200:
                    print(f"  ⚠ {label}: HTTP {r.status_code}")
                    continue
    
                data = r.json()
                if not isinstance(data, list) or len(data) < 2:
                    print(f"  ⚠ {label}: invalid payload")
                    continue
    
                jobs = data[1:]
                print(f"  {label}: {len(jobs)} jobs")
    
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
            except Exception as e:
                print(f"  ❌ {label} failed: {e}")

    def scrape_weworkremotely(self):
        print("\n[WeWorkRemotely]")
        base = "https://weworkremotely.com/categories"
        categories = ["remote-programming-jobs", "remote-design-jobs", "remote-product-jobs",
                     "remote-sales-and-marketing-jobs", "remote-customer-support-jobs"]
    
        headers = {**HEADERS, "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)", 
                  "Accept": "text/html"}
        MAX_PAGES = 10
        MAX_TIMEOUTS = 2
    
        for cat in categories:
            print(f"\nCategory: {cat}")
            page = 1
            timeouts = 0
    
            while page <= MAX_PAGES:
                url = f"{base}/{cat}" + (f"?page={page}" if page > 1 else "")
    
                try:
                    r = requests.get(url, headers=headers, timeout=6)
                    if r.status_code != 200:
                        print(f"  ⚠ Page {page}: HTTP {r.status_code}")
                        break
    
                    if "<rss" in r.text.lower():
                        print("  ⚠ RSS detected, stopping")
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
                    timeouts = 0
    
                except requests.exceptions.ReadTimeout:
                    timeouts += 1
                    print(f"  ⏱ Page {page}: timeout ({timeouts}/{MAX_TIMEOUTS})")
                    if timeouts >= MAX_TIMEOUTS:
                        break
                except Exception as e:
                    print(f"  ❌ Page {page}: failed → {e}")
                    break

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
                browser = p.chromium.launch(headless=True, 
                    args=["--no-sandbox", "--disable-dev-shm-usage"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, timeout=30_000)
                page.wait_for_timeout(3000)
    
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
            print(f"  ❌ YC Playwright failed: {e}")

    def scrape_internshala(self):
        print("\n[Internshala]")
        base = "https://internshala.com"
        paths = ["jobs/product-manager-jobs", "jobs/business-analyst-jobs",
                "jobs/software-developer-jobs", "jobs/frontend-developer-jobs",
                "jobs/backend-developer-jobs", "jobs/ui-ux-designer-jobs",
                "jobs/data-analyst-jobs", "jobs/product-intern-jobs"]

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

    # ===================================================================
    # ENHANCED COMPANY SCRAPING WITH AUTO-DETECTION
    # ===================================================================

    def detect_ats_system(self, url):
        """Smart ATS detection - returns (ats_type, slug, final_url)"""
        headers = {**HEADERS, "Accept": "text/html,application/xhtml+xml"}
        
        try:
            r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            final_url = r.url
            content_lower = r.text.lower()
            
            # Direct URL matches
            url_checks = [
                (r'boards?\.greenhouse\.io/(?:embed/job_board\?for=)?([^/?&]+)', "greenhouse"),
                (r'jobs?\.lever\.co/([^/?&]+)', "lever"),
                (r'(?:jobs\.)?ashbyhq\.com/([^/?&]+)', "ashby"),
                (r'myworkdayjobs\.com/([^/?&]+)', "workday"),
            ]
            
            for pattern, ats_name in url_checks:
                match = re.search(pattern, final_url, re.I)
                if match:
                    return (ats_name, match.group(1), final_url)
            
            # Content-based detection (embedded ATS)
            content_checks = [
                (r'boards?\.greenhouse\.io/(?:embed/job_board\?for=)?([^"\'&<>]+)', "greenhouse"),
                (r'jobs?\.lever\.co/([^"\'&/<>]+)', "lever"),
                (r'jobs\.ashbyhq\.com/([^"\'&/<>]+)', "ashby"),
            ]
            
            for pattern, ats_name in content_checks:
                match = re.search(pattern, r.text[:15000])
                if match:
                    slug = match.group(1).strip()
                    # Clean slug
                    slug = re.sub(r'["\'\s].*$', '', slug)
                    return (ats_name, slug, final_url)
            
            # Link-based detection
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.find_all('a', href=True, limit=100):
                href = link.get('href', '')
                for pattern, ats_name in url_checks[:3]:  # Skip workday
                    match = re.search(pattern, href, re.I)
                    if match:
                        return (ats_name, match.group(1), final_url)
            
            return ("generic", None, final_url)
            
        except Exception as e:
            print(f"  ⚠ Detection error: {e}")
            return ("generic", None, url)

    def scrape_greenhouse_api(self, company_name, slug):
        """Try Greenhouse API endpoint"""
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
        headers = {**HEADERS, "Accept": "application/json"}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                jobs = data.get("jobs", [])
                
                print(f"  ✓ Greenhouse API: {len(jobs)} jobs")
                
                for j in jobs:
                    self.add({
                        "id": f"gh_{slug}_{j.get('id')}",
                        "title": j.get("title", ""),
                        "company": company_name,
                        "location": j.get("location", {}).get("name", "Various"),
                        "source": f"{company_name} (Greenhouse)",
                        "applyLink": j.get("absolute_url", ""),
                        "postedDate": self.now(),
                    })
                return True
            return False
        except:
            return False

    def scrape_greenhouse(self, company_name, slug):
        """Enhanced Greenhouse scraper with API + HTML fallback"""
        
        # Try API first
        if self.scrape_greenhouse_api(company_name, slug):
            return
        
        # Fallback to HTML scraping
        url = f"https://boards.greenhouse.io/embed/job_board?for={slug}"
        headers = {**HEADERS, "Accept": "text/html"}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                # Try without embed
                url = f"https://boards.greenhouse.io/{slug}"
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    print(f"  ⚠ HTTP {r.status_code}")
                    return
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Find ALL links that contain /jobs/ followed by numbers
            valid_jobs = []
            seen_ids = set()
            
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                
                # Look for job ID pattern
                job_match = re.search(r'/jobs/(\d+)', href)
                if not job_match:
                    continue
                
                job_id = job_match.group(1)
                if job_id in seen_ids:
                    continue
                
                # Get title
                title = a.get_text(strip=True)
                
                # Skip if no meaningful title
                if not title or len(title) < 3:
                    # Try to find title in parent
                    parent = a.find_parent("div")
                    if parent:
                        title_elem = parent.find("h3") or parent.find("h4") or parent.find("span")
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                
                if not title or len(title) < 3:
                    continue
                
                # Skip navigation links
                skip_words = ["view all", "see all", "back to", "return to"]
                if any(w in title.lower() for w in skip_words):
                    continue
                
                seen_ids.add(job_id)
                
                # Try to get location
                location = "Various"
                parent = a.find_parent("div", class_="opening")
                if not parent:
                    parent = a.find_parent("div")
                
                if parent:
                    loc_elem = parent.find("span", class_="location") or parent.find(text=re.compile(r'\b(Remote|Hybrid|Onsite|India|USA|UK)\b'))
                    if loc_elem:
                        location = loc_elem.strip() if isinstance(loc_elem, str) else loc_elem.get_text(strip=True)
                
                # Build full URL
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = f"https://boards.greenhouse.io{href}"
                else:
                    full_url = f"https://boards.greenhouse.io/{slug}/{href}"
                
                valid_jobs.append((job_id, title, location, full_url))
            
            print(f"  ✓ Greenhouse HTML: {len(valid_jobs)} jobs")
            
            for job_id, title, location, full_url in valid_jobs:
                self.add({
                    "id": f"gh_{slug}_{job_id}",
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "source": f"{company_name} (Greenhouse)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Greenhouse HTML: {e}")
    

            
    def scrape_lever(self, company_name, slug):
        """Enhanced Lever scraper with better detection"""
        
        # Try API first
        api_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        headers = {**HEADERS, "Accept": "application/json"}
        
        try:
            r = requests.get(api_url, headers=headers, timeout=10)
            if r.status_code == 200:
                try:
                    jobs = r.json()
                    if isinstance(jobs, list) and len(jobs) > 0:
                        print(f"  ✓ Lever API: {len(jobs)} jobs")
                        for j in jobs:
                            self.add({
                                "id": f"lever_{slug}_{j.get('id', hash(j.get('text', '')))}",
                                "title": j.get("text", ""),
                                "company": company_name,
                                "location": j.get("categories", {}).get("location", "Various"),
                                "source": f"{company_name} (Lever)",
                                "applyLink": j.get("hostedUrl", ""),
                                "postedDate": self.now(),
                            })
                        return
                except:
                    pass
            
            # Fallback to HTML scraping
            html_url = f"https://jobs.lever.co/{slug}"
            r = requests.get(html_url, headers={**HEADERS, "Accept": "text/html"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Multiple strategies for finding jobs
            all_links = []
            
            # Strategy 1: Standard posting links
            all_links.extend(soup.select("a.posting-title"))
            
            # Strategy 2: Any link with lever.co/slug in it
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if f"lever.co/{slug}" in href or "/jobs/" in href:
                    all_links.append(a)
            
            # Strategy 3: Links inside posting containers
            all_links.extend(soup.select("div.posting a"))
            all_links.extend(soup.select("div[class*='posting'] a"))
            all_links.extend(soup.select("a[class*='posting']"))
            
            valid_jobs = []
            seen_hrefs = set()
            
            for a in all_links:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not href or href in seen_hrefs:
                    continue
                
                if not title or len(title) < 3:
                    continue
                
                # Skip navigation
                skip_words = ["all jobs", "view all", "departments", "locations"]
                if any(w in title.lower() for w in skip_words):
                    continue
                
                seen_hrefs.add(href)
                valid_jobs.append((href, title))
            
            print(f"  ✓ Lever HTML: {len(valid_jobs)} jobs")
            
            for href, title in valid_jobs:
                full_url = href if href.startswith("http") else f"https://jobs.lever.co{href}"
                
                self.add({
                    "id": f"lever_{slug}_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Lever)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Lever: {e}")
            
    def scrape_ashby(self, company_name, slug):
        """FIXED Ashby scraper - API endpoint approach"""
        print(f"  Attempting Ashby scrape for: {slug}")
        
        # METHOD 1: Try the actual API endpoint
        api_url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
        headers = {
            **HEADERS,
            "Accept": "application/json",
            "Origin": "https://jobs.ashbyhq.com",
            "Referer": f"https://jobs.ashbyhq.com/{slug}"
        }
        
        try:
            r = requests.get(api_url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                jobs = data.get("jobs", [])
                
                if jobs:
                    print(f"  ✓ Ashby API: {len(jobs)} jobs")
                    for j in jobs:
                        job_id = j.get("id", "")
                        title = j.get("title", "")
                        
                        if not job_id or not title:
                            continue
                        
                        loc = j.get("location", {})
                        location = loc.get("name", "Various") if isinstance(loc, dict) else "Various"
                        
                        self.add({
                            "id": f"ashby_{slug}_{job_id}",
                            "title": title,
                            "company": company_name,
                            "location": location,
                            "source": f"{company_name} (Ashby)",
                            "applyLink": f"https://jobs.ashbyhq.com/{slug}/{job_id}",
                            "postedDate": self.now(),
                        })
                    return
        except Exception as e:
            print(f"  ⚠ Ashby API failed: {e}")
        
        # METHOD 2: Try Playwright for JavaScript-rendered content
        try:
            from playwright.sync_api import sync_playwright
            
            url = f"https://jobs.ashbyhq.com/{slug}"
            
            print("  Trying Playwright...")
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(3000)  # Wait for JS to render
                
                # Get all links after JS renders
                links = page.query_selector_all("a[href]")
                
                valid_jobs = []
                seen_hrefs = set()
                
                for link in links:
                    href = link.get_attribute("href") or ""
                    title = link.inner_text().strip()
                    
                    if not href or href in seen_hrefs:
                        continue
                    
                    # Check if it's a job link
                    if slug in href and len(title) > 3:
                        skip_keywords = ["all positions", "view all", "privacy", "terms", "back to"]
                        if any(skip in title.lower() for skip in skip_keywords):
                            continue
                        
                        seen_hrefs.add(href)
                        valid_jobs.append((href, title))
                
                browser.close()
                
                print(f"  ✓ Ashby Playwright: {len(valid_jobs)} jobs")
                
                for href, title in valid_jobs:
                    full_url = href if href.startswith("http") else f"https://jobs.ashbyhq.com{href}"
                    
                    self.add({
                        "id": f"ashby_{slug}_{hash(href)}",
                        "title": title,
                        "company": company_name,
                        "location": "Various",
                        "source": f"{company_name} (Ashby)",
                        "applyLink": full_url,
                        "postedDate": self.now(),
                    })
                
                if valid_jobs:
                    return
                    
        except ImportError:
            print("  ⚠ Playwright not installed - run: pip install playwright && playwright install chromium")
        except Exception as e:
            print(f"  ⚠ Playwright failed: {e}")
        
        print("  ❌ All Ashby methods failed")

    def scrape_ashby_companies(self):
        """Scrape companies using Ashby ATS"""
        print("\n[Ashby Companies]")
        print(f"Companies: {len(ASHBY_COMPANIES)}")
    
        for c in ASHBY_COMPANIES:
            name = c.get('name', 'Unknown')
            slug = c.get('slug', '')
            
            print(f"\n[{name}] Ashby Slug: {slug}")
            
            if not slug:
                print("  ⚠ Missing slug")
                continue
            
            try:
                self.scrape_ashby(name, slug)
                time.sleep(0.5)
            except Exception as e:
                print(f"  ❌ Error: {e}")

    # ===================================================================
    # MAIN COMPANY SCRAPERS
    # ===================================================================

    def scrape_ats(self):
        """Scrape TOP_COMPANIES with known ATS"""
        print("\n[ATS Jobs - Enhanced Detection]")
        print(f"Companies: {len(TOP_COMPANIES)}")
    
        for c in TOP_COMPANIES:
            name = c.get('name', 'Unknown')
            ats = c.get('ats', '')
            slug = c.get('slug', '')
            
            print(f"\n[{name}] ATS: {ats}, Slug: {slug}")
            
            try:
                if ats == "greenhouse" and slug:
                    self.scrape_greenhouse(name, slug)
                elif ats == "lever" and slug:
                    self.scrape_lever(name, slug)
                elif ats == "ashby" and slug:  # ADD THIS LINE
                    self.scrape_ashby(name, slug)  # ADD THIS LINE
                else:
                    print(f"  ⚠ Unknown ATS or missing slug")
                
                time.sleep(0.5)
            except Exception as e:
                print(f"  ❌ Error: {e}")

    def scrape_career_pages(self):
        """Enhanced career page scraper with full auto-detection"""
        print("\n[Career Pages - Full Auto-Detection]")
        print(f"Companies: {len(CAREER_PAGES)}")
    
        for company in CAREER_PAGES:
            name = company.get('name', 'Unknown')
            url = company.get('url', '')
            
            if not url:
                print(f"\n[{name}] ⚠ No URL")
                continue
            
            print(f"\n[{name}]")
            print(f"  URL: {url}")
            
            try:
                # Auto-detect
                ats_type, slug, final_url = self.detect_ats_system(url)
                print(f"  Detected: {ats_type}" + (f" | Slug: {slug}" if slug else ""))
                
                # Scrape based on detection
                if ats_type == "greenhouse" and slug:
                    self.scrape_greenhouse(name, slug)
                elif ats_type == "lever" and slug:
                    self.scrape_lever(name, slug)
                elif ats_type == "ashby" and slug:
                    self.scrape_ashby(name, slug)
                elif ats_type == "workday":
                    print("  ⚠ Workday requires JS - skipped")
                else:
                    # Generic fallback
                    self.scrape_generic(name, final_url)
                
                time.sleep(0.4)
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")
    # ===================================================================
    # MAIN COMPANY SCRAPERS
    # ===================================================================

     def scrape_generic(self, company_name, url):
        """Comprehensive generic scraper"""
        headers = {**HEADERS, "Accept": "text/html"}
    
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
    
            # 20+ selectors for maximum coverage
            selectors = [
                # Class-based
                "a.job-title", "a.position-title", "a.posting-title", "a.role-title",
                "a[class*='job']", "a[class*='position']", "a[class*='posting']",
                "a[class*='opening']", "a[class*='role']", "a[class*='career']",
                # Href-based
                "a[href*='/jobs/']", "a[href*='/job/']", "a[href*='/careers/'][href*='job']",
                "a[href*='/positions/']", "a[href*='/openings/']", "a[href*='/apply']",
                "a[href*='/role/']", "a[href*='jobId']", "a[href*='position']",
                # Container-based
                "div.job a", "div.position a", "li.job a", "li.posting a",
                "div[class*='job'] a", "div[class*='career'] a"
            ]
    
            all_links = []
            seen = set()
            for sel in selectors:
                for a in soup.select(sel):
                    href = a.get("href", "")
                    if href and href not in seen:
                        seen.add(href)
                        all_links.append(a)
    
            # Filter
            skip_patterns = [r'^/$', r'^/careers/?$', r'^/jobs/?$',
                             r'/departments', r'/locations', r'/teams']
            skip_words = ["all jobs", "view all", "see all", "departments",
                          "locations", "browse", "filter by"]
    
            valid_jobs = []
            for a in all_links:
                href = a.get("href", "")
                title = a.get_text(strip=True)
    
                if not href or not title or len(title) < 3:
                    continue
                if any(re.search(p, href, re.I) for p in skip_patterns):
                    continue
                if any(w in title.lower() for w in skip_words):
                    continue
    
                indicators = [
                    '/job', '/position', '/opening', '/role', '/apply',
                    '/posting', '/career', 'jobId', 'positionId'
                ]
                if not any(ind in href.lower() for ind in indicators):
                    continue
    
                valid_jobs.append((href, title))
    
            print(f"  ✓ Generic: {len(valid_jobs)} jobs")
    
            for href, title in valid_jobs:
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    base = re.sub(r'/(careers|jobs|openings).*$', '', url)
                    full_url = base + href
                else:
                    full_url = url.rstrip("/") + "/" + href
    
                self.add({
                    "id": f"generic_{company_name}_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name}",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
    
        except Exception as e:
            print(f"  ❌ Generic: {e}")

    def debug_page(self, url):
        """Debug helper to see what's on a page"""
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            print(f"\n=== DEBUG: {url} ===")
            print(f"Status: {r.status_code}")
            print(f"Total links: {len(soup.find_all('a'))}")
            
            # Print first 20 links
            for i, a in enumerate(soup.find_all('a', href=True)[:20]):
                print(f"{i+1}. {a.get('href')} | {a.get_text(strip=True)[:50]}")
            
        except Exception as e:
            print(f"Debug error: {e}")

    # ===================================================================
    # RUN & SAVE
    # ===================================================================

    def run(self):
        print(f"\n[MODE] {SCRAPE_MODE}")

        if SCRAPE_MODE == "VOLUME":
            self.scrape_remotive()
            self.scrape_remoteok()
            self.scrape_weworkremotely()
            self.scrape_remoteco()
            self.scrape_wellfound()
            self.scrape_yc()
            self.scrape_internshala()
            
            # Company-specific
            self.scrape_ats()
            self.scrape_career_pages()
            self.scrape_ashby_companies() 
            # Add to your run() method temporarily:
            self.debug_page("https://boards.greenhouse.io/stripe")
            self.debug_page("https://boards.greenhouse.io/stripe")
            self.debug_page("https://jobs.lever.co/figma")
            self.debug_page("https://jobs.ashbyhq.com/zapier")

        
        print("\n[SOURCE SUMMARY]")
        for k, v in sorted(self.stats.items()):
            print(f"  {k}: {v}")

        print(f"\n✓ TOTAL JOBS: {len(self.jobs)}")

    def save(self):
        os.makedirs("data", exist_ok=True)

        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(
                sorted(self.jobs, key=lambda x: x["score"], reverse=True),
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n✓ Saved → data/jobs.json ({len(self.jobs)} jobs)")


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
