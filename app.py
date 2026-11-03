import os
import sys
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Ensure Python discovers the src package
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.explain import PhishExplainer

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="PhishGuard AI | Explainable Scam Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- HIGH-END CYBERPUNK CSS -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Background glow effect */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0f172a 0%, #030712 100%);
        color: #f8fafc;
    }

    /* Glassmorphism Card Container */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }

    /* Badge styles */
    .badge-danger {
        background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
        color: #fff;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        letter-spacing: 0.05em;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
    }
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%);
        color: #fff;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
    }
    .badge-success {
        background: linear-gradient(135deg, #10b981 0%, #065f46 100%);
        color: #fff;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }

    /* Glowing header */
    .hero-title {
        font-weight: 800;
        font-size: 2.8rem;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    /* Reason bullet items */
    .reason-item-phish {
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        font-size: 0.95rem;
    }
    .reason-item-benign {
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- LOAD MODEL WITH CACHING -----------------
@st.cache_resource
def load_explainer():
    return PhishExplainer()

try:
    explainer = load_explainer()
except Exception as e:
    st.error(f"Failed to load model. Did you run `src/train.py`? Error: {e}")
    st.stop()

# ----------------- SIDEBAR CONTROLS & PRESETS -----------------
with st.sidebar:
    st.markdown("### ⚡ **Test Presets**")
    st.caption("Click any real-world attack pattern to auto-populate the detector:")

    presets = {
        "🎯 PayPal Phishing Kit": "http://paypal-security.update-account.xyz/login",
        "🌐 Fake Banking Multi-Subdomain": "http://chase.online.verify-security.account-update.buzz/auth",
        "👾 Direct IP Attack": "http://192.168.1.105/admin/login.php",
        "🔤 Punycode Spoofing": "http://xn--gogle-pra.com/verify-account",
        "✅ Clean Bench (Google)": "https://www.google.com/search?q=cybersecurity",
        "✅ Clean Bench (GitHub)": "https://github.com/explore"
    }

    selected_preset = st.selectbox("Choose a scenario:", list(presets.keys()))
    preset_url = presets[selected_preset]

    st.markdown("---")
    st.markdown("### 🔬 **Model Specs**")
    st.markdown("""
    - **Engine:** XGBoost Classifier
    - **Calibration:** Isotonic Regression
    - **Explainability:** SHAP TreeExplainer
    - **Features:** 25 Lexical Signals
    """)
    st.info("💡 **Tip:** PhishGuard is lexical-only. It inspects URL architecture without pinging the server.")

# ----------------- MAIN VIEW -----------------
st.markdown('<h1 class="hero-title">PhishGuard AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size:1.15rem; color:#94a3b8; margin-top:-5px;'>Explainable URL Security Engine Powered by Machine Learning & Game Theory</p>", unsafe_allow_html=True)

# Input Bar
col_in, col_btn = st.columns([5, 1])
with col_in:
    target_url = st.text_input(
        "Enter or paste any suspicious URL to analyze:",
        value=preset_url,
        placeholder="https://example-site.com/verify-credentials"
    )
with col_btn:
    st.write("")
    st.write("")
    scan_clicked = st.button("🚀 Analyze", use_container_width=True)

# Run Analysis
if target_url:
    with st.spinner("Extracting structural features and calculating Shapley attributions..."):
        result = explainer.analyze_url(target_url)

    score = result["risk_score"]
    verdict = result["verdict"]

    st.markdown("---")

    # ----------------- TOP METRIC & GAUGE SECTION -----------------
    c_left, c_right = st.columns([1, 1.2])

    with c_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### **Threat Assessment**")
        
        # Risk Badge
        if score >= 70:
            badge_html = f'<span class="badge-danger">🚨 {verdict.upper()}</span>'
            bar_color = "#ef4444"
        elif score >= 35:
            badge_html = f'<span class="badge-warning">⚠️ {verdict.upper()}</span>'
            bar_color = "#f59e0b"
        else:
            badge_html = f'<span class="badge-success">🛡️ {verdict.upper()}</span>'
            bar_color = "#10b981"

        st.markdown(badge_html, unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size: 3.5rem; margin: 10px 0; color:{bar_color}; font-weight:800;'>{score:.1f}%</h1>", unsafe_allow_html=True)
        st.write(f"**Status:** {result['verdict_desc']}")
        st.caption("Risk score represents an isotonic calibrated probability distribution, not a static blacklist check.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        # Plotly Speedometer Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'suffix': "%", 'font': {'color': "white", 'size': 32, 'family': 'Outfit'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                'bar': {'color': bar_color, 'thickness': 0.28},
                'bgcolor': "rgba(15, 23, 42, 0.4)",
                'borderwidth': 1,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.15)'},
                    {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
                ],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=240,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ----------------- EXPLAINABILITY BREAKDOWN -----------------
    st.markdown("### 🧠 **Explainable AI (XAI) Factor Breakdown**")
    st.markdown("<p style='color:#94a3b8;'>SHAP game-theory attributions isolating why the machine flagged this link:</p>", unsafe_allow_html=True)

    col_factors, col_chart = st.columns([1, 1.2])

    with col_factors:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("##### 🔍 **Dominant Risk Amplifiers**")
        if result["phishing_reasons"]:
            for item in result["phishing_reasons"]:
                st.markdown(
                    f'<div class="reason-item-phish">⚠️ <b>{item["description"]}</b><br>'
                    f'<small style="color:#fca5a5;">Feature: <code>{item["feature"]}={item["value"]}</code> (SHAP Impact: +{item["shap_value"]:.3f})</small></div>',
                    unsafe_allow_html=True
                )
        else:
            st.write("No strong malicious features detected.")

        if result["benign_reasons"]:
            st.markdown("<h5 style='margin-top: 15px;'>🛡️ <b>Trust Reinforcing Signals</b></h5>", unsafe_allow_html=True)
            for item in result["benign_reasons"][:2]:
                st.markdown(
                    f'<div class="reason-item-benign">✅ <b>{item["description"]}</b><br>'
                    f'<small style="color:#86efac;">Feature: <code>{item["feature"]}={item["value"]}</code> (SHAP Impact: {item["shap_value"]:.3f})</small></div>',
                    unsafe_allow_html=True
                )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart:
        # SHAP Horizontal Bar Chart
        top_shap_items = sorted(result["all_shap"], key=lambda x: abs(x["shap_value"]), reverse=True)[:8]
        top_shap_items.reverse()  # Ascending for clean horizontal display

        labels = [item["feature"] for item in top_shap_items]
        values = [item["shap_value"] for item in top_shap_items]
        colors = ["#ef4444" if v > 0 else "#10b981" for v in values]

        fig_bar = go.Figure(go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker_color=colors,
            text=[f"{v:+.3f}" for v in values],
            textposition="auto"
        ))
        fig_bar.update_layout(
            title="Feature Attribution Impact (SHAP Values)",
            title_font=dict(color="#f8fafc", size=14),
            xaxis_title="← Favors Legitimate | Favors Phishing →",
            xaxis=dict(gridcolor="#1e293b", color="#94a3b8"),
            yaxis=dict(gridcolor="#1e293b", color="#94a3b8"),
            paper_bgcolor='rgba(15, 23, 42, 0.4)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=340,
            margin=dict(l=10, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ----------------- RAW FEATURE INSPECTOR -----------------
    with st.expander("🛠️ Deep Inspection: Raw Extracted Feature Vector (25 dimensions)"):
        raw_df = pd.DataFrame(list(result["raw_features"].items()), columns=["Feature Signal", "Extracted Value"])
        st.dataframe(raw_df, use_container_width=True, height=260)

# Footer Disclaimer
st.markdown("---")
st.markdown(
    "<center><small style='color: #64748b;'>"
    "⚠️ <b>Security Notice:</b> PhishGuard estimates risk based on static lexical indicators. "
    "A low score is not a guarantee of security. Always verify the source before providing credentials."
    "</small></center>",
    unsafe_allow_html=True
)