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

    def scrape_greenhouse(self, company_name, slug):
        """Enhanced Greenhouse scraper with fallback"""
        url = f"https://boards.greenhouse.io/{slug}"
        headers = {**HEADERS, "Accept": "text/html"}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ HTTP {r.status_code}")
                return
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Try multiple selectors
            all_links = (
                soup.select("div.opening a") +
                soup.select("section.level-0 > div a") +
                soup.select("a[href*='/jobs/']") +
                soup.select("div[id*='job'] a")
            )
            
            valid_jobs = []
            job_pattern = r'/jobs/(\d+)'
            skip_words = ["all jobs", "view all", "departments", "locations", "teams"]
            
            for a in all_links:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not href or not title or len(title) < 3:
                    continue
                if not re.search(job_pattern, href):
                    continue
                if any(w in title.lower() for w in skip_words):
                    continue
                
                valid_jobs.append((href, title, a))
            
            print(f"  ✓ Greenhouse: {len(valid_jobs)} jobs")
            
            for href, title, elem in valid_jobs:
                location = "Various"
                parent = elem.find_parent("div", class_="opening")
                if parent:
                    loc = parent.select_one("span.location")
                    if loc:
                        location = loc.get_text(strip=True)
                
                full_url = href if href.startswith("http") else f"https://boards.greenhouse.io{href}"
                job_id = re.search(job_pattern, href).group(1) if re.search(job_pattern, href) else hash(href)
                
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
            print(f"  ❌ Greenhouse: {e}")

    def scrape_lever(self, company_name, slug):
        """Enhanced Lever scraper with API + HTML fallback"""
        api_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        headers = {**HEADERS, "Accept": "application/json"}
        
        try:
            # Try API first
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
            
            # Fallback to HTML
            html_url = f"https://jobs.lever.co/{slug}"
            r = requests.get(html_url, headers={**HEADERS, "Accept": "text/html"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            jobs = (
                soup.select("a.posting-title") +
                soup.select("div.posting a[href*='/jobs/']") +
                soup.select("a[class*='posting']")
            )
            
            valid_jobs = []
            for a in jobs:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                if href and title and len(title) > 3:
                    valid_jobs.append((href, title))
            
            print(f"  ✓ Lever HTML: {len(valid_jobs)} jobs")
            
            for href, title in valid_jobs:
                self.add({
                    "id": f"lever_{slug}_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Lever)",
                    "applyLink": href if href.startswith("http") else f"https://jobs.lever.co{href}",
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Lever: {e}")

    def scrape_ashby_companies(self, company_name, slug):
    """Enhanced Ashby scraper with better detection"""

    url = f"https://jobs.ashbyhq.com/{slug}"
    headers = {**HEADERS, "Accept": "text/html"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"  ⚠ HTTP {r.status_code}")
            return

        soup = BeautifulSoup(r.text, "html.parser")

        # Multiple selection strategies
        all_links = (
            soup.select("a[href*='/jobs/']") +
            soup.select("a[href*='/applications/']") +
            soup.select("a[class*='job']") +
            soup.select("a[class*='posting']") +
            soup.select("div[class*='job'] a") +
            soup.select("div[class*='posting'] a")
        )

        valid_jobs = []
        seen_hrefs = set()

        # More lenient UUID / job-id pattern
        uuid_pattern = r'/([a-f0-9-]{8,}|jobs?/[^/\s]+)'

        for a in all_links:
            href = a.get("href", "")
            title = a.get_text(strip=True)

            # Skip if no href or already seen
            if not href or href in seen_hrefs:
                continue

            # Must look like a job link
            if not re.search(uuid_pattern, href, re.I):
                continue

            # Skip navigation links
            skip_words = ["all jobs", "view all", "see all", "departments", "locations"]
            if any(w in title.lower() for w in skip_words):
                continue

            # Title must be meaningful
            if not title or len(title) < 3:
                continue

            seen_hrefs.add(href)
            valid_jobs.append((href, title))

        print(f"  ✓ Ashby: {len(valid_jobs)} jobs")

        for href, title in valid_jobs:
            full_url = (
                href if href.startswith("http")
                else f"https://jobs.ashbyhq.com{href}"
            )

            self.add({
                "id": f"ashby_{slug}_{hash(href)}",
                "title": title,
                "company": company_name,
                "location": "Various",
                "source": f"{company_name} (Ashby)",
                "applyLink": full_url,
                "postedDate": self.now(),
            })

    except Exception as e:
        print(f"  ❌ Ashby: {e}")

    
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
                
                # Must have job-like indicator
                indicators = ['/job', '/position', '/opening', '/role', '/apply', 
                            '/posting', '/career', 'jobId', 'positionId']
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
                else:
                    print(f"  ⚠ Unknown ATS or missing slug")
                
                time.sleep(0.3)
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
