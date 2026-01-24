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
    {"name": "ParetoAI", "ats": "ashby", "slug": "pareto-ai"},
    {"name": "Upflow", "ats": "ashby", "slug": "upflow"},        
    {"name": "Articul8", "ats": "ashby", "slug": "articul8"},
    {"name": "Axion", "ats": "ashby", "slug": "axion"}, 
    {"name": "Axelera AI", "ats": "ashby", "slug": "axelera"},
    {"name": "Poshmark", "ats": "ashby", "slug": "poshmark"},
    {"name": "SigNoz", "ats": "ashby", "slug": "SigNoz"},
    {"name": "Plane Software, Inc.", "ats": "ashby", "slug": "plane"},
    {"name": "Kraken", "ats": "ashby", "slug": "kraken.com"},
    {"name": "Deel", "ats": "ashby", "slug": "deel"},                   
    {"name": "ElevenLabs", "ats": "ashby", "slug": "elevenlabs"},        
    {"name": "Aspora", "ats": "ashby", "slug": "Aspora"},               
    {"name": "SearchStax", "ats": "ashby", "slug": "searchstax"},       
    {"name": "Almabase", "ats": "ashby", "slug": "Almabase"},            
    {"name": "Credo.AI", "ats": "ashby", "slug": "credo.ai"},           
    {"name": "Real", "ats": "ashby", "slug": "real"},                   
    {"name": "Zania", "ats": "ashby", "slug": "zania"},                  
    {"name": "Fourier", "ats": "ashby", "slug": "fourier"},
    {"name": "Fermi AI", "ats": "ashby", "slug": "Fermi AI"},                   
    {"name": "Decagon", "ats": "ashby", "slug": "decagon"},                     
    {"name": "Lovable", "ats": "ashby", "slug": "lovable"},                 
    {"name": "Assembled", "ats": "ashby", "slug": "assembledhq"},            
    {"name": "Sierra", "ats": "ashby", "slug": "Sierra"},                      
    {"name": "Turnkey", "ats": "ashby", "slug": "turnkey"},                    
    {"name": "Campfire", "ats": "ashby", "slug": "campfire"},                  
    {"name": "LI.FI", "ats": "ashby", "slug": "li.fi"},                         
    {"name": "Clarity", "ats": "ashby", "slug": "clarity"},                     
    {"name": "Lindy", "ats": "ashby", "slug": "lindy"},
    {"name": "Kit", "ats": "ashby", "slug": "kit"},
    {"name": "ZeroRisk", "ats": "ashby", "slug": "zerorisk"},
    {"name": "Clerk", "ats": "ashby", "slug": "clerk"},
    {"name": "Fin", "ats": "ashby", "slug": "fin"},
    {"name": "Vetcove", "ats": "ashby", "slug": "vetcove"},
    {"name": "RoomPriceGenie", "ats": "ashby", "slug": "roompricegenie"},
    {"name": "Scribd", "ats": "ashby", "slug": "scribd"},
    {"name": "Jellyfish", "ats": "ashby", "slug": "jellyfish"},
    {"name": "Avida", "ats": "ashby", "slug": "avida"},
    {"name": "Weave", "ats": "ashby", "slug": "weave"},
    {"name": "Ordio", "ats": "ashby", "slug": "ordio"},
    {"name": "0x", "ats": "ashby", "slug": "0x"},
    {"name": "Zippy", "ats": "ashby", "slug": "zippymh"},
    {"name": "Realm Alliance", "ats": "ashby", "slug": "realmalliance"},
    {"name": "HighlightTA", "ats": "ashby", "slug": "HighlightTA"},
    {"name": "PostHog", "ats": "ashby", "slug": "posthog"},
    {"name": "Hasura", "ats": "ashby", "slug": "hasura"},
    {"name": "Apollo GraphQL", "ats": "ashby", "slug": "apollo-graphql"},
    {"name": "Resend", "ats": "ashby", "slug": "resend"},
    {"name": "Lago", "ats": "ashby", "slug": "lago"},
    {"name": "Together AI", "ats": "ashby", "slug": "together"},
    {"name": "Harvey", "ats": "ashby", "slug": "harvey"},
    {"name": "Anyscale", "ats": "ashby", "slug": "anyscale"},
    {"name": "Weaviate", "ats": "ashby", "slug": "weaviate"},
    {"name": "Qdrant", "ats": "ashby", "slug": "qdrant"},
    {"name": "Descript", "ats": "ashby", "slug": "descript"},
    {"name": "Whimsical", "ats": "ashby", "slug": "whimsical"},
    {"name": "Gamma", "ats": "ashby", "slug": "gamma"},
    {"name": "Help Scout", "ats": "ashby", "slug": "helpscout"},
    {"name": "Sanity", "ats": "ashby", "slug": "sanity"},

]
# config.py
# -------------------------------------------------
# Curated companies list (Antler / user-provided)
# Scraped via dedicated function, same job pipeline
# -------------------------------------------------

ANTLER_COMPANIES = [
    {
        "name": "Dealroom",
        "careers": ["https://dealroom.co/careers"]
    },
    {
        "name": "PitchBook",
        "careers": ["https://pitchbook.com/careers"]
    },
    {
        "name": "Antler",
        "careers": ["https://antler.co/careers"]
    },
    {
        "name": "Navana AI",
        "careers": ["https://navana.ai/careers"]
    },
    {
        "name": "Navana Tech India Pvt. Ltd.",
        "careers": ["https://navana.ai/careers"]
    },
    {
        "name": "Figr",
        "careers": ["https://join.figr.design"]
    },
    {
        "name": "Pascal AI Labs",
        "careers": ["https://pascalailabs.com/careers"]
    },
    {
        "name": "Plotch AI",
        "careers": ["https://plotch.ai/careers"]
    },
    {
        "name": "Build ChatGPT App",
        "careers": ["https://buildchatgpt.app/careers"]
    },
    {
        "name": "Segwise",
        "careers": ["https://segwise.ai/careers"]
    },
    {
        "name": "Autodraft",
        "careers": ["https://autodraft.in/careers"]
    },
    {
        "name": "MyAlt",
        "careers": ["https://myalt.shop/careers"]
    }
]


