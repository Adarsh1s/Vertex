import streamlit as st
from utils.auth import require_auth
from utils.api import get_profile

st.set_page_config(page_title="My Profile", page_icon="👤")
require_auth()

st.title("My Profile")

with st.spinner("Loading profile..."):
    res = get_profile()
    
if res.status_code == 200:
    data = res.json()
    st.write("### Financial Information")
    st.write(f"**Monthly Income:** ₹{data.get('monthly_income', 0):,.2f}")
    st.write(f"**Monthly Expenses:** ₹{data.get('monthly_expenses', 0):,.2f}")
    st.write(f"**Investment Amount:** ₹{data.get('investment_amount', 0):,.2f}")
    st.write(f"**Horizon:** {data.get('investment_horizon_years', 0)} years")
    st.write(f"**Goal:** {data.get('investment_goal', 'N/A')}")
    
    st.write("---")
    st.write("### Risk Assessment")
    score = data.get('risk_score')
    st.write(f"**Risk Score:** {score if score is not None else 'Not taken'}/100")
    st.write(f"**Risk Profile:** {data.get('risk_profile_name', 'N/A')}")
    
    if st.button("Edit Profile Details"):
        st.switch_page("pages/1_Onboarding.py")
    if st.button("Retake Risk Questionnaire"):
        st.switch_page("pages/2_Questionnaire.py")
else:
    st.warning("Profile not completed.")
    if st.button("Complete Onboarding Now"):
        st.switch_page("pages/1_Onboarding.py")
