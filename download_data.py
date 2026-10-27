import os
import pandas as pd
import random

os.makedirs("data", exist_ok=True)
output_path = os.path.join("data", "raw_urls.csv")

print("Generating clean raw URL dataset...")

# Legitimate base domains and paths
legit_domains = [
    "google.com", "youtube.com", "microsoft.com", "apple.com", "amazon.com",
    "wikipedia.org", "linkedin.com", "github.com", "cloudflare.com", "netflix.com",
    "stackoverflow.com", "medium.com", "reddit.com", "nytimes.com", "bbc.co.uk",
    "adobe.com", "spotify.com", "dropbox.com", "cnn.com", "espn.com"
]
legit_paths = [
    "", "/about", "/contact", "/terms", "/help", "/articles/2024",
    "/profile/view", "/dashboard", "/docs/guide", "/search?q=query"
]

# Phishing components
scam_brands = ["paypal", "chase", "wellsfargo", "appleid", "netflix", "bankofamerica", "coinbase", "binance", "metamask", "microsoft-security"]
scam_words = ["verify", "login", "account-update", "secure-portal", "auth-check", "recover", "wallet-sync"]
suspicious_tlds = [".xyz", ".top", ".tk", ".fit", ".icu", ".work", ".buzz"]

urls = []
labels = []

# Generate 1,500 legitimate URLs (Label 0)
for _ in range(1500):
    domain = random.choice(legit_domains)
    path = random.choice(legit_paths)
    proto = "https://" if random.random() > 0.1 else "http://"
    sub = "www." if random.random() > 0.5 else ""
    urls.append(f"{proto}{sub}{domain}{path}")
    labels.append(0)

# Generate 1,500 phishing URLs (Label 1)
for _ in range(1500):
    brand = random.choice(scam_brands)
    action = random.choice(scam_words)
    tld = random.choice(suspicious_tlds)
    proto = "http://" if random.random() > 0.3 else "https://"
    
    style = random.randint(1, 4)
    if style == 1:
        # e.g., http://paypal-security-login.xyz/update
        url = f"{proto}{brand}-{action}{tld}/signin?id={random.randint(1000, 9999)}"
    elif style == 2:
        # IP address host
        ip = f"{random.randint(11, 199)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        url = f"http://{ip}/{brand}/login.php"
    elif style == 3:
        # Multi-subdomain trick: login.paypal.com.account-update.xyz
        url = f"{proto}login.{brand}.com.{action}{tld}/index.html"
    else:
        # Random high-entropy token domain
        token = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
        url = f"{proto}{token}{tld}/{brand}-verify"
        
    urls.append(url)
    labels.append(1)

df = pd.DataFrame({"url": urls, "label": labels})
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv(output_path, index=False)

print(f"Success! Created {len(df)} URLs in {output_path}")
print(df["label"].value_counts())