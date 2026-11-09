import math
import re
from urllib.parse import urlparse
import tldextract

# Suspicious Top-Level Domains (TLDs) frequently abused in scam campaigns
SUSPICIOUS_TLDS = {
    "xyz", "top", "work", "tk", "ml", "ga", "cf", "gq", "buzz", "club", "icu", "fit", "top"
}

# Major trusted global domains that should not be flagged purely for long search parameters
TRUSTED_ROOT_DOMAINS = {
    "google.com", "youtube.com", "microsoft.com", "apple.com", "amazon.com",
    "github.com", "linkedin.com", "wikipedia.org", "cloudflare.com", "netflix.com",
    "stackoverflow.com", "medium.com", "yahoo.com", "bing.com", "reddit.com"
}

SENSITIVE_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "banking", "signin",
    "password", "confirm", "wallet", "authenticate"
]

def calculate_entropy(text: str) -> float:
    """Calculates Shannon Entropy of a string to detect randomized/dga domain names."""
    if not text:
        return 0.0
    entropy = 0.0
    length = len(text)
    for char in set(text):
        prob = text.count(char) / length
        entropy -= prob * math.log2(prob)
    return round(entropy, 4)

def extract_features(url: str) -> dict:
    url_to_parse = url if "://" in url else "http://" + url
    parsed = urlparse(url_to_parse)
    extracted = tldextract.extract(url)

    hostname = (parsed.netloc or "").lower().split(":")[0]
    path = parsed.path or ""
    query = parsed.query or ""
    root_domain = f"{extracted.domain}.{extracted.suffix}".lower()

    features = {}

    # --- 1. Structural & Hostname Features ---
    features["url_length"] = len(url)
    features["hostname_length"] = len(hostname)
    features["path_length"] = len(path)
    features["query_length"] = len(query)

    # Subdomain depth
    subdomain_parts = [p for p in extracted.subdomain.split(".") if p] if extracted.subdomain else []
    features["subdomain_count"] = len(subdomain_parts)

    # IP address as host
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    features["is_ip_address"] = int(bool(re.match(ip_pattern, hostname)))

    # HTTPS check
    features["uses_https"] = int(url.lower().startswith("https://"))

    # Punycode check
    features["is_punycode"] = int("xn--" in hostname)

    # TLD checks
    features["is_suspicious_tld"] = int(extracted.suffix.lower() in SUSPICIOUS_TLDS)
    features["is_trusted_domain"] = int(root_domain in TRUSTED_ROOT_DOMAINS)

    # Hostname entropy (only on hostname, NOT the query string)
    features["hostname_entropy"] = calculate_entropy(extracted.domain)

    # --- 2. Character Counts (Focused on Hostname & Path) ---
    features["count_dots"] = hostname.count(".")
    features["count_hyphens"] = hostname.count("-")
    features["count_at"] = url.count("@")
    features["count_digits"] = sum(c.isdigit() for c in hostname)
    features["count_slash"] = path.count("/")
    
    # Digit ratio in hostname
    host_letters = sum(c.isalpha() for c in hostname)
    features["host_digit_ratio"] = round(features["count_digits"] / max(host_letters, 1), 4)

    # --- 3. Keyword Deception Flags ---
    # Focus keyword search on hostname and path rather than search query text
    host_and_path = f"{hostname}{path}".lower()
    features["keyword_count"] = sum(1 for kw in SENSITIVE_KEYWORDS if kw in host_and_path)

    return features