import os
import sys

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import numpy as np
import pandas as pd
import shap
from src.features import extract_features
# Plain-English translation rules for technical features
FEATURE_DESCRIPTIONS = {
    "url_length": "Overall URL length is unusually long",
    "hostname_length": "Domain name length is unusually long",
    "path_length": "Website path structure is unusually long",
    "query_length": "URL contains an unusually long query string",
    "count_dots": "Contains a high number of dots (often used in subdomain spoofing)",
    "count_hyphens": "Contains multiple hyphens (common in brand impersonation)",
    "count_at": "Uses '@' symbol (can obscure the true destination host)",
    "count_question": "Contains multiple URL query delimiters",
    "count_percent": "Contains heavy URL percent-encoding (often masks malicious characters)",
    "count_equal": "Contains numerous parameter assignments",
    "count_slash": "Contains deep path nesting with many forward slashes",
    "count_digits": "Contains an abnormally high count of numeric digits",
    "count_letters": "Character distribution pattern is abnormal",
    "digit_letter_ratio": "Suspiciously high ratio of numbers compared to letters",
    "subdomain_count": "Multiple subdomain levels detected (classic spoofing pattern)",
    "is_ip_address": "Uses a direct IP address instead of a standard domain name",
    "uses_https": "Does not use standard HTTPS encryption (unencrypted HTTP connection)",
    "is_punycode": "Uses Punycode encoding (xn--), typical of lookalike homograph attacks",
    "is_suspicious_tld": "Uses an uncommon or high-abuse top-level domain (e.g., .xyz, .top)",
    "hostname_entropy": "Domain name has high character randomness (suggests automated generation)",
    "keyword_count": "Contains sensitive urgency/credential keywords (e.g., 'login', 'verify')"
}

class PhishExplainer:
    def __init__(self, model_path="models/model.joblib"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Run src/train.py first.")
        
        saved_data = joblib.load(model_path)
        self.calibrated_model = saved_data["model"]
        self.base_model = saved_data["base_model"]
        self.feature_names = saved_data["feature_names"]

        # TreeExplainer is fast and exact for tree-based models (XGBoost / Random Forest)
        # If Logistic Regression was selected, we fall back to LinearExplainer or shap.Explainer
        try:
            self.explainer = shap.TreeExplainer(self.base_model)
        except Exception:
            # Fallback for linear pipelines or non-tree estimators
            if hasattr(self.base_model, "named_steps"):
                clf = self.base_model.named_steps.get("clf", self.base_model)
            else:
                clf = self.base_model
            # Use background sample of zeros for baseline
            background = np.zeros((1, len(self.feature_names)))
            self.explainer = shap.Explainer(clf, background)

    def analyze_url(self, url: str, top_k: int = 4):
        """
        Extracts features, computes risk score, runs SHAP attribution,
        and outputs top plain-English reasons for the verdict.
        """
        # 1. Feature extraction
        raw_feats = extract_features(url)
        df_feats = pd.DataFrame([raw_feats])[self.feature_names]

        # 2. Risk prediction (0 - 100%)
        prob = self.calibrated_model.predict_proba(df_feats)[0][1]
        risk_score = round(prob * 100, 2)

        if risk_score >= 70:
            verdict = "High Risk"
            verdict_desc = "Likely a phishing or malicious link."
        elif risk_score >= 35:
            verdict = "Medium Risk"
            verdict_desc = "Suspicious attributes found; exercise caution."
        else:
            verdict = "Low Risk"
            verdict_desc = "Appears structurally consistent with legitimate links."

        # 3. SHAP attribution computation
        shap_values = self.explainer(df_feats)
        
        # Extract SHAP array for positive class (phishing)
        if isinstance(shap_values.values, list):
            # In some scikit-learn tree models, values is a list [class_0, class_1]
            values = shap_values.values[1][0]
        elif len(shap_values.values.shape) == 3:
            # Shape is (samples, features, classes)
            values = shap_values.values[0, :, 1]
        else:
            values = shap_values.values[0]

        feature_val_series = df_feats.iloc[0]
        
        # Build explanation items
        explanations = []
        for feat_name, shap_val in zip(self.feature_names, values):
            explanations.append({
                "feature": feat_name,
                "value": feature_val_series[feat_name],
                "shap_value": float(shap_val),
                "description": FEATURE_DESCRIPTIONS.get(feat_name, feat_name)
            })

        # Sort features pushing the score toward phishing (highest positive SHAP values)
        phishing_reasons = sorted(
            [e for e in explanations if e["shap_value"] > 0],
            key=lambda x: x["shap_value"],
            reverse=True
        )[:top_k]

        # Features pushing score toward legitimate
        benign_reasons = sorted(
            [e for e in explanations if e["shap_value"] < 0],
            key=lambda x: x["shap_value"]
        )[:top_k]

        return {
            "url": url,
            "risk_score": risk_score,
            "verdict": verdict,
            "verdict_desc": verdict_desc,
            "phishing_reasons": phishing_reasons,
            "benign_reasons": benign_reasons,
            "all_shap": explanations,
            "raw_features": raw_feats
        }

if __name__ == "__main__":
    # Test on a malicious link and a benign link
    analyzer = PhishExplainer()
    
    test_urls = [
        "http://paypal-security.update-account.xyz/login",
        "https://www.google.com"
    ]
    
    for u in test_urls:
        res = analyzer.analyze_url(u)
        print("\n" + "=" * 60)
        print(f"URL: {res['url']}")
        print(f"Risk: {res['risk_score']}% ({res['verdict']})")
        print(f"Status: {res['verdict_desc']}")
        print("\nKey Contributing Risk Factors (SHAP Explanations):")
        if res["phishing_reasons"]:
            for r in res["phishing_reasons"]:
                print(f"  • {r['description']} (Impact: +{r['shap_value']:.3f})")
        else:
            print("  • No strong malicious indicators detected.")
        print("=" * 60)