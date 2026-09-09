import streamlit as st
from utils.auth import require_auth
from utils.api import get_profile, create_profile, update_profile

st.set_page_config(page_title="Onboarding", page_icon="📝")
require_auth()

st.title("Financial Profile Onboarding")

# check if profile exists
res = get_profile()
profile_exists = False
existing_data = {}

if res.status_code == 200:
    profile_exists = True
    existing_data = res.json()

with st.form("onboarding_form"):
    st.subheader("Your Financial Details")
    
    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Monthly Income (₹)", 
                                         min_value=0.0, 
                                         value=float(existing_data.get("monthly_income", 100000.0)),
                                         step=5000.0)
        investment_amount = st.number_input("One-time Investment Amount (₹)", 
                                            min_value=1000.0, 
                                            value=float(existing_data.get("investment_amount", 50000.0)),
                                            step=5000.0)
    with col2:
        monthly_expenses = st.number_input("Monthly Expenses (₹)", 
                                           min_value=0.0, 
                                           value=float(existing_data.get("monthly_expenses", 40000.0)),
                                           step=5000.0)
        horizon = st.number_input("Investment Horizon (Years)", 
                                  min_value=1, max_value=50, 
                                  value=int(existing_data.get("investment_horizon_years", 5)))
        
    goal = st.text_input("Primary Investment Goal", value=existing_data.get("investment_goal", "Wealth Creation"))
    
    submit_btn = st.form_submit_button("Save Profile")

if submit_btn:
    payload = {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "investment_amount": investment_amount,
        "investment_horizon_years": horizon,
        "investment_goal": goal
    }
    
    with st.spinner("Saving..."):
        if profile_exists:
            update_res = update_profile(payload)
            if update_res.status_code == 200:
                st.success("Profile updated successfully!")
                st.info("You might want to retake the Questionnaire or Regenerate your Portfolio.")
            else:
                st.error(f"Failed to update: {update_res.text}")
        else:
            create_res = create_profile(payload)
            if create_res.status_code == 200:
                st.success("Profile created! Please proceed to the Risk Questionnaire.")
            else:
                st.error(f"Failed to create: {create_res.text}")
