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
# TOP_COMPANIES - Only Greenhouse companies with VERIFIED working slugs
# All 404 companies removed, no duplicates
# ===================================================================
TOP_COMPANIES = [
    # --------------------
    # GREENHOUSE - INDIAN COMPANIES (Working)
    # --------------------
    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},
    {"name": "PayPay India", "ats": "greenhouse", "slug": "paypay"},
    {"name": "RevX", "ats": "greenhouse", "slug": "revx"},
    {"name": "Zinnia", "ats": "greenhouse", "slug": "zinnia"},
    {"name": "Netradyne", "ats": "greenhouse", "slug": "netradyne"},
    {"name": "Samsara", "ats": "greenhouse", "slug": "samsara"},
    {"name": "Razorpay", "ats": "greenhouse", "slug": "razorpaysoftwareprivatelimited"},
    {"name": "Slice", "ats": "greenhouse", "slug": "slice"},
    {"name": "Groww", "ats": "greenhouse", "slug": "groww"},

    # --------------------
    # GREENHOUSE - GLOBAL TECH COMPANIES (Working)
    # --------------------
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
]

CAREER_PAGES = []
ASHBY_COMPANIES = []


COMPANIES = [
    {"name":"Pixlogix Infotech", "ats":"unknown", "source":"Indeed/LinkedIn"},
    {"name":"CloudOne Digital", "ats":"unknown"},
    {"name":"Freemius", "ats":"unknown"},
    {"name":"Awesome Motive", "ats":"unknown"},
    {"name":"Liquid Web", "ats":"unknown"},
    {"name":"Wipro", "ats":"unknown"},
    {"name":"Accenture", "ats":"unknown"},
    {"name":"Groww", "ats":"unknown"},
]
# ===================================================================
# CAREER_PAGES - Only working companies with auto-detectable ATS
# Removed: BYJU'S (6 jobs), Nykaa (errors), PolicyBazaar (timeout), 
#          Snyk (1 job), Confluent (0 jobs)
# ===================================================================
CAREER_PAGES = [
    {"name": "Figma", "url": "https://www.figma.com/careers"},
    {"name": "Notion", "url": "https://www.notion.so/careers"},
    {"name": "Linear", "url": "https://linear.app/careers"},
    {"name": "Vercel", "url": "https://vercel.com/careers"},
    {"name": "Render", "url": "https://render.com/careers"},
    {"name": "Supabase", "url": "https://supabase.com/careers"},
    {"name": "1Password", "url": "https://1password.com/careers"},
    {"name": "Wise", "url": "https://www.wise.jobs"},
]

# ===================================================================
# ASHBY_COMPANIES - Only companies with working Ashby API
# Removed: Cursor (in previous list, moved to CAREER_PAGES if needed)
# Note: Vercel returned 0 jobs but keeping for now
# ===================================================================
ASHBY_COMPANIES = [
    {"name": "Zapier", "ats": "ashby", "slug": "zapier"},
    {"name": "Ramp", "ats": "ashby", "slug": "ramp"},
    {"name": "Notion", "ats": "ashby", "slug": "notion"},
    {"name": "Linear", "ats": "ashby", "slug": "linear"},
    {"name": "Supabase", "ats": "ashby", "slug": "supabase"},
    {"name": "Vanta", "ats": "ashby", "slug": "vanta"},
    {"name": "Watershed", "ats": "ashby", "slug": "watershed"},
    {"name": "gigaml", "ats": "ashby", "slug": "gigaml"},
]

# ===================================================================
# REMOVED COMPANIES (404 errors - don't use Greenhouse or wrong slugs)
# ===================================================================
# {"name": "Dunzo", "ats": "greenhouse", "slug": "dunzo"},  # 404
# {"name": "Cred", "ats": "greenhouse", "slug": "cred"},  # 404
# {"name": "Jupiter", "ats": "greenhouse", "slug": "amica"},  # 404
# {"name": "Zeta", "ats": "greenhouse", "slug": "zeta"},  # 404
# {"name": "Innovaccer", "ats": "greenhouse", "slug": "innovaccer"},  # 404
# {"name": "Whatfix", "ats": "greenhouse", "slug": "whatfix"},  # 404
# {"name": "Chargebee", "ats": "greenhouse", "slug": "chargebee"},  # 404
# {"name": "Freshworks", "ats": "greenhouse", "slug": "freshworks"},  # 404
# {"name": "Zoho", "ats": "greenhouse", "slug": "zoho"},  # 404
# {"name": "Swiggy", "ats": "greenhouse", "slug": "swiggy"},  # 404
# {"name": "Zepto", "ats": "greenhouse", "slug": "zepto"},  # 404
# {"name": "Meesho", "ats": "greenhouse", "slug": "meesho"},  # 404
# {"name": "Ola", "ats": "greenhouse", "slug": "olacabs"},  # 404
# {"name": "Dream11", "ats": "greenhouse", "slug": "dream11"},  # 404
# {"name": "Urban Company", "ats": "greenhouse", "slug": "urbancompany"},  # 404
# {"name": "Cars24", "ats": "greenhouse", "slug": "cars24"},  # 404
# {"name": "HubSpot", "ats": "greenhouse", "slug": "hubspot"},  # 0 jobs
# {"name": "Vercel", "ats": "ashby", "slug": "vercel"},  # 0 jobs in Ashby
