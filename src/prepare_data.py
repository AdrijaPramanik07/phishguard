import os
import sys
import pandas as pd
import tldextract

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.features import extract_features

def extract_registered_domain(url):
    try:
        ext = tldextract.extract(str(url))
        return f"{ext.domain}.{ext.suffix}".lower()
    except Exception:
        return ""

def main():
    csv_path = os.path.join("data", "raw_urls.csv")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run download_data.py first.")
        return

    print("Loading raw URL dataset...")
    df = pd.read_csv(csv_path)

    # Standardize headers
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Find URL and Label columns dynamically
    url_col = next((c for c in ["url", "urls", "link", "address"] if c in df.columns), df.columns[0])
    label_col = next((c for c in ["label", "status", "class", "target", "result"] if c in df.columns), df.columns[1])

    df = df[[url_col, label_col]].dropna()
    df.columns = ["url", "label"]
    df["url"] = df["url"].astype(str).str.strip()
    df = df[df["url"].str.len() > 3]

    # Convert label to 0 and 1
    if df["label"].dtype == object:
        df["label"] = df["label"].astype(str).str.lower().map(
            lambda x: 1 if any(w in x for w in ["1", "phish", "bad", "malicious"]) else 0
        )
    else:
        df["label"] = (df["label"] == 1).astype(int)

    # Drop duplicates
    df = df.drop_duplicates(subset=["url"])
    df["domain"] = df["url"].apply(extract_registered_domain)
    df = df[df["domain"] != ""].drop_duplicates(subset=["domain", "label"])

    # Limit to 5,000 balanced samples for quick local training if dataset is huge
    if len(df) > 5000:
        df = df.groupby("label", group_keys=False).apply(
            lambda x: x.sample(min(len(x), 2500), random_state=42)
        )

    print(f"Processing {len(df)} unique URLs...")
    print(f"Class breakdown:\n{df['label'].value_counts()}")

    # Extract features
    rows = []
    labels = []
    for _, item in df.iterrows():
        try:
            feats = extract_features(item["url"])
            rows.append(feats)
            labels.append(item["label"])
        except Exception:
            continue

    features_df = pd.DataFrame(rows)
    features_df["label"] = labels

    output_path = os.path.join("data", "features.csv")
    features_df.to_csv(output_path, index=False)
    print(f"\nDone! Saved {len(features_df)} rows to {output_path}")

if __name__ == "__main__":
    main()