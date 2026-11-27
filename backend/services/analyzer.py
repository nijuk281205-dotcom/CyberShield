"""Rule-based fraud indicators.

The analyzer only reads the *text* of a URL or message. It never opens a link,
resolves DNS, or executes anything the user submitted.
"""
import ipaddress
import re
from urllib.parse import urlparse, unquote

SUSPICIOUS_KEYWORDS = [
    "login", "signin", "verify", "update", "secure", "account", "banking", "confirm",
    "password", "wallet", "bonus", "free", "gift", "prize", "winner", "claim", "suspend",
    "unlock", "invoice", "refund", "kyc",
]
SUSPICIOUS_TLDS = {"zip", "mov", "tk", "ml", "ga", "cf", "gq", "xyz", "top", "click", "country", "work", "support", "loan", "icu"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy", "shorturl.at", "tiny.cc"}
BRANDS = ["paypal", "amazon", "google", "microsoft", "apple", "netflix", "facebook", "instagram",
          "sbi", "hdfc", "icici", "paytm", "phonepe", "irctc", "whatsapp", "flipkart"]

LIMITATIONS = (
    "This is a rule-based check of the text of the link or message only. It does not visit the site, "
    "check reputation databases, or know about brand-new scams. A Low Risk result does not prove "
    "something is safe, and a High Risk result does not prove it is fraudulent."
)


def _level(score):
    if score >= 55:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def _finding(title, detail, points):
    return {"title": title, "detail": detail, "points": points}


def normalize_url(raw):
    raw = raw.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
        return "http://" + raw, True
    return raw, False


def analyze_url(raw):
    url, added_scheme = normalize_url(raw)
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        return None
    if not host or not re.fullmatch(r"[a-z0-9.\-\[\]:_]+", host):
        return None
    if "." not in host and ":" not in host:
        return None

    findings = []

    if parsed.scheme not in ("http", "https"):
        findings.append(_finding("Unusual link type", f"The link uses '{parsed.scheme}://' instead of http(s).", 25))
    elif parsed.scheme == "http":
        if added_scheme:
            findings.append(_finding("No HTTPS specified", "No https:// was given, so an encrypted connection can't be assumed.", 10))
        else:
            findings.append(_finding("Not using HTTPS", "The link uses plain HTTP, so traffic is not encrypted.", 15))

    is_ip = False
    try:
        ipaddress.ip_address(host.strip("[]"))
        is_ip = True
    except ValueError:
        if re.fullmatch(r"(0x[0-9a-f]+|\d+)(\.(0x[0-9a-f]+|\d+)){0,3}", host):
            is_ip = True
    if is_ip:
        findings.append(_finding("IP address instead of a domain", "Legitimate services rarely ask you to log in at a raw IP address.", 30))

    labels = host.split(".")
    tld = labels[-1] if len(labels) > 1 else ""

    if not is_ip:
        if host in SHORTENERS:
            findings.append(_finding("URL shortener", "The real destination is hidden behind a shortened link.", 15))
        if tld in SUSPICIOUS_TLDS:
            findings.append(_finding("Higher-risk domain ending", f"'.{tld}' is commonly used in low-cost or abused domains.", 12))
        if len(labels) > 4:
            findings.append(_finding("Many subdomains", f"The host has {len(labels)} parts, a pattern used to imitate real sites.", 15))
        if host.count("-") >= 2:
            findings.append(_finding("Many hyphens in domain", "Domains with several hyphens often imitate brand names.", 10))
        if "xn--" in host:
            findings.append(_finding("Punycode / look-alike characters", "The domain may use look-alike international characters.", 20))
        if sum(c.isdigit() for c in host) >= 4:
            findings.append(_finding("Many digits in domain", "Random-looking digits are common in throwaway domains.", 8))

        registrable = ".".join(labels[-2:]) if len(labels) >= 2 else host
        main = registrable.split(".")[0]
        sub_part = ".".join(labels[:-2])
        for brand in BRANDS:
            if brand in sub_part or (brand in main and main != brand):
                findings.append(_finding(
                    "Possible brand impersonation",
                    f"The name '{brand}' appears in the address but the main domain is '{registrable}'.", 25))
                break

    if parsed.username is not None or "@" in parsed.netloc:
        findings.append(_finding("'@' in the address", "Text before '@' is ignored by browsers and is used to disguise the real host.", 25))

    if port and port not in (80, 443):
        findings.append(_finding("Unusual port", f"The link uses port {port}, which normal websites rarely expose.", 10))

    if len(url) > 100:
        findings.append(_finding("Very long URL", f"{len(url)} characters; long URLs can hide the real destination.", 15))
    elif len(url) > 75:
        findings.append(_finding("Long URL", f"{len(url)} characters.", 8))

    decoded = unquote(parsed.path + "?" + parsed.query)
    if url.count("%") >= 3:
        findings.append(_finding("Heavy percent-encoding", "Lots of encoded characters can obscure what the link really contains.", 10))
    if re.search(r"[<>\"'`{}|\\^]", decoded) or "//" in parsed.path:
        findings.append(_finding("Suspicious characters", "The path contains unusual characters or a double slash.", 10))
    if re.search(r"(https?://|redirect=|url=|next=|return=)", parsed.query.lower()):
        findings.append(_finding("Redirect parameter", "The link contains another URL or redirect instruction.", 10))

    haystack = (host + " " + decoded).lower()
    hits = sorted({k for k in SUSPICIOUS_KEYWORDS if k in haystack})
    if hits:
        pts = min(8 + 4 * (len(hits) - 1), 24)
        findings.append(_finding("Sensitive keywords", "Found: " + ", ".join(hits[:6]) + ". Scam pages often use these to look urgent or official.", pts))

    score = min(sum(f["points"] for f in findings), 100)
    level = _level(score)
    summary = (f"{len(findings)} indicator(s) found. Overall: {level} risk." if findings
               else "No common risk indicators found in the link text. Overall: Low risk.")
    recs = {
        "High": [
            "Do not open this link or enter any personal details.",
            "If it came from a message, delete it or report it as spam or phishing.",
            "If you already entered a password, change it right away and enable two-factor authentication.",
            "Visit the real company by typing its address yourself or using its official app.",
        ],
        "Medium": [
            "Be careful. Avoid logging in or paying through this link.",
            "Check the domain letter by letter against the official website.",
            "Confirm with the sender through a different channel before acting.",
        ],
        "Low": [
            "No strong warning signs in the text, but stay alert.",
            "Check the sender and context. Never share OTPs or passwords through links.",
            "Keep your browser and device updated.",
        ],
    }[level]
    return {"risk_level": level, "score": score, "summary": summary, "findings": findings,
            "recommendations": recs, "limitations": LIMITATIONS}


TEXT_RULES = [
    ("Urgency or threats", r"\b(urgent|immediately|within \d+ (hours?|minutes?)|last warning|final notice|suspended|blocked|expire[sd]?|act now)\b", 15),
    ("Asks for OTP, PIN or password", r"\b(otp|one[- ]time password|pin|cvv|password|passcode|card number)\b", 25),
    ("Prize or reward offer", r"\b(you (have )?won|winner|lottery|prize|congratulations|free gift|cashback|reward)\b", 20),
    ("Money transfer request", r"\b(send money|transfer|gift cards?|western union|bitcoin|crypto|processing fee|advance fee|wire)\b", 20),
    ("Account or KYC warning", r"\b(kyc|verify your account|account (will be )?(closed|suspended|locked)|update your (details|account|bank))\b", 20),
    ("Impersonates an authority", r"\b(bank|income tax|customs|police|cyber ?crime|courier|support team|customer care)\b", 8),
    ("Secrecy or pressure", r"\b(don'?t tell|keep (this )?secret|do not share with anyone|only you)\b", 12),
]


def analyze_text(raw):
    findings = []
    lower = raw.lower()
    for title, pattern, pts in TEXT_RULES:
        if re.search(pattern, lower):
            findings.append(_finding(title, "The message uses wording commonly seen in scams for this pattern.", pts))
    urls = re.findall(r"(https?://\S+|www\.\S+)", raw)
    if urls:
        sub = analyze_url(urls[0].rstrip(".,)"))
        if sub and sub["risk_level"] != "Low":
            findings.append(_finding("Contains a risky link", f"The first link in the message was rated {sub['risk_level']} risk.",
                                     25 if sub["risk_level"] == "High" else 15))
        else:
            findings.append(_finding("Contains a link", "Messages that push you to click a link deserve extra care.", 5))
    if re.search(r"\b\d{10,}\b", raw) and re.search(r"\b(call|whatsapp|contact)\b", lower):
        findings.append(_finding("Unknown phone number to contact", "Scammers often ask you to call or message a number.", 8))
    if len(re.findall(r"[A-Z]{4,}", raw)) >= 3 or raw.count("!") >= 3:
        findings.append(_finding("Shouting style", "Excess capital letters or exclamation marks add false urgency.", 5))

    score = min(sum(f["points"] for f in findings), 100)
    level = _level(score)
    summary = (f"{len(findings)} suspicious pattern(s) found. Overall: {level} risk." if findings
               else "No common scam patterns found. Overall: Low risk.")
    recs = {
        "High": ["Do not reply, click links, or share any codes or details.",
                 "Block the sender and report it (in India: cybercrime.gov.in or helpline 1930).",
                 "Contact the organisation using a number from its official website."],
        "Medium": ["Do not act on it yet. Verify with the organisation through an official channel.",
                   "Never share OTPs, PINs or passwords with anyone."],
        "Low": ["No strong scam patterns, but stay cautious with unexpected messages.",
                "Never share OTPs or passwords, even if the sender seems familiar."],
    }[level]
    return {"risk_level": level, "score": score, "summary": summary, "findings": findings,
            "recommendations": recs, "limitations": LIMITATIONS}
