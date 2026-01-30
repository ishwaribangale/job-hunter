# config.py
# ----------------------------------
# Global Config - EXPANDED WITH NEW COMPANIES
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
# TOP_COMPANIES - Greenhouse/Lever companies with VERIFIED slugs
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
    {"name": "Pitchbookdata", "ats": "greenhouse", "slug": "pitchbookdata"},

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

# ===================================================================
# CAREER_PAGES - Auto-detect ATS from career pages
# This is where most of your NEW companies should go!
# ===================================================================
CAREER_PAGES = [
    # --------------------
    # EXISTING WORKING PAGES
    # --------------------
    {"name": "Figma", "url": "https://www.figma.com/careers"},
    {"name": "Notion", "url": "https://www.notion.so/careers"},
    {"name": "Linear", "url": "https://linear.app/careers"},
    {"name": "Vercel", "url": "https://vercel.com/careers"},
    {"name": "Render", "url": "https://render.com/careers"},
    {"name": "Supabase", "url": "https://supabase.com/careers"},
    {"name": "1Password", "url": "https://1password.com/careers"},
    {"name": "Wise", "url": "https://www.wise.jobs"},

    # --------------------
    # NEW COMPANIES - ENTERPRISE & CORE SAAS
    # --------------------
    {"name": "Anunta Technology", "url": "https://anunta.com/about-us/careers"},
    {"name": "Freshworks", "url": "https://freshworks.com/company/careers"},
    {"name": "Perfios", "url": "https://perfios.com/careers"},
    {"name": "MoEngage", "url": "https://moengage.com/careers"},
    {"name": "WebEngage", "url": "https://webengage.com/careers"},
    {"name": "Kapture CX", "url": "https://kapture.cx/careers"},
    {"name": "SpotDraft", "url": "https://spotdraft.com/careers"},
    {"name": "Signzy", "url": "https://signzy.com/careers"},
    {"name": "iMocha", "url": "https://imocha.io/careers"},

    # --------------------
    # AI & DEVELOPER TOOLS
    # --------------------
    {"name": "Detect Technologies", "url": "https://detecttechnologies.com/current-openings"},
    {"name": "Proctor AI", "url": "https://proctorai.io/careers"},
    {"name": "Scribble Data", "url": "https://scribbledata.io/careers"},
    {"name": "Postudio", "url": "https://postud.io"},

    # --------------------
    # CONSTRUCTION & LOGISTICS SAAS
    # --------------------
    {"name": "BuildNext", "url": "https://careers.buildnext.in"},
    {"name": "Fleetx", "url": "https://fleetx.io/careers"},
    {"name": "CargoFL", "url": "https://cargoflow.ai/careers"},

    # --------------------
    # FINTECH & FINANCE SAAS
    # --------------------
    {"name": "Khatabook", "url": "https://khatabook.com/careers"},
    {"name": "Dhan", "url": "https://recruitcareers.zappyhire.com/en/dhan"},
    {"name": "Swipe", "url": "https://swipe.fyi/careers"},
    {"name": "Spendflo", "url": "https://spendflo.com/careers"},

    # --------------------
    # HR TECH & PRODUCTIVITY
    # --------------------
    {"name": "SquadStack", "url": "https://squadstack.com/careers"},
    {"name": "Smartstaff", "url": "https://smartstaff.co.in/careers"},
    {"name": "Huddleup.ai", "url": "https://huddleup.ai/careers"},

    # --------------------
    # OTHER SPECIALIZED SAAS
    # --------------------
    {"name": "Novatr", "url": "https://novatr.com/career"},
    {"name": "Docsumo", "url": "https://docsumo.com/careers"},
    {"name": "Zuddl", "url": "https://zuddl.com/careers"},
    {"name": "SplashLearn", "url": "https://splashlearn.com/careers"},
    {"name": "VAMA App", "url": "https://vama.app/careers"},
    {"name": "Topmate", "url": "https://topmate.io/careers"},
]

