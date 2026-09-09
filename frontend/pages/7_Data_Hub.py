import pandas as pd
import streamlit as st

from utils.api import get_imports, import_transactions
from utils.auth import require_auth

st.set_page_config(page_title="FinPulse Data Hub", page_icon="🗂️", layout="wide")
require_auth()

st.title("FinPulse Data Hub")
st.caption("Import a bank or transaction CSV. FinPulse preserves source rows, validates them, removes duplicates, categorizes spending, and refreshes monthly analytics.")

with st.expander("CSV format"):
    st.code("date,description,amount\n2026-09-01,Salary,95000\n2026-09-02,Swiggy,-420")
    st.write("Accepted aliases: `transaction date`, `narration`, `merchant`, and `details`. Positive amounts are income; negative amounts are expenses.")

uploaded = st.file_uploader("Bank / transaction export", type=["csv"])
if uploaded and st.button("Run ETL import", type="primary"):
    with st.spinner("Landing, validating, and loading transaction data..."):
        response = import_transactions(uploaded)
    if response.status_code == 200:
        data = response.json()
        st.success(data["message"])
        a, b, c = st.columns(3)
        a.metric("Loaded", data["accepted_rows"])
        b.metric("Rejected", data["rejected_rows"])
        c.metric("Duplicates skipped", data["duplicate_rows"])
    else:
        st.error(response.text)

imports = get_imports()
st.subheader("Data lake import history")
if imports.status_code == 200 and imports.json():
    st.dataframe(pd.DataFrame(imports.json()), use_container_width=True, hide_index=True)
else:
    st.info("No files imported yet.")
