# roles.py
# ----------------------------------
# Role Intelligence Engine
# ----------------------------------

ROLE_MAP = {
    "design": [
        "designer", "ui", "ux",
        "visual", "graphic", "product designer"
    ],
    "product": [
        "product manager", "apm",
        "associate product", "product owner"
    ],
    "business": [
        "business analyst", "operations",
        "strategy", "consultant"
    ],
    "software": [
        "software", "engineer", "developer",
        "frontend", "backend", "full stack",
        "mobile", "ios", "android"
    ],
    "client": [
        "customer success", "client success",
        "account manager", "relationship"
    ]
}


def infer_role(title: str) -> str:
    if not title:
        return "other"

    t = title.lower()

    for role, keywords in ROLE_MAP.items():
        for k in keywords:
            if k in t:
                return role

    return "other"
