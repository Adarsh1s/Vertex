import streamlit as st
import pandas as pd
from utils.auth import require_auth
from utils.api import get_portfolio_history

st.set_page_config(page_title="Portfolio History", page_icon="📜")
require_auth()

st.title("Portfolio History")

with st.spinner("Loading history..."):
    res = get_portfolio_history()
    
if res.status_code == 200:
    data = res.json()
    if not data:
        st.info("You haven't generated any portfolios yet.")
    else:
        df = pd.DataFrame(data)
        df = df[["version", "model_name", "total_investment", "generated_at", "is_active"]]
        df.columns = ["Version", "Model Name", "Total Investment (₹)", "Generated Date", "Active"]
        st.dataframe(df, use_container_width=True)
else:
    st.error(f"Failed to fetch history: {res.text}")
