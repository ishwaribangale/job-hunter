# config.py
# ----------------------------------
# Global Config - CLEANED & OPTIMIZED
# Only companies with reliable, job-level URLs
# ----------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 12

# ===================================================================
# TOP_COMPANIES - Only Greenhouse companies with verified job-level URLs
# ===================================================================
TOP_COMPANIES = [
    # --------------------
    # GREENHOUSE - VERIFIED WORKING (Job-level URLs only)
    # --------------------
    # Indian Companies
    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},
    {"name": "PayPay India", "ats": "greenhouse", "slug": "paypay"},
    {"name": "RevX", "ats": "greenhouse", "slug": "revx"},
    {"name": "Zinnia", "ats": "greenhouse", "slug": "zinnia"},
    {"name": "Netradyne", "ats": "greenhouse", "slug": "netradyne"},
    {"name": "Samsara", "ats": "greenhouse", "slug": "samsara"},
        # Additional verified Indian companies using Greenhouse
    {"name": "Dunzo", "ats": "greenhouse", "slug": "dunzo"},
    {"name": "Razorpay", "ats": "greenhouse", "slug": "razorpaysoftwareprivatelimited"},
    {"name": "Cred", "ats": "greenhouse", "slug": "cred"},
    {"name": "Jupiter", "ats": "greenhouse", "slug": "amica"},  # Jupiter's parent company
    {"name": "Slice", "ats": "greenhouse", "slug": "slice"},
    {"name": "Zeta", "ats": "greenhouse", "slug": "zeta"},
    {"name": "Innovaccer", "ats": "greenhouse", "slug": "innovaccer"},
    {"name": "Whatfix", "ats": "greenhouse", "slug": "whatfix"},
    {"name": "Chargebee", "ats": "greenhouse", "slug": "chargebee"},
    {"name": "Freshworks", "ats": "greenhouse", "slug": "freshworks"},
    {"name": "Zoho", "ats": "greenhouse", "slug": "zoho"},
    
    # Global Tech Companies (Greenhouse API - Clean job URLs)
    {"name": "Anthropic", "ats": "greenhouse", "slug": "anthropic"},
    {"name": "OneTrust", "ats": "greenhouse", "slug": "onetrust"},
    {"name": "Airbnb", "ats": "greenhouse", "slug": "airbnb"},
    {"name": "Dropbox", "ats": "greenhouse", "slug": "dropbox"},
    {"name": "Stripe", "ats": "greenhouse", "slug": "stripe"},
    {"name": "Lyft", "ats": "greenhouse", "slug": "lyft"},
    {"name": "Betterment", "ats": "greenhouse", "slug": "betterment"},
    {"name": "Instacart", "ats": "greenhouse", "slug": "instacart"},
    {"name": "GoDaddy", "ats": "greenhouse", "slug": "godaddy"},
    {"name": "Webflow", "ats": "greenhouse", "slug": "webflow"},
    {"name": "Netlify", "ats": "greenhouse", "slug": "netlify"},
    {"name": "Postman", "ats": "greenhouse", "slug": "postman"},
    {"name": "Mercury", "ats": "greenhouse", "slug": "mercury"},
    
    # Additional Indian Companies (Greenhouse)
    {"name": "Razorpay", "ats": "greenhouse", "slug": "razorpaysoftwareprivatelimited"},
    {"name": "Swiggy", "ats": "greenhouse", "slug": "swiggy"},
    {"name": "Cred", "ats": "greenhouse", "slug": "cred"},
    {"name": "Zepto", "ats": "greenhouse", "slug": "zepto"},
    {"name": "Meesho", "ats": "greenhouse", "slug": "meesho"},
    {"name": "Ola", "ats": "greenhouse", "slug": "olacabs"},
    {"name": "Dream11", "ats": "greenhouse", "slug": "dream11"},
    {"name": "Urban Company", "ats": "greenhouse", "slug": "urbancompany"},
    {"name": "Cars24", "ats": "greenhouse", "slug": "cars24"},
    {"name": "Groww", "ats": "greenhouse", "slug": "groww"},
]

# ===================================================================
# CAREER_PAGES - Only companies with clean auto-detectable ATS
# REMOVED: All problematic companies listed in requirements
# ===================================================================
CAREER_PAGES = [
    # --------------------
    # FIGMA (Greenhouse - works well)
    # --------------------
    {"name": "Figma", "url": "https://www.figma.com/careers"},
    
    # --------------------
    # NOTION (Ashby - works well)
    # --------------------
    {"name": "Notion", "url": "https://www.notion.so/careers"},
    
    # --------------------
    # FINTECH (Clean job URLs)
    # --------------------
    {"name": "Wise", "url": "https://www.wise.jobs"},
    
    # --------------------
    # INDIAN STARTUPS (Internshala-like, clean URLs)
    # --------------------
    {"name": "BYJU'S", "url": "https://byjus.com/careers"},
    {"name": "Nykaa", "url": "https://www.nykaa.com/careers"},
    {"name": "PolicyBazaar", "url": "https://www.policybazaar.com/about-us/careers"},
    
    # --------------------
    # DATA / SECURITY (Only if they have clean URLs)
    # --------------------
    {"name": "Snyk", "url": "https://snyk.io/careers"},
    {"name": "1Password", "url": "https://1password.com/careers"},
    {"name": "Confluent", "url": "https://www.confluent.io/careers"},
]

# ===================================================================
# ASHBY_COMPANIES - Only companies with working Ashby API
# REMOVED: Cursor, Retool, Scale AI (problematic)
# ===================================================================
ASHBY_COMPANIES = [
    {"name": "Zapier", "ats": "ashby", "slug": "zapier"},
    {"name": "Ramp", "ats": "ashby", "slug": "ramp"},
    {"name": "Notion", "ats": "ashby", "slug": "notion"},
    {"name": "Linear", "ats": "ashby", "slug": "linear"},
    {"name": "Supabase", "ats": "ashby", "slug": "supabase"},
    {"name": "Vercel", "ats": "ashby", "slug": "vercel"},
    {"name": "Vanta", "ats": "ashby", "slug": "vanta"},
    {"name": "Watershed", "ats": "ashby", "slug": "watershed"},
]
