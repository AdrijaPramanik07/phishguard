import os
import sys
from urllib.parse import urlparse
import tldextract
import joblib
import numpy as np
import pandas as pd
import shap

# Ensure root directory is discoverable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.features import extract_features

def get_direction_aware_reason(feature: str, val: any, shap_val: float) -> str:
    """
    Produces dynamic, context-aware phrasing based on feature values
    and whether SHAP pulled the prediction toward Phishing or Safe.
    """
    is_phish = shap_val > 0

    if feature == "url_length":
        return f"Long URL structure ({val} characters) increased suspicion" if is_phish else f"Overall URL length ({val} chars) matches typical safe links"

    if feature == "hostname_length":
        return f"Host domain is unusually long ({val} characters)" if is_phish else f"Hostname length ({val} chars) is compact and standard"

    if feature == "subdomain_count":
        return f"Unusual multi-level subdomain nesting ({val} levels detected)" if is_phish else f"Single standard domain hierarchy without deceptive prefixes"

    if feature == "is_suspicious_tld":
        return "Uses an uncommon or high-abuse top-level domain" if is_phish else "Uses a standard top-level domain (.com, .org, etc.)"

    if feature == "is_trusted_domain":
        return "Unverified external domain (not on established trust index)" if is_phish else "Verified root domain matching recognized web infrastructure"

    if feature == "uses_https":
        return "Connection is unencrypted (plain HTTP)" if is_phish else "Connection uses standard HTTPS transport security"

    if feature == "keyword_count":
        return f"Contains {val} high-urgency credential/security keywords" if is_phish else "Does not contain urgent authentication keywords"

    if feature == "count_hyphens":
        return f"Multiple hyphens ({val}) in hostname, often used for spoofing" if is_phish else "Domain structure uses standard hyphenation"

    if feature == "count_dots":
        return f"High dot count ({val}) indicates potential subdomain spoofing" if is_phish else "Dot count is within normal range"

    if feature == "is_ip_address":
        return "Uses a direct numeric IP address instead of a domain name" if is_phish else "Uses a properly registered domain name"

    if feature == "hostname_entropy":
        return f"Domain name exhibits high character randomness ({val})" if is_phish else "Domain text conforms to readable natural language patterns"

    if feature == "count_at":
        return "Contains '@' symbol which can conceal the true destination host" if is_phish else "Standard URI formatting without delimiter spoofing"

    if feature == "is_punycode":
        return "Uses Punycode (xn--) encoding typical of homograph lookalike attacks" if is_phish else "Standard ASCII character set"

    # Default fallback
    return f"Feature '{feature}' ({val}) increased risk" if is_phish else f"Feature '{feature}' ({val}) favored legitimacy"


class PhishExplainer:
    def __init__(self, model_path="models/model.joblib"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Run src/train.py first.")

        saved_data = joblib.load(model_path)
        self.calibrated_model = saved_data["model"]
        self.base_model = saved_data["base_model"]
        self.feature_names = saved_data["feature_names"]

        try:
            self.explainer = shap.TreeExplainer(self.base_model)
        except Exception:
            if hasattr(self.base_model, "named_steps"):
                clf = self.base_model.named_steps.get("clf", self.base_model)
            else:
                clf = self.base_model
            background = np.zeros((1, len(self.feature_names)))
            self.explainer = shap.Explainer(clf, background)

    def analyze_url(self, raw_url: str):
        url = raw_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        # Parse anatomy
        parsed = urlparse(url)
        ext = tldextract.extract(url)

        scheme = parsed.scheme + "://"
        subdomain = ext.subdomain
        registered_domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
        path_query = (parsed.path or "") + ("?" + parsed.query if parsed.query else "")

        # Extract features and predict
        raw_feats = extract_features(url)
        df_feats = pd.DataFrame([raw_feats])[self.feature_names]

        raw_prob = float(self.calibrated_model.predict_proba(df_feats)[0][1])

        # Credibility fix: Clip probability to 1% - 99%
        clipped_score = round(np.clip(raw_prob * 100, 1.0, 99.0), 1)

        if clipped_score >= 70:
            verdict = "High Risk"
            verdict_desc = "Significant deceptive signals identified. High likelihood of credential theft or impersonation."
        elif clipped_score >= 35:
            verdict = "Medium Risk"
            verdict_desc = "Suspicious structural anomalies detected. Proceed with caution."
        else:
            verdict = "Low Risk"
            verdict_desc = "URL architecture aligns with standard legitimate properties."

        # Plain summary generation
        if ext.subdomain and any(brand in ext.subdomain.lower() for brand in ["paypal", "chase", "netflix", "google", "apple"]):
            plain_summary = f"This link uses '{ext.subdomain}' in its prefix, but the actual destination domain is '{registered_domain}'."
        elif raw_feats.get("is_ip_address", 0) == 1:
            plain_summary = f"This link routes directly to numeric IP '{registered_domain}' instead of an authenticated domain."
        elif clipped_score >= 70:
            plain_summary = f"Destination domain '{registered_domain}' displays typical credential harvesting traits."
        else:
            plain_summary = f"Destination domain '{registered_domain}' exhibits standard web naming structure."

        # SHAP calculation
        shap_values = self.explainer(df_feats)
        if isinstance(shap_values.values, list):
            values = shap_values.values[1][0]
        elif len(shap_values.values.shape) == 3:
            values = shap_values.values[0, :, 1]
        else:
            values = shap_values.values[0]

        total_abs_impact = float(np.sum(np.abs(values))) or 1.0
        feature_val_series = df_feats.iloc[0]

        explanations = []
        for feat_name, shap_val in zip(self.feature_names, values):
            val = feature_val_series[feat_name]
            # Convert raw log-odds into relative percentage impact
            impact_share = round((abs(float(shap_val)) / total_abs_impact) * 100, 1)
            explanations.append({
                "feature": feat_name,
                "value": val,
                "shap_value": float(shap_val),
                "impact_share": impact_share,
                "reason_text": get_direction_aware_reason(feat_name, val, float(shap_val))
            })

        # Top factors
        raised_risk = sorted([e for e in explanations if e["shap_value"] > 0], key=lambda x: x["impact_share"], reverse=True)[:4]
        lowered_risk = sorted([e for e in explanations if e["shap_value"] < 0], key=lambda x: x["impact_share"], reverse=True)[:4]

        return {
            "url": url,
            "anatomy": {
                "scheme": scheme,
                "subdomain": subdomain,
                "domain": registered_domain,
                "path": path_query if path_query else "/"
            },
            "risk_score": clipped_score,
            "verdict": verdict,
            "verdict_desc": verdict_desc,
            "plain_summary": plain_summary,
            "raised_risk": raised_risk,
            "lowered_risk": lowered_risk
        }