# config.py
# ----------------------------------
# Global Config - SAFE & OPTIMIZED
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
# TOP_COMPANIES - Greenhouse/Lever (STABLE, DO NOT TOUCH)
# ===================================================================
TOP_COMPANIES = [
    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},
    {"name": "PayPay India", "ats": "greenhouse", "slug": "paypay"},
    {"name": "RevX", "ats": "greenhouse", "slug": "revx"},
    {"name": "Zinnia", "ats": "greenhouse", "slug": "zinnia"},
    {"name": "Netradyne", "ats": "greenhouse", "slug": "netradyne"},
    {"name": "Samsara", "ats": "greenhouse", "slug": "samsara"},
    {"name": "Razorpay", "ats": "greenhouse", "slug": "razorpaysoftwareprivatelimited"},
    {"name": "Slice", "ats": "greenhouse", "slug": "slice"},
    {"name": "Groww", "ats": "greenhouse", "slug": "groww"},
    {"name": "Pitchbookdata", "ats": "greenhouse", "slug": "pitchbookdata"},
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

# ===================================================================
# CAREER_PAGES - AUTO ATS DETECTION (WORKING ONLY)
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

    {"name": "Anunta Technology", "url": "https://anunta.com/about-us/careers"},
    {"name": "Freshworks", "url": "https://freshworks.com/company/careers"},
    {"name": "Perfios", "url": "https://perfios.com/careers"},
    {"name": "MoEngage", "url": "https://moengage.com/careers"},
    {"name": "WebEngage", "url": "https://webengage.com/careers"},
    {"name": "Kapture CX", "url": "https://kapture.cx/careers"},
    {"name": "SpotDraft", "url": "https://spotdraft.com/careers"},
    {"name": "iMocha", "url": "https://imocha.io/careers"},
    {"name": "Zoho", "url": "https://careers.zohocorp.com/jobs/careers"},
    {"name": "Chargebee", "url": "https://www.chargebee.com/careers/"},
    {"name": "BrowserStack", "url": "https://www.browserstack.com/careers"},
    {"name": "Whatfix", "url": "https://whatfix.com/careers/"},

]

# ===================================================================
# CAREER_PAGES_QUARANTINE (0 JOBS / TIMEOUT HEAVY)
# Not removed – opt-in retries only
# ===================================================================
CAREER_PAGES_QUARANTINE = [
    {"name": "SplashLearn", "url": "https://splashlearn.com/careers"},
    {"name": "Postudio", "url": "https://postud.io"},
    {"name": "BuildNext", "url": "https://careers.buildnext.in"},
    {"name": "Signzy", "url": "https://signzy.com/careers"},
    {"name": "VAMA App", "url": "https://vama.app/careers"},
    {"name": "Topmate", "url": "https://topmate.io/careers"},
]

# ===================================================================
# ASHBY_COMPANIES - VERIFIED WORKING (DO NOT REMOVE)
# ===================================================================
ASHBY_COMPANIES = [
    {"name": "Zapier", "slug": "zapier"},
    {"name": "Ramp", "slug": "ramp"},
    {"name": "Notion", "slug": "notion"},
    {"name": "Linear", "slug": "linear"},
    {"name": "Supabase", "slug": "supabase"},
    {"name": "Vanta", "slug": "vanta"},
    {"name": "Watershed", "slug": "watershed"},
    {"name": "gigaml", "slug": "gigaml"},
    {"name": "Cartesia", "slug": "cartesia"},
    {"name": "Ema", "slug": "ema"},
    {"name": "Granica", "slug": "granica"},
    {"name": "Commure", "slug": "commure"},
    {"name": "Mercor", "slug": "mercor"},
    {"name": "JuniperSquare", "slug": "junipersquare"},
    {"name": "AcaiTravel", "slug": "acai"},
    {"name": "AltimateAI", "slug": "altimate"},
    {"name": "Upflow", "slug": "upflow"},
    {"name": "Articul8", "slug": "articul8"},
    {"name": "Axion", "slug": "axion"},
    {"name": "Axelera AI", "slug": "axelera"},
    {"name": "Poshmark", "slug": "poshmark"},
    {"name": "SigNoz", "slug": "signoz"},
    {"name": "Plane Software, Inc.", "slug": "plane"},
    {"name": "Kraken", "slug": "kraken.com"},
    {"name": "Deel", "slug": "deel"},
    {"name": "ElevenLabs", "slug": "elevenlabs"},
    {"name": "Decagon", "slug": "decagon"},
    {"name": "Lovable", "slug": "lovable"},
    {"name": "Assembled", "slug": "assembledhq"},
    {"name": "Sierra", "slug": "sierra"},
    {"name": "Turnkey", "slug": "turnkey"},
    {"name": "Campfire", "slug": "campfire"},
    {"name": "LI.FI", "slug": "li.fi"},
    {"name": "Clerk", "slug": "clerk"},
    {"name": "Fin", "slug": "fin"},
    {"name": "Jellyfish", "slug": "jellyfish"},
    {"name": "Super.com", "slug": "super.com"},
    {"name": "Protege", "slug": "protege"},
    {"name": "Winona", "slug": "winona"},
    {"name": "Harvey", "slug": "harvey"},
    {"name": "Anyscale", "slug": "anyscale"},
    {"name": "Weaviate", "slug": "weaviate"},
    {"name": "Apollo GraphQL", "slug": "apollo-graphql"},
    {"name": "Resend", "slug": "resend"},
    {"name": "Gamma", "slug": "gamma"},
    {"name": "Help Scout", "slug": "helpscout"},
    {"name": "Sanity", "slug": "sanity"},
    {"name": "Sahara", "slug": "sahara"},
]

# ===================================================================
# ASHBY_QUARANTINE - Known failing / private boards
# (NOT REMOVED, but skipped by default)
# ===================================================================
ASHBY_QUARANTINE = [
    {"name": "Hasura", "slug": "hasura"},
    {"name": "Lago", "slug": "lago"},
    {"name": "Together AI", "slug": "together"},
    {"name": "Qdrant", "slug": "qdrant"},
    {"name": "Descript", "slug": "descript"},
    {"name": "Whimsical", "slug": "whimsical"},
    {"name": "Firstbase", "slug": "firstbase"},
    {"name": "AMPER", "slug": "amperelectric"},
    {"name": "Unbox Robotics", "slug": "unboxrobotics"},
    {"name": "Sui", "slug": "sui"},
    {"name": "Teraflow", "slug": "teraflow"},
    {"name": "marketfeed", "slug": "marketfeed"},
    {"name": "VOIZ", "slug": "voiz"},
    {"name": "PATH", "slug": "path"},
    {"name": "Ivy", "slug": "ivy"},
    {"name": "CRED", "slug": "cred"},
    {"name": "Stealth Startup", "slug": "stealth"},
]
