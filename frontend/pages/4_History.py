import streamlit as st
import pandas as pd
from utils.auth import require_auth
from utils.api import get_portfolio_history
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Portfolio History — Vertex", page_icon="📜", layout="wide")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">ACID REVISION LOG</span>
            <span class="badge-chip badge-success">IMMUTABLE PORTFOLIO AUDIT</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">Portfolio Revision</span> History
        </h1>
        <p style="color: #475569; font-size: 0.95rem; margin: 0;">
            Track historical versions of your investment allocations, rebalancing events, and audit timestamps.
        </p>
    </div>
""", unsafe_allow_html=True)

with st.spinner("Loading portfolio revisions from PostgreSQL..."):
    res = get_portfolio_history()
    
if res.status_code == 200:
    data = res.json()
    if not data:
        st.info("You haven't generated any portfolios yet. Head to the Dashboard to create version 1.")
        st.page_link("pages/3_Dashboard.py", label="Open Dashboard →", icon="📊")
    else:
        df = pd.DataFrame(data)
        total_revisions = len(df)
        active_ver = df[df["is_active"] == True]["version"].values
        current_v = active_ver[0] if len(active_ver) > 0 else "None"
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
                <div class="vertex-card" style="padding: 16px;">
                    <div class="vertex-metric-label">Total Revisions</div>
                    <div class="vertex-metric-val">{total_revisions}</div>
                    <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">Versioned Generations</div>
                </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
                <div class="vertex-card" style="padding: 16px;">
                    <div class="vertex-metric-label">Active Version</div>
                    <div class="vertex-metric-val" style="color: #15803D;">v{current_v}</div>
                    <div style="font-size: 0.75rem; color: #15803D; margin-top: 2px;">Currently Live Model</div>
                </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
                <div class="vertex-card" style="padding: 16px;">
                    <div class="vertex-metric-label">Integrity Status</div>
                    <div style="margin: 6px 0 4px 0;"><span class="badge-chip badge-success">ACID AUDIT ENFORCED</span></div>
                    <div style="font-size: 0.75rem; color: #64748B;">Database Triggers Active</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<h3 style='margin-top: 20px; font-size: 1.25rem;'>Historical Version Log</h3>", unsafe_allow_html=True)
        df_display = df[["version", "model_name", "total_investment", "generated_at", "is_active"]].copy()
        df_display["is_active"] = df_display["is_active"].apply(lambda x: "🟢 Live Active" if x else "⚪ Superseded")
        df_display.columns = ["Version", "Model Name", "Allocated Capital (₹)", "Timestamp (UTC)", "Status"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.error(f"Failed to fetch portfolio history: {res.text}")