# ===================================================================
# THIRD_PARTY_PLATFORMS - Companies listed on job boards
# These require different scraping (Instahyre, Wellfound, Uplers, etc.)
# ===================================================================
THIRD_PARTY_PLATFORMS = {
    "instahyre": [
        {"name": "Fibr AI", "url": "https://instahyre.com/jobs-at-fibr-ai"},
        {"name": "Pintel.ai", "url": "https://instahyre.com/jobs-at-pintel"},
        {"name": "Powerplay", "url": "https://instahyre.com/jobs-at-powerplay"},
        {"name": "Clickpost", "url": "https://instahyre.com/jobs-at-clickpost"},
        {"name": "Klaar", "url": "https://instahyre.com/jobs-at-klaar"},
        {"name": "Practically", "url": "https://instahyre.com/jobs-at-practically"},
        {"name": "Oditly", "url": "https://instahyre.com/jobs-at-oditly"},
    ],
    "wellfound": [
        {"name": "Drizz", "url": "https://wellfound.com/company/drizz"},
        {"name": "Converj", "url": "https://wellfound.com/company/converj"},
    ],
    "uplers": [
        {"name": "Perfios", "url": "https://perfios.com/careers"},
        {"name": "Alchemyst AI", "url": "https://uplers.com/company/alchemyst-ai"},
        {"name": "ShelfPay", "url": "https://uplers.com/company/shelfpay"},
        {"name": "PyjamaHR", "url": "https://uplers.com/company/pyjamahr"},
    ],
    "builtin": [
        {"name": "Biva AI", "url": "https://builtin.com/company/biva"},
    ],
    "expertia": [
        {"name": "DesignX", "url": "https://expertia.ai/designx-digital"},
    ],
    "cutshort": [
        {"name": "DoSelect", "url": "https://cutshort.io/company/doselect"},
    ],
}

# ===================================================================
# ASHBY_COMPANIES - Companies using Ashby ATS
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
    {"name": "Firstbase", "ats": "ashby", "slug": "firstbase"},
    {"name": "AMPER", "ats": "ashby", "slug": "amperelectric"},
    {"name": "Unbox Robotics", "ats": "ashby", "slug": "unboxrobotics"},
    {"name": "Sui", "ats": "ashby", "slug": "sui"},
    {"name": "Sahara", "ats": "ashby", "slug": "sahara"},
    {"name": "Teraflow", "ats": "ashby", "slug": "teraflow"},
    {"name": "marketfeed", "ats": "ashby", "slug": "marketfeed"},
    {"name": "VOIZ", "ats": "ashby", "slug": "voiz"},
    {"name": "Airbound", "ats": "ashby", "slug": "airbound"},
    {"name": "PATH", "ats": "ashby", "slug": "path"},
    {"name": "Ivy", "ats": "ashby", "slug": "ivy"},
    {"name": "CRED", "ats": "ashby", "slug": "cred"},
    {"name": "Stealth Startup", "ats": "ashby", "slug": "stealth"},
    {"name": "Super.com", "ats": "ashby", "slug": "super.com"},
    {"name": "Fin", "ats": "ashby", "slug": "fin"},  # remote product
    {"name": "Protege", "ats": "ashby", "slug": "protege"},
    {"name": "Winona", "ats": "ashby", "slug": "winona"},
    {"name": "Jellyfish", "ats": "ashby", "slug": "jellyfish"}, 
    {"name": "Clerk", "ats": "ashby", "slug": "clerk"},        
    {"name": "Super.com", "ats": "ashby", "slug": "super.com"},
]

# ===================================================================
# LEGACY - Keep for backward compatibility
# ===================================================================
COMPANIES = [
    {"name": "Pixlogix Infotech", "ats": "unknown", "source": "Indeed/LinkedIn"},
    {"name": "CloudOne Digital", "ats": "unknown"},
    {"name": "Freemius", "ats": "unknown"},
    {"name": "Awesome Motive", "ats": "unknown"},
    {"name": "Liquid Web", "ats": "unknown"},
    {"name": "Wipro", "ats": "unknown"},
    {"name": "Accenture", "ats": "unknown"},
    {"name": "Groww", "ats": "unknown"},
]
