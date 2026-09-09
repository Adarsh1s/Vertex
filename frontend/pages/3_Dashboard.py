import streamlit as st
import pandas as pd
from utils.auth import require_auth
from utils.api import get_profile, generate_portfolio, get_current_portfolio, get_portfolio_summary, get_expected_returns, get_alerts, get_rebalancing
from utils.charts import draw_allocation_pie

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
require_auth()

st.title("FinPulse Dashboard")

profile_res = get_profile()
if profile_res.status_code != 200:
    st.error("Please complete the Onboarding first.")
    st.stop()

profile_data = profile_res.json()
risk_score = profile_data.get("risk_score")
risk_profile_name = profile_data.get("risk_profile_name")

if not risk_score or not risk_profile_name:
    st.error("Please complete the Risk Questionnaire first.")
    st.stop()

col1, col2 = st.columns([2, 1])
with col1:
    st.info(f"**Risk Profile Badge**: {risk_profile_name} — Score: {risk_score}/100")
with col2:
    if st.button("Generate / Regenerate Portfolio", use_container_width=True):
        with st.spinner("Generating Portfolio..."):
            res = generate_portfolio()
            if res.status_code == 200:
                st.success("Portfolio generated successfully!")
            else:
                st.error(f"Failed to generate: {res.text}")

portfolio_res = get_current_portfolio()
if portfolio_res.status_code == 404:
    st.warning("No active portfolio found. Click 'Regenerate Portfolio' above to create one.")
    st.stop()
elif portfolio_res.status_code != 200:
    st.error(f"Error fetching portfolio: {portfolio_res.text}")
    st.stop()

portfolio_data = portfolio_res.json()
st.subheader(f"Active Model: {portfolio_data['model_name']} (v{portfolio_data['version']})")
st.write(f"Total Allocated Investment: ₹{portfolio_data['total_investment']:,.2f}")
st.write(f"Generated at: {portfolio_data['generated_at']}")

summary_res = get_portfolio_summary()
returns_res = get_expected_returns()
alerts_res = get_alerts()
rebalance_res = get_rebalancing()

if alerts_res.status_code == 200:
    alerts = alerts_res.json()
    if alerts:
        st.subheader("Pulse alerts")
        for alert in alerts:
            icon = "🔴" if alert["severity"] == "high" else "🟡"
            st.warning(f"{icon} **{alert['title']}** — {alert['message']}")

c1, c2 = st.columns([1, 1])

with c1:
    if summary_res.status_code == 200:
        fig = draw_allocation_pie(summary_res.json())
        st.plotly_chart(fig, use_container_width=True)

with c2:
    if returns_res.status_code == 200:
        returns_data = returns_res.json()
        st.markdown("### Expected Returns Estimate")
        st.write("Based on weighted averages of underlying instruments")
        m1, m2, m3 = st.columns(3)
        cols = [m1, m2, m3]
        for i, r in enumerate(returns_data):
            cols[i%3].metric(label=f"{r['period']} Return", value=f"{r['blended_return']:.2f}%")

st.subheader("Detailed Allocation")
df = pd.DataFrame(portfolio_data["positions"])
if not df.empty:
    df = df[["asset_class", "instrument_name", "ticker", "instrument_type", "allocation_percentage", "allocated_amount"]]
    df.columns = ["Asset Class", "Instrument", "Ticker", "Type", "Allocation (%)", "Amount (₹)"]
    st.dataframe(df, use_container_width=True)

if rebalance_res.status_code == 200:
    recommendations = rebalance_res.json()
    if recommendations:
        st.subheader("Rebalancing advisor")
        st.caption("A drift of 5 percentage points or more triggers an action.")
        st.dataframe(pd.DataFrame(recommendations), use_container_width=True)
