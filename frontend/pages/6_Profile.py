import streamlit as st
from utils.auth import require_auth
from utils.api import get_profile
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="My Profile — Vertex", page_icon="👤", layout="centered")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">USER ACCOUNT & PROFILE</span>
            <span class="badge-chip badge-success">3NF OLTP STORE</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">Investor Profile</span> Overview
        </h1>
        <p style="color: #475569; font-size: 0.95rem; margin: 0;">
            Review your financial baseline, risk classification, and investment parameters.
        </p>
    </div>
""", unsafe_allow_html=True)

with st.spinner("Loading profile from PostgreSQL..."):
    res = get_profile()
    
if res.status_code == 200:
    data = res.json()
    income = data.get('monthly_income', 0)
    expenses = data.get('monthly_expenses', 0)
    savings = max(0, income - expenses)
    savings_pct = round((savings / income * 100), 1) if income > 0 else 0
    score = data.get('risk_score')
    profile_name = data.get('risk_profile_name', 'Not Assessed')
    
    # Financial Baseline Card
    with st.container(border=True):
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="font-size: 1.2rem; margin: 0;">Financial Parameters</h3>
                <span class="badge-chip badge-info">app_users & user_profiles</span>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="vertex-metric-box">
                    <div class="vertex-metric-label">Monthly Gross Income</div>
                    <div class="vertex-metric-val">₹{income:,.2f}</div>
                </div>
                <div class="vertex-metric-box">
                    <div class="vertex-metric-label">Allocated Investment Capital</div>
                    <div class="vertex-metric-val">₹{data.get('investment_amount', 0):,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="vertex-metric-box">
                    <div class="vertex-metric-label">Monthly Living Expenses</div>
                    <div class="vertex-metric-val">₹{expenses:,.2f}</div>
                </div>
                <div class="vertex-metric-box">
                    <div class="vertex-metric-label">Net Monthly Savings Capacity</div>
                    <div class="vertex-metric-val" style="color: #15803D;">₹{savings:,.2f} ({savings_pct}%)</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"""
            <div style="margin-top: 12px; padding: 12px 16px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; display: flex; justify-content: space-between; font-size: 0.9rem; color: #1E293B;">
                <span><strong>Horizon:</strong> {data.get('investment_horizon_years', 0)} Years</span>
                <span><strong>Goal:</strong> {data.get('investment_goal', 'Wealth Creation')}</span>
            </div>
        """, unsafe_allow_html=True)
    
    # Risk Assessment Card
    st.markdown(f"""
        <div class="vertex-card" style="padding: 24px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="font-size: 1.2rem; margin: 0;">Risk Classification</h3>
                <span class="badge-chip badge-success">{profile_name}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 24px;">
                <div style="text-align: center; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 16px 24px;">
                    <div class="vertex-metric-label" style="color: #1D4ED8;">RISK SCORE</div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: #1E40AF;">
                        {score if score is not None else 'N/A'}<span style="font-size: 1rem; color: #64748B;"> / 100</span>
                    </div>
                </div>
                <div>
                    <div style="font-weight: 600; color: #0F172A; font-size: 1.05rem;">Assigned Model: {profile_name}</div>
                    <p style="color: #64748B; font-size: 0.85rem; margin: 4px 0 0 0;">
                        Determines the baseline target percentage for Equity, Debt, Gold, and Cash asset classes.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.page_link("pages/1_Onboarding.py", label="Edit Financial Details", icon="✏️", use_container_width=True)
    with col_b:
        st.page_link("pages/2_Questionnaire.py", label="Retake Risk Questionnaire", icon="📝", use_container_width=True)
else:
    st.warning("Financial profile not completed yet.")
    st.page_link("pages/1_Onboarding.py", label="Complete Onboarding Now →", icon="📝")
