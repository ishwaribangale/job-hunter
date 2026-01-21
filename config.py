# config.py
# ----------------------------------
# Global Config
# ----------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 12

TOP_COMPANIES = [
    {"name": "Notion", "ats": "lever", "slug": "notion"},
    {"name": "Figma", "ats": "lever", "slug": "figma"},
    {"name": "Airtable", "ats": "lever", "slug": "airtable"},

    {"name": "Stripe", "ats": "greenhouse", "slug": "stripeinc"},
    {"name": "Razorpay", "ats": "greenhouse", "slug": "razorpaysoftware"},
    {"name": "Atlassian", "ats": "greenhouse", "slug": "atlassian"},
    {"name": "PhonePe", "ats": "greenhouse", "slug": "phonepejobs"},
]
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
    {"name": "Trello", "url": "https://www.atlassian.com/company/careers"},
    {"name": "Zapier", "url": "https://zapier.com/jobs"},
    {"name": "Calendly", "url": "https://careers.calendly.com"},
    {"name": "Webflow", "url": "https://webflow.com/careers"},
    {"name": "Framer", "url": "https://www.framer.com/careers"},

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
    {"name": "Coinbase", "url": "https://www.coinbase.com/careers"},
    {"name": "Robinhood", "url": "https://careers.robinhood.com"},

    # --------------------
    # DATA / SECURITY
    # --------------------
    {"name": "Snowflake", "url": "https://careers.snowflake.com"},
    {"name": "Databricks", "url": "https://www.databricks.com/company/careers"},
    {"name": "Elastic", "url": "https://www.elastic.co/careers"},
    {"name": "MongoDB", "url": "https://www.mongodb.com/careers"},
    {"name": "Snyk", "url": "https://snyk.io/careers"},
    {"name": "Okta", "url": "https://www.okta.com/company/careers"},
    {"name": "Auth0", "url": "https://auth0.com/careers"},

    # --------------------
    # YC / STARTUPS (HIGH SIGNAL)
    # --------------------
    {"name": "Ramp", "url": "https://ramp.com/careers"},
    {"name": "Rippling", "url": "https://www.rippling.com/careers"},
    {"name": "Gusto", "url": "https://gusto.com/about/careers"},
    {"name": "Mercury", "url": "https://mercury.com/careers"},
    {"name": "Scale AI", "url": "https://scale.com/careers"},
    {"name": "Brex", "url": "https://www.brex.com/careers"},
    {"name": "Retool", "url": "https://retool.com/careers"},
    {"name": "Notion Labs", "url": "https://www.notion.so/careers"},
]
