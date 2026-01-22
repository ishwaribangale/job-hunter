# config.py
# ----------------------------------
# Global Config - FIXED & OPTIMIZED
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
# TOP_COMPANIES - Companies with VERIFIED ATS slugs
# Only include companies where slugs are confirmed working
# ===================================================================
TOP_COMPANIES = [
    # --------------------
    # LEVER COMPANIES
    # --------------------
    {"name": "Notion", "ats": "lever", "slug": "notion"},
    {"name": "Figma", "ats": "lever", "slug": "figma"},
    {"name": "Airtable", "ats": "lever", "slug": "airtable"},
    
    # --------------------
    # GREENHOUSE - VERIFIED WORKING SLUGS
    # --------------------
    # Indian Companies
   {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepe"},  # Change from "phonepejobs"
    {"name": "PayPay India", "ats": "greenhouse", "slug": "paypay"},
    {"name": "RevX", "ats": "greenhouse", "slug": "revx"},
    {"name": "Zinnia", "ats": "greenhouse", "slug": "zinnia"},
    {"name": "Netradyne", "ats": "greenhouse", "slug": "netradyne"},
    {"name": "Samsara", "ats": "greenhouse", "slug": "samsara"},
    
    # Global Tech Companies
    {"name": "Anthropic", "ats": "greenhouse", "slug": "anthropic"},
    {"name": "OneTrust", "ats": "greenhouse", "slug": "onetrust"},
    {"name": "Airbnb", "ats": "greenhouse", "slug": "airbnb"},
    {"name": "Dropbox", "ats": "greenhouse", "slug": "dropbox"},
    {"name": "HubSpot", "ats": "greenhouse", "slug": "hubspot"},
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
# CAREER_PAGES - Auto-detection for companies without known ATS
# The scraper will automatically detect Greenhouse/Lever/Ashby/Generic
# ===================================================================
CAREER_PAGES = [
    # --------------------
    # AI / DEV TOOLS
    # --------------------
    {"name": "OpenAI", "url": "https://openai.com/careers"},
    {"name": "Anthropic", "url": "https://www.anthropic.com/careers"},
    {"name": "Cohere", "url": "https://cohere.com/careers"},
    {"name": "Hugging Face", "url": "https://huggingface.co/careers"},
    {"name": "Stability AI", "url": "https://stability.ai/careers"},
    {"name": "Midjourney", "url": "https://www.midjourney.com/careers"},
    {"name": "Perplexity", "url": "https://www.perplexity.ai/careers"},

    # --------------------
    # PRODUCT / SAAS
    # --------------------
    {"name": "Linear", "url": "https://linear.app/careers"},
    {"name": "Notion", "url": "https://www.notion.so/careers"},
    {"name": "Figma", "url": "https://www.figma.com/careers"},
    {"name": "Canva", "url": "https://www.canva.com/careers"},
    {"name": "Airtable", "url": "https://airtable.com/careers"},
    {"name": "Miro", "url": "https://miro.com/careers"},
    {"name": "ClickUp", "url": "https://clickup.com/careers"},
    {"name": "Asana", "url": "https://asana.com/jobs"},
    {"name": "Trello/Atlassian", "url": "https://www.atlassian.com/company/careers"},
    {"name": "Zapier", "url": "https://zapier.com/jobs"},
    {"name": "Calendly", "url": "https://careers.calendly.com"},
    {"name": "Webflow", "url": "https://webflow.com/careers"},
    {"name": "Framer", "url": "https://www.framer.com/careers"},
    {"name": "Loom", "url": "https://www.loom.com/careers"},

    # --------------------
    # DEV INFRA / CLOUD
    # --------------------
    {"name": "Vercel", "url": "https://vercel.com/careers"},
    {"name": "Netlify", "url": "https://www.netlify.com/careers"},
    {"name": "Cloudflare", "url": "https://www.cloudflare.com/careers"},
    {"name": "HashiCorp", "url": "https://www.hashicorp.com/careers"},
    {"name": "GitLab", "url": "https://about.gitlab.com/jobs"},
    {"name": "GitHub", "url": "https://github.com/about/careers"},
    {"name": "Docker", "url": "https://www.docker.com/careers"},
    {"name": "Postman", "url": "https://www.postman.com/company/careers"},
    {"name": "Supabase", "url": "https://supabase.com/careers"},
    {"name": "PlanetScale", "url": "https://planetscale.com/careers"},
    {"name": "DigitalOcean", "url": "https://www.digitalocean.com/careers"},
    {"name": "Railway", "url": "https://railway.app/careers"},
    {"name": "Render", "url": "https://render.com/careers"},

    # --------------------
    # FINTECH
    # --------------------
    {"name": "Stripe", "url": "https://stripe.com/jobs"},
    {"name": "Wise", "url": "https://www.wise.jobs"},
    {"name": "Revolut", "url": "https://www.revolut.com/careers"},
    {"name": "Brex", "url": "https://www.brex.com/careers"},
    {"name": "Plaid", "url": "https://plaid.com/careers"},
    {"name": "Razorpay", "url": "https://razorpay.com/jobs"},
    {"name": "PhonePe", "url": "https://www.phonepe.com/careers"},
    {"name": "Paytm", "url": "https://paytm.com/careers"},
    {"name": "CRED", "url": "https://cred.club/careers"},
    {"name": "Jupiter", "url": "https://www.jupiter.money/careers"},
    {"name": "Coinbase", "url": "https://www.coinbase.com/careers"},
    {"name": "Robinhood", "url": "https://careers.robinhood.com"},

    # --------------------
    # INDIAN STARTUPS
    # --------------------
    {"name": "Zerodha", "url": "https://zerodha.com/careers"},
    {"name": "Swiggy", "url": "https://www.swiggy.com/careers"},
    {"name": "Zomato", "url": "https://www.zomato.com/careers"},
    {"name": "Meesho", "url": "https://www.meesho.com/careers"},
    {"name": "Dream11", "url": "https://www.dream11.com/careers"},
    {"name": "Unacademy", "url": "https://unacademy.com/careers"},
    {"name": "BYJU'S", "url": "https://byjus.com/careers"},
    {"name": "Ola", "url": "https://www.olacabs.com/careers"},
    {"name": "PolicyBazaar", "url": "https://www.policybazaar.com/about-us/careers"},
    {"name": "Nykaa", "url": "https://www.nykaa.com/careers"},
    {"name": "Groww", "url": "https://groww.in/careers"},

    # --------------------
    # DATA / SECURITY
    # --------------------
    {"name": "Snowflake", "url": "https://careers.snowflake.com"},
    {"name": "Databricks", "url": "https://www.databricks.com/company/careers"},
    {"name": "Elastic", "url": "https://www.elastic.co/careers"},
    {"name": "MongoDB", "url": "https://www.mongodb.com/careers"},
    {"name": "Confluent", "url": "https://www.confluent.io/careers"},
    {"name": "Snyk", "url": "https://snyk.io/careers"},
    {"name": "Okta", "url": "https://www.okta.com/company/careers"},
    {"name": "Auth0", "url": "https://auth0.com/careers"},
    {"name": "1Password", "url": "https://1password.com/careers"},

    # --------------------
    # YC / STARTUPS (HIGH SIGNAL)
    # --------------------
    {"name": "Ramp", "url": "https://ramp.com/careers"},
    {"name": "Rippling", "url": "https://www.rippling.com/careers"},
    {"name": "Gusto", "url": "https://gusto.com/about/careers"},
    {"name": "Mercury", "url": "https://mercury.com/careers"},
    {"name": "Scale AI", "url": "https://scale.com/careers"},
    {"name": "Retool", "url": "https://retool.com/careers"},
    {"name": "Airtable", "url": "https://airtable.com/careers"},
    {"name": "Lattice", "url": "https://lattice.com/careers"},
    {"name": "Deel", "url": "https://www.deel.com/careers"},
    {"name": "Remote", "url": "https://remote.com/careers"},
    {"name": "Flexport", "url": "https://www.flexport.com/careers"},
    
    # --------------------
    # E-COMMERCE / CONSUMER
    # --------------------
    {"name": "Shopify", "url": "https://www.shopify.com/careers"},
    {"name": "Etsy", "url": "https://www.etsy.com/careers"},
    {"name": "Faire", "url": "https://www.faire.com/careers"},
    {"name": "Gorgias", "url": "https://www.gorgias.com/careers"},
]

# ===================================================================
# ASHBY_COMPANIES - Separate list for dedicated Ashby scraper
# ===================================================================
ASHBY_COMPANIES = [
    {"name": "Zapier", "ats": "ashby", "slug": "zapier"},
    {"name": "Ramp", "ats": "ashby", "slug": "ramp"},
    {"name": "Notion", "ats": "ashby", "slug": "notion"},
    {"name": "Linear", "ats": "ashby", "slug": "linear"},
    {"name": "Retool", "ats": "ashby", "slug": "retool"},
    {"name": "Mercury", "ats": "ashby", "slug": "mercury"},
    {"name": "Anthropic", "ats": "ashby", "slug": "anthropic"},
    {"name": "Scale AI", "ats": "ashby", "slug": "scale"},
    {"name": "Supabase", "ats": "ashby", "slug": "supabase"},
    {"name": "Vercel", "ats": "ashby", "slug": "vercel"},
    {"name": "Vanta", "ats": "ashby", "slug": "vanta"},
    {"name": "Watershed", "ats": "ashby", "slug": "watershed"},
    {"name": "Brex", "ats": "ashby", "slug": "brex"},
    {"name": "Anduril", "ats": "ashby", "slug": "anduril"},
    {"name": "Cursor", "ats": "ashby", "slug": "cursor"},
]
