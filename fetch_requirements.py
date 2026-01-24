# fetch_requirements.py
# Run this AFTER scraping to enrich jobs with requirements

import json
from requirements_extractor import RequirementsExtractor
import time

def enrich_jobs_with_requirements(input_file="data/jobs.json", 
                                   output_file="data/jobs_enriched.json",
                                   max_jobs=100):
    """Fetch requirements for jobs that don't have them"""
    
    with open(input_file, 'r') as f:
        jobs = json.load(f)
    
    extractor = RequirementsExtractor()
    enriched_count = 0
    
    for i, job in enumerate(jobs):
        # Skip if already has requirements
        if job.get('requirements'):
            continue
        
        # Stop after max_jobs to save time
        if enriched_count >= max_jobs:
            break
        
        print(f"[{i+1}/{len(jobs)}] Fetching: {job['title'][:50]}...")
        
        try:
            job['requirements'] = extractor.extract_from_url(job['applyLink'])
            enriched_count += 1
            time.sleep(0.5)  # Be nice to servers
        except Exception as e:
            print(f"  Error: {e}")
            job['requirements'] = extractor._empty_requirements()
    
    # Save enriched jobs
    with open(output_file, 'w') as f:
        json.dump(jobs, f, indent=2)
    
    print(f"\n✓ Enriched {enriched_count} jobs → {output_file}")

if __name__ == "__main__":
    # Enrich top 100 jobs only (to save time)
    enrich_jobs_with_requirements(max_jobs=100)
