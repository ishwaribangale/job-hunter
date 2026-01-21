# diagnostic.py
# ----------------------------------
# Diagnose career pages to find ATS systems
# ----------------------------------

import requests
import re
from bs4 import BeautifulSoup
from config import HEADERS, CAREER_PAGES

def diagnose_company(company_name, url):
    """Deep dive into a company's career page"""
    print(f"\n{'='*70}")
    print(f"🔍 DIAGNOSING: {company_name}")
    print(f"📍 URL: {url}")
    print('='*70)
    
    headers = {
        **HEADERS,
        "Accept": "text/html,application/xhtml+xml",
    }
    
    try:
        # Follow redirects
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        final_url = r.url
        
        print(f"\n✅ Status: {r.status_code}")
        print(f"🔗 Final URL: {final_url}")
        
        # Check for ATS in URL
        ats_in_url = None
        if "greenhouse.io" in final_url or "boards.greenhouse" in final_url:
            ats_in_url = "Greenhouse"
            match = re.search(r'greenhouse\.io/(?:embed/job_board\?for=)?([^/?&]+)', final_url)
            if match:
                print(f"   └─ Greenhouse slug: {match.group(1)}")
        elif "lever.co" in final_url or "jobs.lever" in final_url:
            ats_in_url = "Lever"
            match = re.search(r'lever\.co/([^/?&]+)', final_url)
            if match:
                print(f"   └─ Lever slug: {match.group(1)}")
        elif "ashbyhq.com" in final_url or "jobs.ashbyhq" in final_url:
            ats_in_url = "Ashby"
            match = re.search(r'ashbyhq\.com/([^/?&]+)', final_url)
            if match:
                print(f"   └─ Ashby slug: {match.group(1)}")
        elif "workday" in final_url.lower():
            ats_in_url = "Workday (requires JS)"
        
        if ats_in_url:
            print(f"\n🎯 ATS DETECTED IN URL: {ats_in_url}")
        
        # Parse content
        soup = BeautifulSoup(r.text, "html.parser")
        content_lower = r.text.lower()
        
        # Check for ATS in content
        print("\n📄 CONTENT ANALYSIS:")
        
        if "greenhouse" in content_lower[:10000]:
            print("  ✓ Contains 'greenhouse' text")
            # Find greenhouse URLs
            gh_matches = re.findall(r'greenhouse\.io/(?:embed/job_board\?for=)?([^"\'&\s]+)', r.text)
            if gh_matches:
                print(f"    └─ Greenhouse slug(s): {set(gh_matches)}")
        
        if "lever" in content_lower[:10000]:
            print("  ✓ Contains 'lever' text")
            lever_matches = re.findall(r'lever\.co/([^"\'&\s/]+)', r.text)
            if lever_matches:
                print(f"    └─ Lever slug(s): {set(lever_matches)}")
        
        if "ashbyhq" in content_lower[:10000]:
            print("  ✓ Contains 'ashbyhq' text")
            ashby_matches = re.findall(r'ashbyhq\.com/([^"\'&\s/]+)', r.text)
            if ashby_matches:
                print(f"    └─ Ashby slug(s): {set(ashby_matches)}")
        
        # Find job-related links
        print("\n🔗 JOB LINKS FOUND:")
        job_links = soup.find_all('a', href=True)
        
        job_patterns = {
            'greenhouse': [],
            'lever': [],
            'ashby': [],
            'generic': []
        }
        
        for link in job_links[:100]:  # Check first 100 links
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if 'greenhouse.io' in href:
                job_patterns['greenhouse'].append((text[:50], href[:100]))
            elif 'lever.co' in href:
                job_patterns['lever'].append((text[:50], href[:100]))
            elif 'ashbyhq.com' in href:
                job_patterns['ashby'].append((text[:50], href[:100]))
            elif any(keyword in href.lower() for keyword in ['/job/', '/position/', '/opening/', '/role/']):
                if text and len(text) > 5:  # Likely a job title
                    job_patterns['generic'].append((text[:50], href[:100]))
        
        for ats, links in job_patterns.items():
            if links:
                print(f"\n  📋 {ats.upper()} ({len(links)} links):")
                for text, href in links[:3]:  # Show first 3
                    print(f"    • {text}")
                    print(f"      {href}")
        
        # Find common selectors
        print("\n🎨 HTML STRUCTURE:")
        
        common_job_containers = [
            ("div.opening", "Greenhouse openings"),
            ("a.posting-title", "Lever postings"),
            ("div.job", "Generic job div"),
            ("a[href*='/jobs/']", "Job links"),
            ("li[class*='job']", "Job list items"),
        ]
        
        for selector, description in common_job_containers:
            found = soup.select(selector)
            if found:
                print(f"  ✓ Found {len(found)}x {description}")
        
        # JavaScript detection
        scripts = soup.find_all('script')
        print(f"\n📜 JAVASCRIPT: {len(scripts)} script tags found")
        
        for script in scripts[:10]:
            src = script.get('src', '')
            if any(ats in src for ats in ['greenhouse', 'lever', 'ashby']):
                print(f"  ✓ ATS script: {src[:80]}")
        
        # Final recommendation
        print("\n" + "="*70)
        print("💡 RECOMMENDATION:")
        
        if ats_in_url:
            print(f"  → Use dedicated {ats_in_url} scraper")
        elif job_patterns['greenhouse']:
            print(f"  → Use Greenhouse scraper (embedded)")
        elif job_patterns['lever']:
            print(f"  → Use Lever scraper (embedded)")
        elif job_patterns['ashby']:
            print(f"  → Use Ashby scraper")
        elif job_patterns['generic']:
            print(f"  → Use generic scraper with these patterns:")
            unique_patterns = set(href.split('/')[3:5] for _, href in job_patterns['generic'][:5] if '/' in href)
            for pattern in list(unique_patterns)[:3]:
                print(f"     • /{'/'.join(pattern)}")
        else:
            print(f"  → ⚠️ No obvious job listings found - may require:")
            print(f"     • JavaScript rendering (Playwright/Selenium)")
            print(f"     • Manual inspection of page source")
            print(f"     • API endpoint detection")
        
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    # Test specific companies
    test_companies = [
        ("Notion", "https://www.notion.so/careers"),
        ("OpenAI", "https://openai.com/careers"),
        ("Calendly", "https://careers.calendly.com"),
        ("Zapier", "https://zapier.com/jobs"),
        ("Figma", "https://www.figma.com/careers"),
    ]
    
    for name, url in test_companies:
        diagnose_company(name, url)
        print("\n" + "🔹"*35 + "\n")
    
    # Or diagnose all
    # for company in CAREER_PAGES:
    #     diagnose_company(company['name'], company['url'])
