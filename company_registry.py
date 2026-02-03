import json
import os
from typing import List, Dict

DEFAULT_COMPANIES_PATH = os.path.join("data", "companies.json")


def load_companies(path: str = DEFAULT_COMPANIES_PATH) -> List[Dict]:
    """Load company registry from a JSON file."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except Exception:
        return []


def normalize_company(company: Dict) -> Dict:
    """Return a minimal, normalized company record."""
    return {
        "name": company.get("name", "Unknown"),
        "career_url": company.get("career_url") or company.get("url", ""),
        "ats": company.get("ats", ""),
        "slug": company.get("slug", ""),
        "country": company.get("country", "GLOBAL"),
    }


def get_companies(path: str = DEFAULT_COMPANIES_PATH) -> List[Dict]:
    companies = load_companies(path)
    return [normalize_company(c) for c in companies if isinstance(c, dict)]


def filter_companies(companies: List[Dict], country: str = "", ats: str = "") -> List[Dict]:
    results = companies
    if country:
        results = [c for c in results if (c.get("country") or "").upper() == country.upper()]
    if ats:
        results = [c for c in results if (c.get("ats") or "").lower() == ats.lower()]
    return results
