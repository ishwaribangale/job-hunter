# scraper.py
# ----------------------------------
# PJIS – Job Intelligence Scraper
# Phase 1: Completeness (STABLE)
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
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        }
    
        for attempt in range(2):  # retry once
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
    
                return  # success, exit
    
            except requests.exceptions.ReadTimeout:
                print(f"  ⏱ Timeout (attempt {attempt + 1}/2)")
    
            except Exception as e:
                print(f"  ❌ Remote.co failed: {e}")
                return
    
        print("  ⚠ Remote.co skipped after retries")

    def scrape_remotive(self):
        print("\n[Remotive]")
    
        categories = [
            None,
            "software-dev",
            "product",
            "design",
            "marketing",
            "sales",
            "data",
            "customer-support",
            "devops",
            "qa",
            "finance",
        ]
    
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
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        }
    
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
        tags = [
            None,
            "engineer",
            "software-dev",
            "frontend",
            "backend",
            "fullstack",
            "product",
            "design",
            "data",
            "marketing",
            "sales",
            "customer-support",
        ]
    
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)",
            "Accept": "application/json",
        }
    
        for tag in tags:
            if tag is None:
                url = base
                label = "main"
            else:
                url = f"{base}?tag={tag}"
                label = tag
    
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
        categories = [
            "remote-programming-jobs",
            "remote-design-jobs",
            "remote-product-jobs",
            "remote-sales-and-marketing-jobs",
            "remote-customer-support-jobs",
        ]
    
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (compatible; PJIS/1.0)",
            "Accept": "text/html",
        }
    
        MAX_PAGES = 10
        MAX_TIMEOUTS = 2
    
        for cat in categories:
            print(f"\nCategory: {cat}")
    
            page = 1
            timeouts = 0
    
            while page <= MAX_PAGES:
                url = f"{base}/{cat}"
                if page > 1:
                    url += f"?page={page}"
    
                try:
                    r = requests.get(url, headers=headers, timeout=6)
    
                    if r.status_code != 200:
                        print(f"  ⚠ Page {page}: HTTP {r.status_code}")
                        break
    
                    if "<rss" in r.text.lower():
                        print("  ⚠ RSS or bot response detected, stopping category")
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
                        print("  ⚠ Too many timeouts, stopping category")
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
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
    
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
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
        paths = [
            "jobs/product-manager-jobs",
            "jobs/business-analyst-jobs",
            "jobs/software-developer-jobs",
            "jobs/frontend-developer-jobs",
            "jobs/backend-developer-jobs",
            "jobs/ui-ux-designer-jobs",
            "jobs/data-analyst-jobs",
            "jobs/product-intern-jobs",
        ]

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
    # ENHANCED ATS & CAREER PAGE SCRAPERS
    # ===================================================================

    def scrape_ats(self):
        """Enhanced ATS scraper with better validation"""
        print("\n[ATS Jobs - Enhanced]")
        print("Companies configured:", len(TOP_COMPANIES))
    
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "application/json,text/html",
        }
    
        for c in TOP_COMPANIES:
            ats_name = c.get('ats', 'unknown')
            company_name = c.get('name', 'unknown')
            print(f"\n[{company_name}] ATS: {ats_name}")
    
            try:
                if c["ats"] == "lever":
                    self._scrape_lever_enhanced(c, headers)
                elif c["ats"] == "greenhouse":
                    self._scrape_greenhouse_enhanced(c, headers)
                    
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ❌ {company_name} error: {e}")

    def _scrape_lever_enhanced(self, company, headers):
        """Enhanced Lever scraper with validation"""
        company_slug = company.get('slug', '')
        api_url = f"https://jobs.lever.co/{company_slug}?mode=json"
        
        try:
            r = requests.get(api_url, headers=headers, timeout=10)
            
            if r.status_code == 200 and r.text.strip().startswith("["):
                jobs = r.json()
                print(f"  ✓ Lever API: {len(jobs)} jobs")
                
                for j in jobs:
                    job_id = j.get('id', '')
                    job_text = j.get('text', '')
                    job_url = j.get('hostedUrl', '')
                    job_categories = j.get('categories', {})
                    job_location = job_categories.get('location', 'Various')
                    company_name = company.get('name', 'Unknown')
                    
                    self.add({
                        "id": f"lever_{job_id}",
                        "title": job_text,
                        "company": company_name,
                        "location": job_location,
                        "source": f"{company_name} (Lever)",
                        "applyLink": job_url,
                        "postedDate": self.now(),
                    })
                return
            
            print("  ⚠ Lever API blocked, trying HTML...")
            html_url = f"https://jobs.lever.co/{company_slug}"
            r = requests.get(html_url, headers=headers, timeout=10)
            
            soup = BeautifulSoup(r.text, "html.parser")
            jobs = soup.select("a.posting-title")
            
            print(f"  ✓ Lever HTML: {len(jobs)} jobs")
            
            company_name = company.get('name', 'Unknown')
            for a in jobs:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not href or not title:
                    continue
                    
                self.add({
                    "id": f"lever_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Lever)",
                    "applyLink": href,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Lever failed: {e}")

    def _scrape_greenhouse_enhanced(self, company, headers):
        """Enhanced Greenhouse scraper with validation"""
        company_slug = company.get('slug', '')
        url = f"https://boards.greenhouse.io/{company_slug}"
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code != 200:
                print(f"  ⚠ HTTP {r.status_code}")
                return
                
            soup = BeautifulSoup(r.text, "html.parser")
            
            jobs = (
                soup.select("div.opening a") or 
                soup.select("a[href*='/jobs/']") or
                soup.select("div.job a")
            )
            
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
            
            print(f"  ✓ Greenhouse: {len(valid_jobs)} valid jobs")
            
            company_name = company.get('name', 'Unknown')
            for href, title, elem in valid_jobs:
                location = "Various"
                parent = elem.find_parent("div", class_="opening")
                if parent:
                    loc_elem = parent.select_one("span.location")
                    if loc_elem:
                        location = loc_elem.get_text(strip=True)
                
                full_url = href if href.startswith("http") else "https://boards.greenhouse.io" + href
                
                # Extract job ID outside f-string
                job_id_match = re.search(job_id_pattern, href)
                job_id = job_id_match.group(1) if job_id_match else str(hash(href))
                
                self.add({
                    "id": f"gh_{job_id}",
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "source": f"{company_name} (Greenhouse)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Greenhouse failed: {e}")

    def scrape_career_pages(self):
        """Enhanced career page scraper with auto-detection"""
        print("\n[Career Pages - Enhanced]")
        print("Companies configured:", len(CAREER_PAGES))
    
        headers = {
            **HEADERS,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "text/html",
        }
    
        for company in CAREER_PAGES:
            company_name = company.get('name', 'Unknown')
            print(f"\n[{company_name}]")
            
            try:
                ats_type = self._detect_ats_from_url(company["url"])
                
                if ats_type == "greenhouse":
                    self._scrape_career_greenhouse(company, headers)
                elif ats_type == "lever":
                    self._scrape_career_lever(company, headers)
                elif ats_type == "ashbyhq":
                    self._scrape_career_ashby(company, headers)
                elif ats_type == "workday":
                    print("  ⚠ Workday detected - requires JS rendering")
                else:
                    self._scrape_career_generic(company, headers)
                    
                time.sleep(0.4)
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")

    def _detect_ats_from_url(self, url):
        """Auto-detect ATS system from career page URL"""
        if "greenhouse.io" in url or "boards.greenhouse" in url:
            return "greenhouse"
        elif "lever.co" in url or "jobs.lever" in url:
            return "lever"
        elif "ashbyhq.com" in url or "jobs.ashbyhq" in url:
            return "ashbyhq"
        elif "myworkdayjobs.com" in url or "workday" in url.lower():
            return "workday"
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True)
            final_url = r.url
            
            if "greenhouse.io" in final_url:
                return "greenhouse"
            elif "lever.co" in final_url:
                return "lever"
            elif "ashbyhq.com" in final_url:
                return "ashbyhq"
                
            if "greenhouse" in r.text.lower()[:5000]:
                return "greenhouse"
            elif "lever" in r.text.lower()[:5000]:
                return "lever"
                
        except Exception:
            pass
        
        return "generic"

    def _scrape_career_greenhouse(self, company, headers):
        """Scrape Greenhouse-based career page"""
        slug_pattern = r'greenhouse\.io/([^/]+)'
        company_url = company.get("url", "")
        slug_match = re.search(slug_pattern, company_url)
        if slug_match:
            slug = slug_match.group(1)
        else:
            try:
                r = requests.get(company_url, headers=headers, timeout=5, allow_redirects=True)
                slug_match = re.search(slug_pattern, r.url)
                if slug_match:
                    slug = slug_match.group(1)
                else:
                    print("  ⚠ Could not find Greenhouse slug")
                    return
            except Exception:
                print("  ⚠ Failed to detect Greenhouse slug")
                return
        
        company_name = company.get("name", "Unknown")
        self._scrape_greenhouse_enhanced(
            {"name": company_name, "slug": slug},
            headers
        )

    def _scrape_career_lever(self, company, headers):
        """Scrape Lever-based career page"""
        slug_pattern = r'lever\.co/([^/]+)'
        company_url = company.get("url", "")
        slug_match = re.search(slug_pattern, company_url)
        if slug_match:
            slug = slug_match.group(1)
        else:
            print("  ⚠ Could not find Lever slug")
            return
        
        company_name = company.get("name", "Unknown")
        self._scrape_lever_enhanced(
            {"name": company_name, "slug": slug},
            headers
        )

    def _scrape_career_ashby(self, company, headers):
        """Scrape Ashby-based career page"""
        try:
            company_url = company.get("url", "")
            r = requests.get(company_url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
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
            
            company_name = company.get("name", "Unknown")
            for href, title in valid_jobs:
                full_url = href if href.startswith("http") else company_url.rstrip("/") + href
                
                self.add({
                    "id": f"ashby_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Ashby)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Ashby failed: {e}")

    def _scrape_career_generic(self, company, headers):
        """Generic career page scraper with smart filtering"""
        try:
            company_url = company.get("url", "")
            r = requests.get(company_url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            selectors = [
                "a[href*='/job/']",
                "a[href*='/jobs/'][href*='-']",
                "a[href*='/careers/'][href*='/job']",
                "a.job-title",
                "a.position-title",
                "div.job a",
                "div.position a",
            ]
            
            jobs = []
            for selector in selectors:
                jobs = soup.select(selector)
                if len(jobs) > 5:
                    break
            
            skip_patterns = [
                r'^/careers/?$',
                r'^/jobs/?$',
                r'/departments',
                r'/locations',
                r'/teams',
            ]
            
            skip_keywords = [
                "all jobs", "view all", "departments", 
                "locations", "open positions", "browse",
                "filter by", "search jobs"
            ]
            
            job_path_pattern = r'/(job|position|role|opening)[s]?/[\w-]+'
            
            valid_jobs = []
            for a in jobs:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                
                if not href or not title or len(title) < 5:
                    continue
                
                if any(re.search(pattern, href) for pattern in skip_patterns):
                    continue
                
                if any(word in title.lower() for word in skip_keywords):
                    continue
                
                if not re.search(job_path_pattern, href, re.I):
                    continue
                
                valid_jobs.append((href, title))
            
            print(f"  ✓ Generic: {len(valid_jobs)} jobs")
            
            company_name = company.get("name", "Unknown")
            for href, title in valid_jobs:
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    base = company_url.split("/careers")[0].split("/jobs")[0]
                    full_url = base + href
                else:
                    full_url = company_url.rstrip("/") + "/" + href
                
                self.add({
                    "id": f"career_{company_name}_{hash(href)}",
                    "title": title,
                    "company": company_name,
                    "location": "Various",
                    "source": f"{company_name} (Career)",
                    "applyLink": full_url,
                    "postedDate": self.now(),
                })
                
        except Exception as e:
            print(f"  ❌ Generic scraper failed: {e}")

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

            self.scrape_ats()
            self.scrape_career_pages()

        print("\n[SOURCE SUMMARY]")
        for k, v in self.stats.items():
            print(f"{k}: {v}")

        print("\nTOTAL JOBS:", len(self.jobs))

    def save(self):
        os.makedirs("data", exist_ok=True)

        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(
                sorted(self.jobs, key=lambda x: x["score"], reverse=True),
                f,
                indent=2,
                ensure_ascii=False,
            )

        print("Saved → data/jobs.json")
if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
    scraper.save()
