import streamlit as st
from utils.auth import require_auth
from utils.api import get_profile, create_profile, update_profile
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Financial Onboarding — Vertex", page_icon="📝", layout="centered")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">STEP 1 OF 2</span>
            <span class="badge-chip badge-success">FINANCIAL PROFILE</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">Financial Baseline</span> Onboarding
        </h1>
        <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0;">
            Provide your monthly cashflow and capital parameters to configure your portfolio model.
        </p>
    </div>
""", unsafe_allow_html=True)

# check if profile exists
res = get_profile()
profile_exists = False
existing_data = {}

if res.status_code == 200:
    profile_exists = True
    existing_data = res.json()

st.markdown('<div class="vertex-card">', unsafe_allow_html=True)
st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 16px;'>Cashflow & Investment Parameters</h3>", unsafe_allow_html=True)

with st.form("onboarding_form"):
    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input(
            "Monthly Gross Income (₹)", 
            min_value=0.0, 
            value=float(existing_data.get("monthly_income", 100000.0)),
            step=5000.0,
            help="Total monthly in-hand earnings"
        )
        investment_amount = st.number_input(
            "Initial Investment Capital (₹)", 
            min_value=1000.0, 
            value=float(existing_data.get("investment_amount", 50000.0)),
            step=5000.0,
            help="Total amount allocated to your portfolio"
        )
    with col2:
        monthly_expenses = st.number_input(
            "Monthly Living Expenses (₹)", 
            min_value=0.0, 
            value=float(existing_data.get("monthly_expenses", 40000.0)),
            step=5000.0,
            help="Rent, bills, and standard monthly outflows"
        )
        horizon = st.number_input(
            "Investment Horizon (Years)", 
            min_value=1, max_value=50, 
            value=int(existing_data.get("investment_horizon_years", 5)),
            help="How long you plan to stay invested before major withdrawal"
        )
        
    goal = st.text_input(
        "Primary Investment Objective", 
        value=existing_data.get("investment_goal", "Long-Term Wealth Creation"),
        placeholder="e.g. Wealth Creation, Retirement, Education"
    )
    
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    submit_btn = st.form_submit_button("💾 Save Financial Profile", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

if submit_btn:
    payload = {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "investment_amount": investment_amount,
        "investment_horizon_years": horizon,
        "investment_goal": goal
    }
    
    with st.spinner("Persisting profile in PostgreSQL..."):
        if profile_exists:
            update_res = update_profile(payload)
            if update_res.status_code == 200:
                st.success("Financial profile updated successfully!")
                c_a, c_b = st.columns(2)
                with c_a:
                    if st.button("Proceed to Risk Questionnaire →", type="primary", use_container_width=True):
                        st.switch_page("pages/2_Questionnaire.py")
                with c_b:
                    if st.button("Go to Dashboard", use_container_width=True):
                        st.switch_page("pages/3_Dashboard.py")
            else:
                st.error(f"Failed to update profile: {update_res.text}")
        else:
            create_res = create_profile(payload)
            if create_res.status_code == 200:
                st.success("Financial profile created successfully! Now take the Risk Questionnaire.")
                if st.button("Continue to Step 2: Risk Questionnaire →", type="primary", use_container_width=True):
                    st.switch_page("pages/2_Questionnaire.py")
            else:
                st.error(f"Failed to create profile: {create_res.text}")
