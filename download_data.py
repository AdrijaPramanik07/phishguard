import os
import random
import pandas as pd

os.makedirs("data", exist_ok=True)
output_path = os.path.join("data", "raw_urls.csv")

print("Generating realistic URL dataset with diverse lengths...")

legit_domains = [
    "google.com", "youtube.com", "microsoft.com", "apple.com", "amazon.com",
    "wikipedia.org", "linkedin.com", "github.com", "cloudflare.com", "netflix.com",
    "stackoverflow.com", "medium.com", "reddit.com", "yahoo.com", "bing.com"
]

# Mix of short, medium, and very long query strings for benign sites
benign_query_templates = [
    "",
    "/about",
    "/help/faq",
    "/search?q={term}&oq={term}&sourceid=chrome&ie=UTF-8",
    "/results?search_query={term}&sp=EgIQAQ%253D%253D",
    "/dp/B08N5WRWNW?ref_=Oct_DLandingS_D_12345678_0&smid=ATVPDKIKX0DER",
    "/questions/12345678/{term}-in-python-and-machine-learning-data-pipeline",
    "/search?q={term}&client=firefox-b-d&sca_esv=123456&biw=1920&bih=955&dpr=1"
]

search_terms = ["youtube", "machine-learning", "cybersecurity", "nextjs-tailwind", "fastapi-docs", "weather-today", "flight-booking"]

scam_brands = ["paypal", "chase", "wellsfargo", "appleid", "netflix", "bankofamerica", "coinbase", "binance", "metamask"]
scam_words = ["verify", "login", "account-update", "secure-portal", "auth-check", "recover", "wallet-sync"]
suspicious_tlds = [".xyz", ".top", ".tk", ".fit", ".icu", ".work", ".buzz"]

urls = []
labels = []

# 1. Generate 2,000 Legitimate URLs (including very long parameter URLs)
for _ in range(2000):
    domain = random.choice(legit_domains)
    template = random.choice(benign_query_templates)
    term = random.choice(search_terms)
    path = template.format(term=term)
    
    # 30% of legitimate URLs are given long tracking strings
    if random.random() > 0.6:
        long_hash = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789-_", k=random.randint(60, 140)))
        path += f"&tracking_token={long_hash}&gs_lcrp={long_hash}"

    sub = "www." if random.random() > 0.4 else ""
    urls.append(f"https://{sub}{domain}{path}")
    labels.append(0)

# 2. Generate 2,000 Phishing URLs (deceptive hosts, suspicious TLDs, IP hosts)
for _ in range(2000):
    brand = random.choice(scam_brands)
    action = random.choice(scam_words)
    tld = random.choice(suspicious_tlds)
    proto = "http://" if random.random() > 0.3 else "https://"

    style = random.randint(1, 4)
    if style == 1:
        url = f"{proto}{brand}-{action}{tld}/signin?id={random.randint(1000, 9999)}"
    elif style == 2:
        ip = f"{random.randint(11, 199)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        url = f"http://{ip}/{brand}/login.php"
    elif style == 3:
        url = f"{proto}login.{brand}.com.{action}{tld}/index.html"
    else:
        token = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
        url = f"{proto}{token}{tld}/{brand}-verify"

    urls.append(url)
    labels.append(1)

df = pd.DataFrame({"url": urls, "label": labels})
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} balanced URLs with realistic long parameters.")