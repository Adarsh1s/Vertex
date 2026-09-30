import streamlit as st
import pandas as pd
from utils.auth import require_auth
from utils.api import (
    get_profile, 
    generate_portfolio, 
    get_current_portfolio, 
    get_portfolio_summary, 
    get_expected_returns, 
    get_alerts, 
    get_portfolio_drift
)
from utils.charts import draw_allocation_pie
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Dashboard & Telemetry — Vertex", page_icon="📊", layout="wide")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">REAL-TIME PORTFOLIO TELEMETRY</span>
            <span class="badge-chip badge-success">🟢 ENGINE SYNC ACTIVE</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">Portfolio Intelligence</span> & Live Valuation
        </h1>
        <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0;">
            Live multi-asset valuation, real-time drift telemetry, and risk-profile rebalancing.
        </p>
    </div>
""", unsafe_allow_html=True)

profile_res = get_profile()
if profile_res.status_code != 200:
    st.warning("⚠️ Please complete the Onboarding step to set up your financial profile.")
    if st.button("Complete Onboarding Now", type="primary"):
        st.switch_page("pages/1_Onboarding.py")
    st.stop()

profile_data = profile_res.json()
risk_score = profile_data.get("risk_score")
risk_profile_name = profile_data.get("risk_profile_name")

if not risk_score or not risk_profile_name:
    st.warning("⚠️ Please complete the Risk Questionnaire to determine your asset allocation model.")
    if st.button("Take Risk Questionnaire Now", type="primary"):
        st.switch_page("pages/2_Questionnaire.py")
    st.stop()

# Action & Profile Ribbon
col_prof, col_btn = st.columns([3, 1])
with col_prof:
    st.markdown(f"""
        <div class="vertex-metric-box" style="display: flex; align-items: center; justify-content: space-between; padding: 12px 20px;">
            <div>
                <span style="font-size: 0.8rem; color: #9CA3AF; font-weight: 600;">ACTIVE RISK PROFILE: </span>
                <strong style="color: #818CF8; font-family: 'Outfit', sans-serif; font-size: 1.05rem;">{risk_profile_name}</strong>
            </div>
            <div>
                <span style="font-size: 0.8rem; color: #9CA3AF; font-weight: 600;">SCORE: </span>
                <span class="badge-chip badge-info">{risk_score} / 100</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_btn:
    if st.button("⚡ Generate / Rebalance", use_container_width=True, type="primary"):
        with st.spinner("Executing ACID Portfolio Versioning Transaction..."):
            res = generate_portfolio()
            if res.status_code == 200:
                st.success("Portfolio generated successfully!")
                st.rerun()
            else:
                st.error(f"Failed to generate: {res.text}")

portfolio_res = get_current_portfolio()
if portfolio_res.status_code == 404:
    st.info("No active portfolio found. Click 'Generate / Rebalance' above to create your first portfolio.")
    st.stop()
elif portfolio_res.status_code != 200:
    st.error(f"Error fetching portfolio: {portfolio_res.text}")
    st.stop()

portfolio_data = portfolio_res.json()

