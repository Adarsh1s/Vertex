import streamlit as st
import pandas as pd
from utils.auth import require_auth
from utils.api import compare_portfolio, get_risk_profiles
from utils.charts import draw_comparison_bar

st.set_page_config(page_title="Compare Models", page_icon="⚖️", layout="wide")
require_auth()

st.title("What-if Comparison")
st.write("Compare different risk models side-by-side.")

res_profiles = get_risk_profiles()
if res_profiles.status_code == 200:
    profiles = res_profiles.json()
    p_names = [p['profile_name'] for p in profiles]
    
    col1, col2 = st.columns(2)
    with col1:
        model_1 = st.selectbox("Select Model 1", options=p_names, index=0)
    with col2:
        model_2 = st.selectbox("Select Model 2", options=p_names, index=min(3, len(p_names)-1))
        
    if st.button("Compare"):
        with st.spinner("Fetching data..."):
            res1 = compare_portfolio(model_1)
            res2 = compare_portfolio(model_2)
            
            if res1.status_code == 200 and res2.status_code == 200:
                data1 = res1.json()
                data2 = res2.json()
                
                combined = data1 + data2
                fig = draw_comparison_bar(combined)
                st.plotly_chart(fig, use_container_width=True)
                
                df = pd.DataFrame(combined)
                if not df.empty:
                    df = df.pivot_table(index="asset_class", columns="model_name", values="allocation_percentage", aggfunc="sum").fillna(0)
                    st.dataframe(df.style.format("{:.2f}%"))
            else:
                st.error("Failed to load comparison data.")
else:
    st.error("Failed to load risk profiles.")
