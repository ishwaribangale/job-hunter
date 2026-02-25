# Company job-source research (initial pass)

This document captures an initial research plan for onboarding the following companies into the platform's scraping pipeline.

## Scope

Companies covered:

1. Ignite Solutions (`ignitesol.com`)
2. Siddha Tech (`siddhatech.com`)
3. rtCamp (`rtcamp.com`)
4. QuadLogix (`quadlogix.com`)
5. Arvan Technologies (`arvan.in`)

## Environment note

From this execution environment, direct HTTP checks against the provided domains failed with proxy `403` tunnel errors, so this pass is a strategy-first onboarding recommendation based on the known source patterns you shared.

## How to ingest each company

### 1) Ignite Solutions (`https://ignitesol.com/`)

**Expected source pattern**
- Careers page on company website.
- Secondary listings on LinkedIn / Glassdoor.

**Recommended ingestion path**
- **Primary**: scrape company career page (preferred source of truth).
- **Fallback**: if no structured ATS is detected, use `generic` site parser and tighten selectors for job cards/links.
- **Do not use aggregator pages as canonical jobs** where possible; they are often stale/duplicated.

**Implementation approach in this codebase**
- Run ATS detection against careers URL first.
- If detected as Greenhouse/Ashby/Lever/Workday/Darwinbox/Kula, add to `data/companies.json` with the specific `ats` and `career_url`.
- If not detected, onboard as `ats: "generic"` and add a small company-specific parser only if generic extraction misses job detail links.

---

### 2) Siddha Tech (`https://www.siddhatech.com/`)

**Expected source pattern**
- Careers section with an Apply form.

**Recommended ingestion path**
- Parse open roles directly from careers page.
- If only a form exists with role labels (no detail pages), ingest role title + location + application URL and mark description fields as partial.

**Implementation approach in this codebase**
- Start with `generic` scraping against the careers URL.
- If role discovery is weak, add a custom company parser similar to existing custom handlers (e.g., `scrape_rtcamp`) to extract form-based postings.

---

### 3) rtCamp (`https://rtcamp.com/`)

**Expected source pattern**
- Dedicated careers portal, plus remote/campus sections.

**Recommended ingestion path**
- Use official careers endpoint/pages as canonical.
- Crawl both primary openings and campus/early-career subpages.
- Ignore third-party boards unless used for enrichment only.

**Implementation approach in this codebase**
- This repository already includes a dedicated `scrape_rtcamp(...)` flow in `scraper.py`, so rtCamp can be maintained as a custom-source company.
- Keep it in the company registry with `ats: "rtcamp"` and the careers URL if not already present.

---

### 4) QuadLogix (`https://www.quadlogix.com/`)

**Expected source pattern**
- Careers page on official site.
- Possible reposts on LinkedIn/Cutshort.

**Recommended ingestion path**
- Pull only from official careers page for primary ingest.
- Treat job-board copies as dedupe candidates and/or monitoring sources.

**Implementation approach in this codebase**
- Attempt ATS detection first.
- If no ATS is found, onboard as `generic` and add post-processing dedupe (by normalized title+company+location hash) when cross-source records are merged.

---

### 5) Arvan Technologies (`https://arvan.in/`)

**Expected source pattern**
- Unclear/missing explicit careers page.
- Jobs primarily discoverable on third-party portals.

**Recommended ingestion path**
- Try to find a first-party careers endpoint (hidden footer link, `/careers`, `/jobs`, or JSON feed) before relying on boards.
- If no first-party source exists:
  - either skip for now (quality-first), or
  - ingest from one approved external board with strict dedupe + freshness checks.

**Implementation approach in this codebase**
- Start with domain ATS detection + generic crawl.
- If first-party jobs are unavailable, create a policy flag for `external_only` companies and route through an explicitly supported board integration (if/when added).

## Recommended onboarding workflow (for all 5)

1. **Source validation**: verify robots/ToS and crawl permission.
2. **ATS auto-detection**: run detector on careers URL.
3. **Choose adapter**:
   - Built-in ATS adapter (best), else
   - Generic parser, else
   - Custom parser.
4. **Company registry entry** in `data/companies.json`.
5. **Quality checks**:
   - Minimum required fields (`title`, `company`, `applyLink`).
   - Freshness window.
   - Duplicate suppression against existing corpus.
6. **Health tracking**: rely on source-health auto-disable for repeatedly empty sources.

## Data quality + compliance recommendations

- Prefer official company careers pages as canonical source.
- Respect `robots.txt` and terms; throttle requests and identify scraper user-agent.
- Avoid scraping authenticated or anti-bot protected pages unless explicitly permitted.
- Do not store unnecessary personal data from application forms.

## Suggested next step

In a follow-up task, we can execute a **live verification pass** and then produce exact `data/companies.json` entries (ATS type + career URL + slug) for each company based on real endpoint detection.
