"""
Job Intelligence Scraper - Free Automated System
Scrapes jobs from multiple sources and saves to GitHub
Runs via GitHub Actions every 2 hours
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import time
from urllib.parse import quote_plus

class JobScraper:
    def __init__(self):
        self.jobs = []
        self.sources = {
            'naukri': True,
            'angellist': True,
            'instahyre': True,
            'career_pages': True,
            'google_jobs': True
        }
        
        # Add your target companies for career page scraping
        self.target_companies = [
            {'name': 'Razorpay', 'careers_url': 'https://razorpay.com/jobs/'},
            {'name': 'CRED', 'careers_url': 'https://careers.cred.club/'},
            {'name': 'Meesho', 'careers_url': 'https://www.meesho.io/careers'},
            {'name': 'PhonePe', 'careers_url': 'https://www.phonepe.com/careers/'},
            {'name': 'Swiggy', 'careers_url': 'https://careers.swiggy.com/'},
            {'name': 'Zomato', 'careers_url': 'https://www.zomato.com/careers'},
            {'name': 'Flipkart', 'careers_url': 'https://www.flipkartcareers.com/'},
            {'name': 'Paytm', 'careers_url': 'https://jobs.lever.co/paytm'},
            {'name': 'Ola', 'careers_url': 'https://www.olacabs.com/careers'},
            {'name': 'Zepto', 'careers_url': 'https://www.zepto.co.in/careers'},
        ]
        
        self.product_keywords = [
            'Product Manager', 'APM', 'Associate Product Manager',
            'Senior Product Manager', 'Product Analyst', 'Business Analyst',
            'Product Operations', 'Product Owner', 'Technical Product Manager'
        ]

    def scrape_naukri(self):
        """Scrape Naukri.com for product management roles"""
        print("🔍 Scraping Naukri...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        keywords = ['product+manager', 'associate+product+manager', 'product+analyst']
        
        for keyword in keywords:
            try:
                url = f'https://www.naukri.com/{keyword}-jobs'
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_cards = soup.find_all('article', class_='jobTuple')[:10]
                    
                    for card in job_cards:
                        try:
                            title_elem = card.find('a', class_='title')
                            company_elem = card.find('a', class_='subTitle')
                            location_elem = card.find('li', class_='location')
                            
                            if title_elem and company_elem:
                                job = {
                                    'id': f"naukri_{int(time.time())}_{len(self.jobs)}",
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip(),
                                    'location': location_elem.text.strip() if location_elem else 'Not specified',
                                    'source': 'Naukri',
                                    'applyLink': 'https://www.naukri.com' + title_elem['href'] if title_elem.get('href') else '#',
                                    'description': card.find('div', class_='job-description').text.strip()[:200] if card.find('div', class_='job-description') else 'Product role opportunity',
                                    'postedDate': datetime.now().isoformat(),
                                    'engagement': {'likes': 0, 'comments': 0, 'isUnseen': False},
                                    'matchScore': 70,
                                    'deadline': None,
                                    'status': None,
                                    'fetchedAt': datetime.now().isoformat(),
                                    'isManual': False
                                }
                                self.jobs.append(job)
                        except Exception as e:
                            print(f"Error parsing Naukri job: {e}")
                            continue
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Error scraping Naukri ({keyword}): {e}")
        
        print(f"✅ Naukri: Found {len([j for j in self.jobs if j['source'] == 'Naukri'])} jobs")

    def scrape_angellist(self):
        """Scrape AngelList (Wellfound) for startup product roles"""
        print("🔍 Scraping AngelList/Wellfound...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            url = 'https://wellfound.com/role/r/product-manager'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='styles_jobListing')[:10]
                
                for card in job_cards:
                    try:
                        title = card.find('h2')
                        company = card.find('div', class_='styles_companyName')
                        
                        if title and company:
                            job = {
                                'id': f"angellist_{int(time.time())}_{len(self.jobs)}",
                                'title': title.text.strip(),
                                'company': company.text.strip(),
                                'location': 'Remote',
                                'source': 'AngelList',
                                'applyLink': f"https://wellfound.com{card.find('a')['href']}" if card.find('a') else '#',
                                'description': 'Product role at a growing startup',
                                'postedDate': datetime.now().isoformat(),
                                'engagement': {'likes': 0, 'comments': 0, 'isUnseen': False},
                                'matchScore': 75,
                                'deadline': None,
                                'status': None,
                                'fetchedAt': datetime.now().isoformat(),
                                'isManual': False
                            }
                            self.jobs.append(job)
                    except Exception as e:
                        print(f"Error parsing AngelList job: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping AngelList: {e}")
        
        print(f"✅ AngelList: Found {len([j for j in self.jobs if j['source'] == 'AngelList'])} jobs")

    def scrape_company_career_pages(self):
        """Scrape career pages of target companies"""
        print("🔍 Scraping Company Career Pages...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for company in self.target_companies:
            try:
                print(f"  Checking {company['name']}...")
                response = requests.get(company['careers_url'], headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text_content = soup.get_text().lower()
                    
                    for keyword in self.product_keywords:
                        if keyword.lower() in text_content:
                            job = {
                                'id': f"career_{company['name']}_{int(time.time())}",
                                'title': keyword,
                                'company': company['name'],
                                'location': 'Check career page',
                                'source': 'Company Career Page',
                                'applyLink': company['careers_url'],
                                'description': f'{keyword} role at {company["name"]}. Visit career page for details.',
                                'postedDate': datetime.now().isoformat(),
                                'engagement': {'likes': 0, 'comments': 0, 'isUnseen': True},
                                'matchScore': 72,
                                'deadline': None,
                                'status': None,
                                'fetchedAt': datetime.now().isoformat(),
                                'isManual': False
                            }
                            self.jobs.append(job)
                            break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping {company['name']}: {e}")
        
        print(f"✅ Career Pages: Found {len([j for j in self.jobs if j['source'] == 'Company Career Page'])} jobs")

    def scrape_google_jobs(self):
        """Scrape Google Jobs using simple search"""
        print("🔍 Scraping Google Jobs...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        keywords = ['product manager remote india', 'associate product manager bangalore']
        
        for keyword in keywords:
            try:
                url = f'https://www.google.com/search?q={quote_plus(keyword)}&ibp=htl;jobs'
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_cards = soup.find_all('div', class_='PwjeAc')[:5]
                    
                    for card in job_cards:
                        try:
                            title = card.find('div', class_='BjJfJf')
                            company = card.find('div', class_='vNEEBe')
                            
                            if title:
                                job = {
                                    'id': f"google_{int(time.time())}_{len(self.jobs)}",
                                    'title': title.text.strip() if title else 'Product Manager',
                                    'company': company.text.strip() if company else 'Various',
                                    'location': 'India',
                                    'source': 'Google Jobs',
                                    'applyLink': url,
                                    'description': 'Product management opportunity',
                                    'postedDate': datetime.now().isoformat(),
                                    'engagement': {'likes': 0, 'comments': 0, 'isUnseen': False},
                                    'matchScore': 68,
                                    'deadline': None,
                                    'status': None,
                                    'fetchedAt': datetime.now().isoformat(),
                                    'isManual': False
                                }
                                self.jobs.append(job)
                        except:
                            continue
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Error scraping Google Jobs: {e}")
        
        print(f"✅ Google Jobs: Found {len([j for j in self.jobs if j['source'] == 'Google Jobs'])} jobs")

    def calculate_match_score(self, job, user_profile):
        """Calculate match score based on user profile"""
        if not user_profile:
            return 70
        
        score = 60
        
        target_roles = user_profile.get('targetRoles', [])
        if any(role.lower() in job['title'].lower() for role in target_roles):
            score += 15
        
        preferred_locations = user_profile.get('location', [])
        if any(loc.lower() in job['location'].lower() for loc in preferred_locations):
            score += 10
        
        skills = user_profile.get('skills', [])
        desc_lower = job['description'].lower()
        skill_matches = sum(1 for skill in skills if skill.lower() in desc_lower)
        score += min(skill_matches * 2, 15)
        
        return min(score, 98)

    def remove_duplicates(self):
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in self.jobs:
            key = f"{job['title'].lower()}_{job['company'].lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        removed = len(self.jobs) - len(unique_jobs)
        self.jobs = unique_jobs
        if removed > 0:
            print(f"🔄 Removed {removed} duplicates")

    def run_full_scrape(self, user_profile=None):
        """Run complete scraping process"""
        print("🚀 Starting job scraping...")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.sources.get('naukri'):
            self.scrape_naukri()
        
        if self.sources.get('angellist'):
            self.scrape_angellist()
        
        if self.sources.get('career_pages'):
            self.scrape_company_career_pages()
        
        if self.sources.get('google_jobs'):
            self.scrape_google_jobs()
        
        self.remove_duplicates()
        
        if user_profile:
            for job in self.jobs:
                job['matchScore'] = self.calculate_match_score(job, user_profile)
        
        print(f"\n✅ Scraping complete! Found {len(self.jobs)} unique jobs")
        
        return self.jobs

    def save_to_json(self, filename='jobs_data.json'):
        """Save jobs to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {filename}")

    def save_to_github(self, token, repo, filepath='data/jobs.json'):
        """Save jobs to GitHub repository"""
        import base64
        
        url = f"https://api.github.com/repos/{repo}/contents/{filepath}"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        content = json.dumps(self.jobs, indent=2)
        content_b64 = base64.b64encode(content.encode()).decode()
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json()['sha']
            else:
                sha = None
        except:
            sha = None
        
        data = {
            'message': f'Update jobs - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'content': content_b64,
        }
        
        if sha:
            data['sha'] = sha
        
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print(f"✅ Saved to GitHub: {repo}/{filepath}")
        else:
            print(f"❌ GitHub save failed: {response.status_code}")

if __name__ == '__main__':
    scraper = JobScraper()
    
    user_profile = {
        'targetRoles': ['Product Manager', 'Associate Product Manager', 'Product Analyst'],
        'skills': ['SQL', 'Python', 'A/B Testing', 'Product Strategy', 'Data Analysis'],
        'location': ['Remote', 'Bangalore', 'Mumbai'],
        'experience': '3-5 years'
    }
    
    jobs = scraper.run_full_scrape(user_profile)
    
    scraper.save_to_json('jobs_data.json')
    
    print("\n📊 Summary:")
    print(f"Total jobs: {len(jobs)}")
    print(f"High match (85%+): {len([j for j in jobs if j['matchScore'] >= 85])}")
    print(f"Good match (75-84%): {len([j for j in jobs if 75 <= j['matchScore'] < 85])}")
    print(f"Unseen jobs: {len([j for j in jobs if j['engagement']['isUnseen']])}")
