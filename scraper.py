
# scraper.py
# ----------------------------------
# PJIS – Job Intelligence Scraper
# ENHANCED - Fixed Company Scraping
# ----------------------------------

# scraper.py - CLEAN VERSION
import os
import json
import re
import time
import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT, TOP_COMPANIES, CAREER_PAGES, ASHBY_COMPANIES
from roles import infer_role
from scoring import score_job
from company_registry import get_companies

SCRAPE_MODE = "VOLUME"
EXTRACT_REQUIREMENTS = True  # Reuse existing requirements
REQUIREMENTS_REUSE_ONLY = True  # Do not fetch new requirements for new jobs

# scraper.py
# ----------------------------------
# PJIS – Job Intelligence Scraper
# ENHANCED - With Requirements Extraction
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


# ===================================================================
# REQUIREMENTS EXTRACTOR (inline to avoid import issues)
# ===================================================================

class RequirementsExtractor:
    """Extracts structured requirements from job postings"""
    
    TECH_SKILLS = {
        'languages': ['python', 'javascript', 'java', 'typescript', 'go', 'rust', 
                     'c\\+\\+', 'ruby', 'php', 'swift', 'kotlin', 'scala'],
        'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'spring', 
                      'node\\.?js', 'express', 'fastapi', 'rails', 'laravel'],
        'tools': ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'jenkins', 
                 'git', 'jira', 'figma', 'postgres', 'mongodb', 'redis'],
        'concepts': ['machine learning', 'ml', 'ai', 'devops', 'agile', 'scrum',
                    'microservices', 'rest api', 'graphql', 'ci/cd', 'tdd']
    }
    
    EXP_PATTERNS = [
        r'(\d+)\+?\s*(?:years?|yrs?).*?(?:experience|exp)',
        r'(?:experience|exp).*?(\d+)\+?\s*(?:years?|yrs?)',
        r'minimum\s+(\d+)\s+years?',
        r'at\s+least\s+(\d+)\s+years?'
    ]
    
    def extract_from_url(self, url, timeout=8):
        """Fetch job page and extract requirements"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; JobScraper/1.0)'}
            r = requests.get(url, headers=headers, timeout=timeout)
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()
            return self.extract_from_text(text)
        except Exception as e:
            return self._empty_requirements()
    
    def extract_from_text(self, text):
        """Extract structured requirements from text"""
        if not text:
            return self._empty_requirements()
        
        text_lower = text.lower()
        
        # Extract skills
        skills = self._extract_skills(text_lower)
        
        # Extract experience
        experience = self._extract_experience(text_lower)
        
        # Extract education
        education = self._extract_education(text_lower)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        return {
            'skills': list(skills)[:10],
            'experience_years': experience,
            'education': education,
            'keywords': keywords[:15]
        }
    
    def _extract_skills(self, text):
        """Extract technical skills"""
        found_skills = set()
        for category, skills in self.TECH_SKILLS.items():
            for skill in skills:
                pattern = r'\b' + skill + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    found_skills.add(skill.replace('\\', ''))
        return found_skills
    
    def _extract_experience(self, text):
        """Extract years of experience"""
        for pattern in self.EXP_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    years = int(match.group(1))
                    if 0 <= years <= 20:
                        return years
                except:
                    continue
        return 0
    
    def _extract_education(self, text):
        """Extract education level"""
        education_levels = {
            'phd': ['ph\\.?d', 'doctorate', 'doctoral'],
            'masters': ['master', 'msc', 'mba', 'm\\.s\\.'],
            'bachelors': ['bachelor', 'bsc', 'b\\.s\\.', 'b\\.a\\.', 'undergraduate']
        }
        
        for level, patterns in education_levels.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return level
        return 'not_specified'
    
    def _extract_keywords(self, text):
        """Extract important keywords"""
        keywords = set()
        
        # Extract first 1000 chars
        text_sample = text[:1000]
        
        # Extract capitalized terms
        caps_pattern = r'\b[A-Z][a-zA-Z]{1,19}\b'
        for match in re.finditer(caps_pattern, text_sample):
            word = match.group()
            if len(word) > 2 and word.lower() not in ['the', 'and', 'for', 'with']:
                keywords.add(word)
        
        # Common phrases
        phrases = ['remote', 'hybrid', 'full-time', 'part-time', 'contract',
                  'startup', 'enterprise', 'saas', 'b2b', 'b2c']
        
        text_lower = text_sample.lower()
        for phrase in phrases:
            if phrase in text_lower:
                keywords.add(phrase)
        
        return list(keywords)
    
    def _empty_requirements(self):
        """Return empty requirements"""
        return {
            'skills': [],
            'experience_years': 0,
            'education': 'not_specified',
            'keywords': []
        }


# ===================================================================
# JOB SCRAPER (your existing code continues below)
# ===================================================================
   

class JobScraper:
    def __init__(self):
        self.jobs = []
        self.seen = set()
        self.stats = {}
        self.company_results = {}
        self.req_extractor = RequirementsExtractor()
        self.existing_jobs = {}  # NEW: Store existing jobs by ID
        self.requirements_fetched = 0  # NEW: Counter for tracking
        self.requirements_reused = 0   # NEW: Counter for tracking
        self.requirements_skipped = 0  # NEW: Counter for tracking
        
        # NEW: Load existing jobs at startup
        self._load_existing_jobs()
    
    def _load_existing_jobs(self):
        """Load existing jobs from jobs.json to avoid re-fetching requirements"""
        jobs_file = "data/jobs.json"
        
        if os.path.exists(jobs_file):
            try:
                with open(jobs_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                    
                # Store jobs by ID for quick lookup
                for job in existing:
                    job_id = job.get("id")
                    if job_id and job.get("requirements"):
                        self.existing_jobs[job_id] = job.get("requirements")
                
                print(f"\n✓ Loaded {len(self.existing_jobs)} existing jobs with requirements")
            except Exception as e:
                print(f"\n⚠ Could not load existing jobs: {e}")

    def now(self):
        return datetime.utcnow().isoformat()

    def add(self, job):
        link = job.get("applyLink")
        if not link:
            return
    
        normalized_link = link.rstrip('/').split('?')[0]
        if normalized_link in self.seen:
            return
    
        job["role"] = infer_role(job.get("title"))
        job["score"] = score_job(job)
        job["fetchedAt"] = self.now()
    
        # SMART REQUIREMENTS HANDLING
        if EXTRACT_REQUIREMENTS:
            job_id = job.get("id")
            
            # Check if we already have requirements for this job
            if job_id and job_id in self.existing_jobs:
                # REUSE existing requirements
                job["requirements"] = self.existing_jobs[job_id]
                self.requirements_reused += 1
            else:
                if REQUIREMENTS_REUSE_ONLY:
                    # Skip fetching new requirements for new jobs
                    job["requirements"] = self.req_extractor._empty_requirements()
                    self.requirements_skipped += 1
                else:
                    # FETCH new requirements
                    print(f"  🔍 [{self.requirements_fetched + 1}] Fetching NEW requirements...")
                    print(f"    {job['title'][:60]}...")
                    job["requirements"] = self.fetch_requirements(job)
                    self.requirements_fetched += 1
        else:
            job["requirements"] = self.req_extractor._empty_requirements()
    
        self.seen.add(normalized_link)
        self.jobs.append(job)
        
        src = job.get("source", "unknown")
        self.stats[src] = self.stats.get(src, 0) + 1
        
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
        
        # METHOD 2: Use Playwright with stealth
        try:
            from playwright.sync_api import sync_playwright
            
            print("  Trying Playwright with stealth mode...")
            
            with sync_playwright() as p:
                # Launch with more realistic browser settings
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                    timezone_id="America/New_York"
                )
                
                # Add extra headers to avoid detection
                context.set_extra_http_headers({
                    "Accept-Language": "en-US,en;q=0.9",
                    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"'
                })
                
                page = context.new_page()
                
                # Go to jobs page
                page.goto("https://wellfound.com/jobs", wait_until="domcontentloaded", timeout=30000)
                
                # Scroll to load lazy content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(3000)
                
                # Get page content
                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                # Find all links
                all_links = soup.find_all("a", href=True)
                
                valid_jobs = []
                seen_urls = set()
                
                for link in all_links:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)
                    
                    # Must be a job link
                    if not any(path in href for path in ['/jobs/', '/companies/', '/role/']):
                        continue
                    
                    # Must have title
                    if not title or len(title) < 5 or len(title) > 100:
                        continue
                    
                    # Skip navigation
                    skip_words = ["sign up", "log in", "see all", "view all", "browse", "filter"]
                    if any(w in title.lower() for w in skip_words):
                        continue
                    
                    # Build full URL
                    full_url = href if href.startswith("http") else f"https://wellfound.com{href}"
                    
                    if full_url in seen_urls:
                        continue
                    
                    seen_urls.add(full_url)
                    valid_jobs.append((full_url, title))
                
                browser.close()
                
                if valid_jobs:
                    print(f"  ✓ Wellfound (Playwright): {len(valid_jobs)} jobs")
                    
                    for url, title in valid_jobs:
                        self.add({
                            "id": f"wellfound_{hash(url)}",
                            "title": title,
                            "company": "Startup (Wellfound)",
                            "location": "Remote / Hybrid",
                            "source": "Wellfound",
                            "applyLink": url,
                            "postedDate": self.now(),
                        })
                    return
                
        except ImportError:
            print("  ⚠ Playwright not installed")
        except Exception as e:
            print(f"  ⚠ Playwright failed: {e}")
        
        # METHOD 3: Skip and inform user
        print("  ⚠ Wellfound requires authentication or has strong bot protection")
        print("  💡 Suggestion: Add Wellfound to CAREER_PAGES for auto-detection or skip")

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
                (r'careers\.smartrecruiters\.com/([^/?&]+)', "smartrecruiters"),
                (r'jobs\.smartrecruiters\.com/([^/?&]+)', "smartrecruiters"),
                (r'apply\.workable\.com/([^/?&]+)', "workable"),
                (r'careers\.kula\.ai/([^/?&]+)', "kula"),
                (r'([^.]+)\.darwinbox\.in/.*/careers', "darwinbox"),
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
                (r'careers\.smartrecruiters\.com/([^"\'&/<>]+)', "smartrecruiters"),
                (r'jobs\.smartrecruiters\.com/([^"\'&/<>]+)', "smartrecruiters"),
                (r'apply\.workable\.com/([^"\'&/<>]+)', "workable"),
                (r'careers\.kula\.ai/([^"\'&/<>]+)', "kula"),
                (r'([^.]+)\.darwinbox\.in/.*/careers', "darwinbox"),
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

    def _is_probable_job_url(self, href: str) -> bool:
        if not href:
            return False
        href_lower = href.lower()
        # Exclude root careers pages or listings without a specific job
        if href_lower.rstrip("/").endswith("/careers") or href_lower.rstrip("/").endswith("/jobs"):
            return False
        # Require strong job indicators
        indicators = ["/job/", "/jobs/", "/career/", "/careers/", "/position/", "/positions/", "/opening/", "/openings/"]
        return any(ind in href_lower for ind in indicators)

    def _title_from_url(self, href: str) -> str:
        try:
            path = urlparse(href).path
            if not path:
                return ""
            slug = path.rstrip("/").split("/")[-1]
            slug = unquote(slug).replace("-", " ").replace("_", " ").strip()
            return slug.title() if slug else ""
        except Exception:
            return ""

    def _extract_jobposting_jsonld(self, soup: BeautifulSoup):
        jobs = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
            except Exception:
                continue

            payloads = []
            if isinstance(data, list):
                payloads = data
            elif isinstance(data, dict):
                payloads = [data]

            for item in payloads:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") != "JobPosting":
                    continue
                title = item.get("title", "")
                url = item.get("url", "")
                location = ""
                loc = item.get("jobLocation")
                if isinstance(loc, dict):
                    location = loc.get("address", {}).get("addressLocality", "")
                elif isinstance(loc, list) and loc:
                    loc0 = loc[0]
                    if isinstance(loc0, dict):
                        location = loc0.get("address", {}).get("addressLocality", "")
                if url and title:
                    jobs.append((title, url, location or "Various"))
        return jobs

    def _url_has_jobposting(self, url: str) -> bool:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                return False
            soup = BeautifulSoup(r.text, "html.parser")
            return len(self._extract_jobposting_jsonld(soup)) > 0
        except Exception:
            return False

    def _find_job_urls_in_sitemap(self, base_url: str, limit: int = 50):
        sitemap_urls = []
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            return sitemap_urls

        candidates = [
            f"{parsed.scheme}://{parsed.netloc}/sitemap.xml",
            f"{parsed.scheme}://{parsed.netloc}/sitemap_index.xml",
        ]

        for sitemap_url in candidates:
            try:
                r = requests.get(sitemap_url, headers=HEADERS, timeout=10)
                if r.status_code != 200:
                    continue
                soup = BeautifulSoup(r.text, "xml")
                loc_tags = soup.find_all("loc")
                for loc in loc_tags:
                    href = (loc.get_text() or "").strip()
                    if not href:
                        continue
                    if self._is_probable_job_url(href):
                        sitemap_urls.append(href)
                        if len(sitemap_urls) >= limit:
                            return sitemap_urls
            except Exception:
                continue

        return sitemap_urls

    def scrape_greenhouse_api(self, company_name, slug):
        """Try Greenhouse API endpoint with SMART validation"""
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
        headers = {**HEADERS, "Accept": "application/json"}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                jobs = data.get("jobs", [])
                
                # SMART VALIDATION - Only filter obvious non-jobs
                valid_jobs = []
                for j in jobs:
                    title = j.get("title", "")
                    abs_url = j.get("absolute_url", "")
                    job_id = j.get("id", "")
                    
                    # Must have all required fields
                    if not title or not abs_url or not job_id:
                        continue
                    
                    # Filter ONLY standalone career pages (not real job titles)
                    # These are NEVER real jobs:
                    standalone_pages = [
                        "careers home", "career page", "careers page",
                        "home page", "about us page", "culture page",
                        "benefits page", "university page", "teams page",
                        "how we operate", "code of conduct", "our values"
                    ]
                    
                    title_lower = title.lower().strip()
                    
                    # Skip if title is EXACTLY one of these pages
                    if title_lower in standalone_pages:
                        continue
                    
                    # Skip if title is just "home", "careers", "about" (single word)
                    single_word_excludes = ["home", "careers", "about", "culture", "benefits", "teams", "university"]
                    if title_lower in single_word_excludes:
                        continue
                    
                    # Everything else is likely a real job
                    valid_jobs.append(j)
                
                print(f"  ✓ Greenhouse API: {len(valid_jobs)} jobs (filtered {len(jobs) - len(valid_jobs)} non-jobs)")
                
                for j in valid_jobs:
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
        """Ashby scraper with SMART validation"""
        print(f"  Attempting Ashby scrape for: {slug}")
        
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
                
                # SMART VALIDATION
                valid_jobs = []
                for j in jobs:
                    job_id = j.get("id", "")
                    title = j.get("title", "")
                    
                    if not job_id or not title:
                        continue
                    
                    # Filter ONLY obvious non-jobs
                    title_lower = title.lower().strip()
                    
                    standalone_pages = [
                        "all positions", "view all positions", "careers home",
                        "about us", "privacy policy", "terms of service"
                    ]
                    
                    if title_lower in standalone_pages:
                        continue
                    
                    # Everything else is valid
                    valid_jobs.append(j)
                
                print(f"  ✓ Ashby API: {len(valid_jobs)} jobs (filtered {len(jobs) - len(valid_jobs)} non-jobs)")
                
                for j in valid_jobs:
                    loc = j.get("location", {})
                    location = loc.get("name", "Various") if isinstance(loc, dict) else "Various"
                    
                    self.add({
                        "id": f"ashby_{slug}_{j.get('id')}",
                        "title": j.get("title"),
                        "company": company_name,
                        "location": location,
                        "source": f"{company_name} (Ashby)",
                        "applyLink": f"https://jobs.ashbyhq.com/{slug}/{j.get('id')}",
                        "postedDate": self.now(),
                    })
                return
        except Exception as e:
            print(f"  ⚠ Ashby API failed: {e}")
        
        print("  ❌ Ashby scraping failed")
        
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
    # CUSTOM & ADDITIONAL ATS SCRAPERS
    # ===================================================================

    def scrape_smartrecruiters(self, company_name, slug):
        """SmartRecruiters scraper using public API"""
        api_url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
        headers = {**HEADERS, "Accept": "application/json"}

        try:
            r = requests.get(api_url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ SmartRecruiters HTTP {r.status_code}")
                return

            data = r.json()
            jobs = data.get("content", []) if isinstance(data, dict) else []
            print(f"  ✓ SmartRecruiters: {len(jobs)} jobs")

            for j in jobs:
                job_id = j.get("id")
                title = j.get("name") or j.get("title", "")
                location = j.get("location", {}).get("city", "Various")
                apply_url = j.get("applyUrl") or j.get("ref", "")

                if not job_id or not title:
                    continue

                self.add({
                    "id": f"sr_{slug}_{job_id}",
                    "title": title,
                    "company": company_name,
                    "location": location or "Various",
                    "source": f"{company_name} (SmartRecruiters)",
                    "applyLink": apply_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ SmartRecruiters: {e}")

    def scrape_workable(self, company_name, slug):
        """Workable scraper using public job board JSON"""
        api_url = f"https://apply.workable.com/{slug}/api/v1/jobs"
        headers = {**HEADERS, "Accept": "application/json"}

        try:
            r = requests.get(api_url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ Workable HTTP {r.status_code}")
                return

            data = r.json()
            jobs = data.get("results", []) if isinstance(data, dict) else []
            print(f"  ✓ Workable: {len(jobs)} jobs")

            for j in jobs:
                job_id = j.get("shortcode") or j.get("id")
                title = j.get("title", "")
                location = (j.get("location") or {}).get("city") or j.get("location", "")
                apply_url = j.get("application_url") or j.get("url")

                if not job_id or not title:
                    continue

                self.add({
                    "id": f"workable_{slug}_{job_id}",
                    "title": title,
                    "company": company_name,
                    "location": location or "Various",
                    "source": f"{company_name} (Workable)",
                    "applyLink": apply_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ Workable: {e}")

    def scrape_kula(self, company_name, slug):
        """Kula careers page scraper"""
        url = f"https://careers.kula.ai/{slug}"
        headers = {**HEADERS, "Accept": "text/html"}

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ Kula HTTP {r.status_code}")
                return

            soup = BeautifulSoup(r.text, "html.parser")
            links = []

            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if "kula.ai" in href or href.startswith("/"):
                    if any(x in href for x in ["/job", "/jobs", "/positions"]):
                        links.append(a)
                    # Kula job detail pages often look like /<slug>/<id>
                    if re.search(r"/\\d+/?$", href):
                        links.append(a)

            seen = set()
            valid = []
            for a in links:
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                seen.add(href)

                title = a.get_text(strip=True)
                if not title or len(title) < 3:
                    parent = a.find_parent()
                    if parent:
                        h = parent.find(["h2", "h3", "h4", "span"])
                        if h:
                            title = h.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                full_url = href if href.startswith("http") else f"https://careers.kula.ai{href}"
                valid.append((title, full_url))

            print(f"  ✓ Kula: {len(valid)} jobs")
            for title, full_url in valid:
                self.add({
                    "id": f"kula_{slug}_{hash(full_url)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Kula)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ Kula: {e}")

    def scrape_brainstormforce(self, company_name, url):
        """Brainstorm Force custom scraper"""
        headers = {**HEADERS, "Accept": "text/html"}
        base = "https://brainstormforce.com"

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ Brainstorm Force HTTP {r.status_code}")
                return

            soup = BeautifulSoup(r.text, "html.parser")
            valid = []
            seen = set()

            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if "/join/" not in href:
                    continue
                if "make-your-own-job-profile" in href:
                    continue
                if href.endswith("/join/"):
                    continue

                full_url = href if href.startswith("http") else base + href
                if full_url in seen:
                    continue
                seen.add(full_url)

                title = a.get_text(strip=True)
                if not title or len(title) < 3:
                    parent = a.find_parent()
                    if parent:
                        h = parent.find(["h2", "h3", "h4", "span"])
                        if h:
                            title = h.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                valid.append((title, full_url))

            print(f"  ✓ Brainstorm Force: {len(valid)} jobs")
            for title, full_url in valid:
                self.add({
                    "id": f"brainstormforce_{hash(full_url)}",
                    "title": title,
                    "company": company_name,
                    "location": "Remote",
                    "source": f"{company_name}",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ Brainstorm Force: {e}")

    def scrape_rtcamp(self, company_name, url):
        """rtCamp custom scraper"""
        headers = {**HEADERS, "Accept": "text/html"}

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ rtCamp HTTP {r.status_code}, trying Playwright...")
                try:
                    from playwright.sync_api import sync_playwright
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                        page = browser.new_page()
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(2000)
                        content = page.content()
                        browser.close()
                    soup = BeautifulSoup(content, "html.parser")
                except Exception as e:
                    print(f"  ⚠ rtCamp Playwright failed: {e}")
                    return
            else:
                soup = BeautifulSoup(r.text, "html.parser")

            valid = []
            seen = set()

            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if "/job/" not in href:
                    continue
                full_url = href if href.startswith("http") else f"https://careers.rtcamp.com{href}"
                if full_url in seen:
                    continue
                seen.add(full_url)

                title = a.get_text(strip=True)
                if not title or len(title) < 3:
                    parent = a.find_parent()
                    if parent:
                        h = parent.find(["h2", "h3", "h4", "span"])
                        if h:
                            title = h.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                valid.append((title, full_url))

            print(f"  ✓ rtCamp: {len(valid)} jobs")
            for title, full_url in valid:
                self.add({
                    "id": f"rtcamp_{hash(full_url)}",
                    "title": title,
                    "company": company_name,
                    "location": "Remote",
                    "source": f"{company_name}",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ rtCamp: {e}")

    def scrape_workday(self, company_name, career_url):
        """Workday scraper using public CXS endpoint"""
        try:
            parsed = urlparse(career_url)
            host = parsed.netloc
            path_parts = [p for p in parsed.path.split("/") if p]
            site = path_parts[0] if path_parts else "External"
            tenant = host.split(".")[0]

            api_url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
            headers = {**HEADERS, "Accept": "application/json"}

            offset = 0
            limit = 50
            total = None

            while True:
                params = {"offset": offset, "limit": limit}
                r = requests.get(api_url, headers=headers, params=params, timeout=12)
                if r.status_code != 200:
                    print(f"  ⚠ Workday HTTP {r.status_code}")
                    return

                data = r.json()
                jobs = data.get("jobPostings", []) if isinstance(data, dict) else []
                if total is None:
                    total = data.get("total", len(jobs))

                for j in jobs:
                    title = j.get("title", "")
                    location = j.get("locationsText", "Various")
                    ext_path = j.get("externalPath") or j.get("jobPath") or ""
                    if not title:
                        continue
                    apply_url = f"https://{host}{ext_path}" if ext_path.startswith("/") else career_url

                    job_id = j.get("bulletFields", [{}])[0].get("id") or j.get("id") or hash(apply_url)
                    self.add({
                        "id": f"workday_{tenant}_{job_id}",
                        "title": title,
                        "company": company_name,
                        "location": location or "Various",
                        "source": f"{company_name} (Workday)",
                        "applyLink": apply_url,
                        "postedDate": self.now(),
                    })

                offset += limit
                if total is not None and offset >= total:
                    break
        except Exception as e:
            print(f"  ❌ Workday: {e}")

    def scrape_darwinbox(self, company_name, career_url):
        """Darwinbox scraper using Playwright to extract job links"""
        headers = {**HEADERS, "Accept": "text/html"}

        try:
            r = requests.get(career_url, headers=headers, timeout=10)
            if r.status_code in (401, 403):
                print(f"  ⚠ Darwinbox HTTP {r.status_code} (login required?)")
                return
            if r.status_code != 200:
                print(f"  ⚠ Darwinbox HTTP {r.status_code}")
                return

            if "login" in r.text.lower() and "candidate" in r.text.lower():
                print("  ⚠ Darwinbox login detected, skipping")
                return

            try:
                from playwright.sync_api import sync_playwright
            except Exception:
                print("  ⚠ Playwright not installed")
                return

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                page = browser.new_page()
                page.goto(career_url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)

                links = page.query_selector_all("a[href]")
                valid = []
                seen = set()

                for link in links:
                    href = link.get_attribute("href") or ""
                    title = link.inner_text().strip()
                    if not href:
                        continue

                    if "darwinbox.in" not in href and not href.startswith("/"):
                        continue

                    href_lower = href.lower()
                    if "login" in href_lower or "signin" in href_lower:
                        continue
                    if href_lower.rstrip("/").endswith("/careers"):
                        continue

                    if not any(x in href_lower for x in ["candidate", "career", "job", "opening", "position"]):
                        continue

                    full_url = href if href.startswith("http") else urljoin(career_url, href)
                    if full_url in seen:
                        continue
                    seen.add(full_url)

                    if not title or len(title) < 3:
                        title = self._title_from_url(full_url) or "Job Opening"

                    valid.append((title, full_url))

                browser.close()

            print(f"  ✓ Darwinbox: {len(valid)} jobs")
            for title, full_url in valid:
                self.add({
                    "id": f"darwinbox_{hash(full_url)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Darwinbox)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ Darwinbox: {e}")

    def scrape_wpmudev(self, company_name, url):
        """WPMU DEV custom scraper"""
        headers = {**HEADERS, "Accept": "text/html"}

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ WPMU DEV HTTP {r.status_code}")
                return

            soup = BeautifulSoup(r.text, "html.parser")
            valid = []
            seen = set()

            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if "/careers/" not in href and "/career/" not in href:
                    continue
                if href.rstrip("/").endswith("/careers") or href.rstrip("/").endswith("/career"):
                    continue

                full_url = href if href.startswith("http") else f"https://wpmudev.com{href}"
                if full_url in seen:
                    continue
                seen.add(full_url)

                title = a.get_text(strip=True)
                if not title or len(title) < 3:
                    parent = a.find_parent()
                    if parent:
                        h = parent.find(["h2", "h3", "h4", "span"])
                        if h:
                            title = h.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                valid.append((title, full_url))

            print(f"  ✓ WPMU DEV: {len(valid)} jobs")
            for title, full_url in valid:
                self.add({
                    "id": f"wpmudev_{hash(full_url)}",
                    "title": title,
                    "company": company_name,
                    "location": "Remote",
                    "source": f"{company_name}",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ WPMU DEV: {e}")

    def scrape_navana(self, company_name, url):
        """Navana Tech custom scraper (Notion/Apply links)"""
        headers = {**HEADERS, "Accept": "text/html"}
        allow_hosts = ("notion.so", "notion.site", "forms.gle", "docs.google.com/forms",
                       "tally.so", "typeform.com")

        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"  ⚠ Navana HTTP {r.status_code}")
                return

            soup = BeautifulSoup(r.text, "html.parser")
            valid = []
            seen = set()

            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if not href:
                    continue
                if not any(h in href for h in allow_hosts):
                    continue

                full_url = href
                if full_url in seen:
                    continue
                seen.add(full_url)

                title = a.get_text(strip=True) or "Apply"
                if not title or len(title) < 3:
                    title = "Apply"

                valid.append((title, full_url))

            print(f"  ✓ Navana: {len(valid)} apply links")
            for title, full_url in valid:
                self.add({
                    "id": f"navana_{hash(full_url)}",
                    "title": title,
                    "company": company_name,
                    "location": "Remote",
                    "source": f"{company_name}",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
        except Exception as e:
            print(f"  ❌ Navana: {e}")

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
                elif ats_type == "smartrecruiters" and slug:
                    self.scrape_smartrecruiters(name, slug)
                elif ats_type == "workable" and slug:
                    self.scrape_workable(name, slug)
                elif ats_type == "kula" and slug:
                    self.scrape_kula(name, slug)
                elif ats_type == "workday":
                    print("  ⚠ Workday requires JS - skipped")
                else:
                    # Generic fallback
                    self.scrape_generic(name, final_url)
                
                time.sleep(0.4)
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")
    # ===================================================================
    # COMPANY REGISTRY (CONFIG-DRIVEN)
    # ===================================================================

    def scrape_companies(self, companies):
        """Scrape companies from registry with ATS routing + auto-detection."""
        if not companies:
            return

        print("\n[Company Registry - ATS Routing + Auto-Detection]")
        print(f"Companies: {len(companies)}")

        for company in companies:
            name = company.get("name", "Unknown")
            url = company.get("career_url", "")
            ats = (company.get("ats") or "").lower()
            slug = company.get("slug", "")
            start_count = len(self.jobs)
            error = None

            print(f"\n[{name}]")
            if url:
                print(f"  URL: {url}")

            try:
                if ats == "greenhouse" and slug:
                    self.scrape_greenhouse(name, slug)
                elif ats == "lever" and slug:
                    self.scrape_lever(name, slug)
                elif ats == "ashby" and slug:
                    self.scrape_ashby(name, slug)
                elif ats == "smartrecruiters" and slug:
                    self.scrape_smartrecruiters(name, slug)
                elif ats == "workable" and slug:
                    self.scrape_workable(name, slug)
                elif ats == "kula" and slug:
                    self.scrape_kula(name, slug)
                elif ats == "workday" and url:
                    self.scrape_workday(name, url)
                elif ats == "darwinbox" and url:
                    self.scrape_darwinbox(name, url)
                elif ats == "brainstormforce" and url:
                    self.scrape_brainstormforce(name, url)
                elif ats == "rtcamp" and url:
                    self.scrape_rtcamp(name, url)
                elif ats == "wpmudev" and url:
                    self.scrape_wpmudev(name, url)
                elif ats == "navana" and url:
                    self.scrape_navana(name, url)
                elif ats:
                    print(f"  ⚠ ATS '{ats}' not supported or missing slug; using auto-detect")
                    if url:
                        ats_type, detected_slug, final_url = self.detect_ats_system(url)
                        if ats_type == "greenhouse" and detected_slug:
                            self.scrape_greenhouse(name, detected_slug)
                        elif ats_type == "lever" and detected_slug:
                            self.scrape_lever(name, detected_slug)
                        elif ats_type == "ashby" and detected_slug:
                            self.scrape_ashby(name, detected_slug)
                        elif ats_type == "smartrecruiters" and detected_slug:
                            self.scrape_smartrecruiters(name, detected_slug)
                        elif ats_type == "workable" and detected_slug:
                            self.scrape_workable(name, detected_slug)
                        elif ats_type == "kula" and detected_slug:
                            self.scrape_kula(name, detected_slug)
                        elif ats_type == "darwinbox":
                            self.scrape_darwinbox(name, final_url)
                        elif ats_type == "workday":
                            self.scrape_workday(name, final_url)
                        else:
                            self.scrape_generic(name, final_url)
                    else:
                        print("  ⚠ Missing career_url; skipped")
                else:
                    if url:
                        ats_type, detected_slug, final_url = self.detect_ats_system(url)
                        print(f"  Detected: {ats_type}" + (f" | Slug: {detected_slug}" if detected_slug else ""))
                        if ats_type == "greenhouse" and detected_slug:
                            self.scrape_greenhouse(name, detected_slug)
                        elif ats_type == "lever" and detected_slug:
                            self.scrape_lever(name, detected_slug)
                        elif ats_type == "ashby" and detected_slug:
                            self.scrape_ashby(name, detected_slug)
                        elif ats_type == "smartrecruiters" and detected_slug:
                            self.scrape_smartrecruiters(name, detected_slug)
                        elif ats_type == "workable" and detected_slug:
                            self.scrape_workable(name, detected_slug)
                        elif ats_type == "kula" and detected_slug:
                            self.scrape_kula(name, detected_slug)
                        elif ats_type == "darwinbox":
                            self.scrape_darwinbox(name, final_url)
                        elif ats_type == "workday":
                            self.scrape_workday(name, final_url)
                        else:
                            self.scrape_generic(name, final_url)
                    else:
                        print("  ⚠ Missing career_url; skipped")

                time.sleep(0.4)
            except Exception as e:
                error = str(e)
                print(f"  ❌ Failed: {e}")

            end_count = len(self.jobs)
            found = max(0, end_count - start_count)
            self.company_results[name] = {
                "found": found,
                "error": error,
            }
            print(f"  ✅ Summary: {found} jobs" + (f" | Error: {error}" if error else ""))
    # ===================================================================
    # MAIN COMPANY SCRAPERS
    # ===================================================================

    def scrape_generic(self, company_name, url):
        """Comprehensive generic scraper with Playwright fallback"""
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
                if not self._is_probable_job_url(href):
                    continue

                valid_jobs.append((href, title))
    
            # If found jobs, process them
            if valid_jobs:
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
                return  # Successfully found jobs

            # Try JSON-LD JobPosting
            jsonld_jobs = self._extract_jobposting_jsonld(soup)
            if jsonld_jobs:
                print(f"  ✓ JSON-LD: {len(jsonld_jobs)} jobs")
                for title, full_url, location in jsonld_jobs:
                    self.add({
                        "id": f"jsonld_{company_name}_{hash(full_url)}",
                        "title": title,
                        "company": company_name,
                        "location": location or "Various",
                        "source": f"{company_name}",
                        "applyLink": full_url,
                        "postedDate": self.now(),
                    })
                return

            # Try sitemap lookup
            sitemap_urls = self._find_job_urls_in_sitemap(url)
            if sitemap_urls:
                print(f"  ✓ Sitemap: {len(sitemap_urls)} urls (validating JobPosting...)")
                for href in sitemap_urls:
                    if not self._url_has_jobposting(href):
                        continue
                    title = self._title_from_url(href) or "Job Opening"
                    self.add({
                        "id": f"sitemap_{company_name}_{hash(href)}",
                        "title": title,
                        "company": company_name,
                        "location": "Various",
                        "source": f"{company_name}",
                        "applyLink": href,
                        "postedDate": self.now(),
                    })
                if self.stats.get(company_name, 0) > 0:
                    return
    
            # If no jobs found, try Playwright for JS-rendered content
            print(f"  ⚠ No jobs via requests, trying Playwright...")
            
            try:
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                    page = browser.new_page()
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(2000)
                    
                    # Get all links after JS renders
                    links = page.query_selector_all("a[href]")
                    
                    valid_jobs_pw = []
                    seen_hrefs = set()
                    
                    for link in links:
                        href = link.get_attribute("href") or ""
                        title = link.inner_text().strip()
                        
                        if not href or href in seen_hrefs or len(title) < 3:
                            continue
                        
                        # Must have job indicator (avoid generic careers pages)
                        if not self._is_probable_job_url(href):
                            continue
                        
                        # Skip navigation
                        if any(w in title.lower() for w in skip_words):
                            continue
                        
                        seen_hrefs.add(href)
                        valid_jobs_pw.append((href, title))
                    
                    browser.close()
                    
                    print(f"  ✓ Generic (Playwright): {len(valid_jobs_pw)} urls (validating JobPosting...)")
                    
                    for href, title in valid_jobs_pw:
                        full_url = href if href.startswith("http") else url.rstrip("/") + href
                        if not self._url_has_jobposting(full_url):
                            continue

                        self.add({
                            "id": f"generic_{company_name}_{hash(href)}",
                            "title": title,
                            "company": company_name,
                            "location": "Various",
                            "source": f"{company_name}",
                            "applyLink": full_url,
                            "postedDate": self.now(),
                        })
                    return
                    
            except ImportError:
                print(f"  ⚠ Playwright not installed")
            except Exception as e:
                print(f"  ⚠ Playwright failed: {e}")
            
            # Last resort - at least we tried
            print(f"  ✓ Generic: 0 jobs")
    
        except Exception as e:
            print(f"  ❌ Generic: {e}")

    def fetch_requirements(self, job):
        """Fetch and extract requirements for a job"""
        try:
            link = job.get("applyLink")
            if not link:
                return self.req_extractor._empty_requirements()
            
            print(f"    Fetching requirements for: {job['title'][:50]}...")
            requirements = self.req_extractor.extract_from_url(link)
            time.sleep(0.3)  # Be nice to servers
            return requirements
        except Exception as e:
            print(f"    ⚠ Error: {e}")
            return self.req_extractor._empty_requirements()

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
            self.scrape_yc()
            self.scrape_internshala()

            companies = get_companies()
            if companies:
                self.registry_companies = companies
                self.scrape_companies(companies)
            else:
                self.scrape_ats()
                self.scrape_career_pages()
                self.scrape_ashby_companies()

        print("\n[SOURCE SUMMARY]")
        for k, v in sorted(self.stats.items()):
            print(f"  {k}: {v}")

        print(f"\n✓ TOTAL JOBS: {len(self.jobs)}")
    
        # NEW: Show requirements summary
        if EXTRACT_REQUIREMENTS:
            print(f"\n[REQUIREMENTS SUMMARY]")
            print(f"  ✓ Reused existing: {self.requirements_reused}")
            print(f"  🔍 Fetched new: {self.requirements_fetched}")
            if REQUIREMENTS_REUSE_ONLY:
                print(f"  ⏭ Skipped new: {self.requirements_skipped}")
            print(f"  ⚡ Time saved: ~{self.requirements_reused * 0.5:.1f} seconds")

        # Company summary report (registry only)
        if getattr(self, "registry_companies", None):
            zero_job = [n for n, r in self.company_results.items() if r.get("found", 0) == 0]
            if zero_job:
                print(f"\n[0-JOB COMPANIES]")
                for name in zero_job:
                    print(f"  - {name}")

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
