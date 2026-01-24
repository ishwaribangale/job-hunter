# enrich_jobs.py
# Run this AFTER scraping to add requirements to jobs

import json
from scraper import JobScraper

def enrich_jobs_with_requirements(max_jobs=100):
    """Add requirements to jobs that don't have them"""
    
    # Load existing jobs
    with open('data/jobs.json', 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    print(f"\n[Enriching Jobs with Requirements]")
    print(f"Total jobs: {len(jobs)}")
    print(f"Will enrich top {max_jobs} jobs\n")
    
    scraper = JobScraper()
    enriched_count = 0
    
    for i, job in enumerate(jobs):
        # Skip if already has requirements
        if job.get('requirements'):
            continue
        
        # Stop after max_jobs
        if enriched_count >= max_jobs:
            print(f"\n✓ Reached limit of {max_jobs} jobs")
            break
        
        print(f"[{enriched_count + 1}/{max_jobs}] {job['company']} - {job['title'][:40]}")
        
        # Fetch requirements
        job['requirements'] = scraper.fetch_requirements(job)
        enriched_count += 1
    
    # Save enriched jobs
    with open('data/jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Enriched {enriched_count} jobs!")
    print(f"✅ Saved to data/jobs.json")

if __name__ == "__main__":
    # Enrich top 100 jobs (increase if you want more)
    enrich_jobs_with_requirements(max_jobs=100)