# Live Market Revaluation & Drift Analytics
drift_res = get_portfolio_drift()
if drift_res.status_code == 200 and drift_res.json().get("has_portfolio"):
    drift_data = drift_res.json()
    total_orig = drift_data.get("total_original_investment", portfolio_data['total_investment'])
    total_live = drift_data.get("total_live_valuation", total_orig)
    gain_loss = drift_data.get("portfolio_gain_loss", 0.0)
    gain_loss_pct = drift_data.get("portfolio_gain_loss_pct", 0.0)
    needs_rebalance = drift_data.get("needs_rebalancing", False)

    # Top KPI Metrics Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class="vertex-card" style="padding: 18px 20px;">
                <div class="vertex-metric-label">Allocated Capital</div>
                <div class="vertex-metric-val">₹{total_orig:,.2f}</div>
                <div style="font-size: 0.78rem; color: #9CA3AF; margin-top: 4px;">Initial Portfolio Capital</div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        delta_class = "vertex-metric-delta-pos" if gain_loss >= 0 else "vertex-metric-delta-neg"
        delta_symbol = "▲ +" if gain_loss >= 0 else "▼ "
        st.markdown(f"""
            <div class="vertex-card" style="padding: 18px 20px;">
                <div class="vertex-metric-label">Live Market Valuation</div>
                <div class="vertex-metric-val">₹{total_live:,.2f}</div>
                <div class="{delta_class}" style="margin-top: 4px;">
                    {delta_symbol}₹{abs(gain_loss):,.2f} ({gain_loss_pct:+.2f}%)
                </div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="vertex-card" style="padding: 18px 20px;">
                <div class="vertex-metric-label">Active Model</div>
                <div class="vertex-metric-val" style="font-size: 1.35rem;">{portfolio_data['model_name']}</div>
                <div style="font-size: 0.78rem; color: #818CF8; margin-top: 4px;">Version {portfolio_data['version']} (ACID)</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        status_label = "NEEDS REBALANCE" if needs_rebalance else "BALANCED"
        status_badge = "badge-warning" if needs_rebalance else "badge-success"
        help_msg = "Deviation ≥ 5.0% detected" if needs_rebalance else "All asset classes within target"
        st.markdown(f"""
            <div class="vertex-card" style="padding: 18px 20px;">
                <div class="vertex-metric-label">Rebalancing Status</div>
                <div style="margin: 8px 0 6px 0;">
                    <span class="badge-chip {status_badge}" style="font-size: 0.9rem; padding: 6px 14px;">{status_label}</span>
                </div>
                <div style="font-size: 0.78rem; color: #9CA3AF;">{help_msg}</div>
            </div>
        """, unsafe_allow_html=True)

    # Drift Alerts Banner
    drift_alerts = drift_data.get("drift_alerts", [])
    if drift_alerts:
        st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 16px 20px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #FBBF24; margin-bottom: 8px;">
                    ⚠️ Real-Time Asset Allocation Drift Detected (≥ 5.0% Threshold)
                </div>
        """, unsafe_allow_html=True)
        for alert_msg in drift_alerts:
            st.markdown(f"<div style='font-size: 0.88rem; color: #E5E7EB; margin-left: 24px;'>• {alert_msg}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

summary_res = get_portfolio_summary()
returns_res = get_expected_returns()
alerts_res = get_alerts()

if alerts_res.status_code == 200:
    alerts = alerts_res.json()
    if alerts:
        with st.expander("🔔 System Intelligence Alerts"):
            for alert in alerts:
                icon = "🔴" if alert["severity"] == "high" else "🟡"
                st.write(f"{icon} **{alert['title']}** — {alert['message']}")

c1, c2 = st.columns([1, 1])

with c1:
    st.markdown('<div class="vertex-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 12px; font-size: 1.2rem;'>Target Asset Allocation</h3>", unsafe_allow_html=True)
    if summary_res.status_code == 200:
        fig = draw_allocation_pie(summary_res.json())
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="vertex-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 4px; font-size: 1.2rem;'>Blended Expected Returns</h3>", unsafe_allow_html=True)
    st.caption("Calculated via weighted average CTE over instrument historical returns")
    if returns_res.status_code == 200:
        returns_data = returns_res.json()
        m_cols = st.columns(len(returns_data))
        for i, r in enumerate(returns_data):
            with m_cols[i]:
                st.markdown(f"""
                    <div class="vertex-metric-box" style="text-align: center; padding: 18px 10px; margin-top: 14px;">
                        <div style="font-size: 0.8rem; color: #9CA3AF; font-weight: 600; text-transform: uppercase;">{r['period']} Horizon</div>
                        <div style="font-family: 'Outfit', sans-serif; font-size: 1.6rem; font-weight: 700; color: #34D399; margin-top: 4px;">
                            +{r['blended_return']:.2f}%
                        </div>
                        <div style="font-size: 0.72rem; color: #6B7280; margin-top: 2px;">Compounded Proj.</div>
                    </div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Asset Class Breakdown
st.markdown("<h3 style='margin-top: 20px; font-size: 1.25rem;'>Asset Class Allocation vs. Target Model</h3>", unsafe_allow_html=True)
if drift_res.status_code == 200 and drift_res.json().get("classes"):
    classes_df = pd.DataFrame(drift_res.json()["classes"])[[
        "asset_class", "original_amount", "live_value", "current_weight_pct", "target_weight_pct", "drift_pct", "drift_severity"
    ]].rename(columns={
        "asset_class": "Asset Class",
        "original_amount": "Invested (₹)",
        "live_value": "Live Value (₹)",
        "current_weight_pct": "Current Weight (%)",
        "target_weight_pct": "Target Model (%)",
        "drift_pct": "Drift (pts)",
        "drift_severity": "Severity"
    })
    st.dataframe(classes_df, use_container_width=True, hide_index=True)

# Detailed Instruments Table
st.markdown("<h3 style='margin-top: 24px; font-size: 1.25rem;'>Detailed Instrument Holdings</h3>", unsafe_allow_html=True)
df = pd.DataFrame(portfolio_data["positions"])
if not df.empty:
    df = df[["asset_class", "instrument_name", "ticker", "instrument_type", "allocation_percentage", "allocated_amount"]]
    df.columns = ["Asset Class", "Instrument Name", "Ticker", "Type", "Allocation (%)", "Invested Capital (₹)"]
    st.dataframe(df, use_container_width=True, hide_index=True)
