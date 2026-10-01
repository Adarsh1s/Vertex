import streamlit as st
import pandas as pd
from utils.auth import require_auth
from utils.api import compare_portfolio, get_risk_profiles
from utils.charts import draw_comparison_bar
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Compare Models — Vertex", page_icon="⚖️", layout="wide")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">SCENARIO MODELING</span>
            <span class="badge-chip badge-success">WHAT-IF ENGINE</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">What-If Model</span> Comparison
        </h1>
        <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0;">
            Compare different risk profiles and asset allocation models side-by-side.
        </p>
    </div>
""", unsafe_allow_html=True)

res_profiles = get_risk_profiles()
if res_profiles.status_code == 200:
    profiles = res_profiles.json()
    p_names = [p['profile_name'] for p in profiles]
    
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.15rem; margin-bottom: 14px;'>Select Models to Compare</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            model_1 = st.selectbox("Baseline Model", options=p_names, index=0)
        with col2:
            model_2 = st.selectbox("Alternative Comparison Model", options=p_names, index=min(2, len(p_names)-1))
            
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        compare_clicked = st.button("⚖️ Compare Allocations", type="primary", use_container_width=True)
        
    if compare_clicked or True: # Run on load or click
        with st.spinner("Fetching model templates from database..."):
            res1 = compare_portfolio(model_1)
            res2 = compare_portfolio(model_2)
            
            if res1.status_code == 200 and res2.status_code == 200:
                data1 = res1.json()
                data2 = res2.json()
                combined = data1 + data2
                
                col_chart, col_tbl = st.columns([3, 2])
                with col_chart:
                    with st.container(border=True):
                        st.markdown("<h3 style='font-size: 1.15rem; margin-bottom: 12px;'>Stacked Asset Class Weight (%)</h3>", unsafe_allow_html=True)
                        fig = draw_comparison_bar(combined)
                        st.plotly_chart(fig, use_container_width=True)
                    
                with col_tbl:
                    with st.container(border=True):
                        st.markdown("<h3 style='font-size: 1.15rem; margin-bottom: 12px;'>Side-by-Side Breakdown</h3>", unsafe_allow_html=True)
                        df = pd.DataFrame(combined)
                        if not df.empty:
                            df_pivot = df.pivot_table(index="asset_class", columns="model_name", values="allocation_percentage", aggfunc="sum").fillna(0)
                            st.dataframe(df_pivot.style.format("{:.1f}%"), use_container_width=True)
            else:
                st.error("Failed to load comparison data.")
else:
    st.error("Failed to load risk profiles.")
