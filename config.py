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
    {"name": "Cartesia", "ats": "ashby", "slug": "cartesia"},
    {"name": "Ema", "ats": "ashby", "slug": "ema"},
    {"name": "Granica", "ats": "ashby", "slug": "granica"},
    {"name": "GigaML", "ats": "ashby", "slug": "gigaml"},
    {"name": "Commure", "ats": "ashby", "slug": "commure"},
    {"name": "Mercor", "ats": "ashby", "slug": "mercor"},
    {"name": "JuniperSquare", "ats": "ashby", "slug": "junipersquare"},
    {"name": "AcaiTravel", "ats": "ashby", "slug": "acai"},
    {"name": "AltimateAI", "ats": "ashby", "slug": "altimate"},
    {"name": "ParetoAI", "ats": "ashby", "slug": "pareto-ai"}
    {"name": "Upflow", "ats": "ashby", "slug": "upflow"},        
    {"name": "Articul8", "ats": "ashby", "slug": "articul8"},
    {"name": "Axion", "ats": "ashby", "slug": "axion"}, 
    {"name": "Axelera AI", "ats": "ashby", "slug": "axelera"},
    {"name": "Poshmark", "ats": "ashby", "slug": "poshmark"},
    {"name": "SigNoz", "ats": "ashby", "slug": "SigNoz"},
    {"name": "Plane Software, Inc.", "ats": "ashby", "slug": "plane"},
    {"name": "Kraken", "ats": "ashby", "slug": "kraken.com"},
    {"name": "Deel", "ats": "ashby", "slug": "deel"},                    // jobs.ashbyhq.com/deel :contentReference[oaicite:0]{index=0}
    {"name": "ElevenLabs", "ats": "ashby", "slug": "elevenlabs"},        // Sales Dev India role on Ashby :contentReference[oaicite:1]{index=1}
    {"name": "Aspora", "ats": "ashby", "slug": "Aspora"},                // jobs.ashbyhq.com/Aspora :contentReference[oaicite:2]{index=2}
    {"name": "SearchStax", "ats": "ashby", "slug": "searchstax"},        // jobs.ashbyhq.com/searchstax :contentReference[oaicite:3]{index=3}
    {"name": "Almabase", "ats": "ashby", "slug": "Almabase"},            // Bangalore role on Ashby :contentReference[oaicite:4]{index=4}
    {"name": "Credo.AI", "ats": "ashby", "slug": "credo.ai"},            // India remote roles :contentReference[oaicite:5]{index=5}
    {"name": "Real", "ats": "ashby", "slug": "real"},                    // Lead Designer India role :contentReference[oaicite:6]{index=6}
    {"name": "Zania", "ats": "ashby", "slug": "zania"},                  // Indian software role found :contentReference[oaicite:7]{index=7}
    {"name": "Fourier", "ats": "ashby", "slug": "fourier"},
    {"name": "Fermi AI", "ats": "ashby", "slug": "Fermi AI"},                   // Associate PM role – Bengaluru, India :contentReference[oaicite:1]{index=1}
    {"name": "Decagon", "ats": "ashby", "slug": "decagon"},                     // Product Manager posting :contentReference[oaicite:2]{index=2}
    {"name": "Lovable", "ats": "ashby", "slug": "lovable"},                     // Senior Product Manager role :contentReference[oaicite:3]{index=3}
    {"name": "Assembled", "ats": "ashby", "slug": "assembledhq"},               // Multiple Product Manager listings (Workforce, Platform) :contentReference[oaicite:4]{index=4}
    {"name": "Sierra", "ats": "ashby", "slug": "Sierra"},                       // Product Manager, Agent Platform :contentReference[oaicite:5]{index=5}
    {"name": "Turnkey", "ats": "ashby", "slug": "turnkey"},                     // Product Manager role :contentReference[oaicite:6]{index=6}
    {"name": "Campfire", "ats": "ashby", "slug": "campfire"},                   // PM opening :contentReference[oaicite:7]{index=7}
    {"name": "LI.FI", "ats": "ashby", "slug": "li.fi"},                          // PM – Expansion & SDKs :contentReference[oaicite:8]{index=8}
    {"name": "Clarity", "ats": "ashby", "slug": "clarity"},                     // Product Manager – Voice of the Customer :contentReference[oaicite:9]{index=9}
    {"name": "Lindy", "ats": "ashby", "slug": "lindy"}       
]

