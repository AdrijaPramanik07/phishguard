import math
import re
from urllib.parse import urlparse
import tldextract

# Suspicious Top-Level Domains (TLDs) frequently abused in free/cheap phishing attacks
SUSPICIOUS_TLDS = {
    "xyz", "top", "work", "tk", "ml", "ga", "cf", "gq", "buzz", "club", "icu", "fit"
}

# Sensitive target keywords often present in phishing link paths or subdomains
SENSITIVE_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "banking", "signin",
    "password", "confirm", "wallet", "authenticate", "service"
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
    """
    Extracts lexical, structural, and keyword features from a raw URL string.
    Returns a dictionary of numerical and boolean features ready for ML models.
    """
    # Ensure scheme exists so urlparse handles host vs path correctly
    url_to_parse = url if "://" in url else "http://" + url
    parsed = urlparse(url_to_parse)
    extracted_domain = tldextract.extract(url)

    hostname = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query

    features = {}

    # --- 1. Length Features ---
    features["url_length"] = len(url)
    features["hostname_length"] = len(hostname)
    features["path_length"] = len(path)
    features["query_length"] = len(query)

    # --- 2. Character Counts & Ratios ---
    features["count_dots"] = url.count(".")
    features["count_hyphens"] = url.count("-")
    features["count_at"] = url.count("@")
    features["count_question"] = url.count("?")
    features["count_percent"] = url.count("%")
    features["count_equal"] = url.count("=")
    features["count_slash"] = url.count("/")
    features["count_digits"] = sum(c.isdigit() for c in url)
    features["count_letters"] = sum(c.isalpha() for c in url)
    
    # Digit to letter ratio (phishing URLs often contain long random digit strings)
    features["digit_letter_ratio"] = round(
        features["count_digits"] / max(features["count_letters"], 1), 4
    )

    # --- 3. Domain & Structural Indicators ---
    # Subdomain depth: counts dots in subdomain portion
    features["subdomain_count"] = (
        len(extracted_domain.subdomain.split(".")) if extracted_domain.subdomain else 0
    )
    
    # Check if host is an explicit IP address (e.g., http://192.168.1.1/login)
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    features["is_ip_address"] = int(bool(re.match(ip_pattern, hostname.split(":")[0])))

    # Protocol check
    features["uses_https"] = int(url.lower().startswith("https://"))

    # Punycode indicator (used in homograph domain impersonation attacks)
    features["is_punycode"] = int("xn--" in hostname)

    # Suspicious TLD check
    tld = extracted_domain.suffix.lower()
    features["is_suspicious_tld"] = int(tld in SUSPICIOUS_TLDS)

    # Entropy of hostname (high randomness suggests algorithmic domain generation)
    features["hostname_entropy"] = calculate_entropy(hostname)

    # --- 4. Keyword Deception Flags ---
    lower_url = url.lower()
    features["keyword_count"] = sum(
        1 for kw in SENSITIVE_KEYWORDS if kw in lower_url
    )

    return features


if __name__ == "__main__":
    # Quick self-test to verify functionality
    test_urls = [
        "https://www.google.com",
        "http://paypa1-security.verify-login.xyz/update-pass?session=123",
        "http://192.168.0.1/admin/login.php"
    ]

    print("--- Testing Feature Extraction ---")
    for u in test_urls:
        feats = extract_features(u)
        print(f"\nURL: {u}")
        print(f"Features ({len(feats)} extracted):")
        for k, v in list(feats.items())[:8]:  # Preview first 8 features
            print(f"  {k}: {v}")
        print("  ...")