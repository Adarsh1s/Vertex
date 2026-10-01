import datetime as dt
import pandas as pd
import streamlit as st

from utils.api import create_goal, get_goal_simulation, get_goals, get_health
from utils.auth import require_auth
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Goals & Health Score — Vertex", page_icon="🎯", layout="wide")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">PL/pgSQL HEALTH ENGINE</span>
            <span class="badge-chip badge-success">🟢 GEOMETRIC SIP SIMULATOR</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">Financial Goals</span> & Health Intelligence
        </h1>
        <p style="color: #9CA3AF; font-size: 0.95rem; margin: 0;">
            Multi-vector financial health assessment computed in PostgreSQL and geometric milestone projections.
        </p>
    </div>
""", unsafe_allow_html=True)

# Health Score Section
health_res = get_health()
if health_res.status_code == 200:
    health = health_res.json()
    score = health.get('score', 0)
    band = health.get('band', 'N/A')
    savings_rate = health.get('savings_rate_pct', 0)
    
    score_color = "#10B981" if score >= 75 else ("#F59E0B" if score >= 50 else "#EF4444")
    
    st.markdown(f"""
        <div class="vertex-card" style="padding: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; margin-bottom: 16px;">
                <div>
                    <div class="vertex-metric-label">VERTEX COMPOSITE HEALTH SCORE</div>
                    <div style="display: flex; align-items: baseline; gap: 8px;">
                        <span style="font-family: 'Outfit', sans-serif; font-size: 3rem; font-weight: 800; color: {score_color};">{score}</span>
                        <span style="font-size: 1.2rem; color: #9CA3AF; font-weight: 600;">/ 100</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="vertex-metric-label">RATING BAND</div>
                    <span class="badge-chip" style="background: rgba(99, 102, 241, 0.2); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.4); font-size: 1rem; padding: 6px 16px;">
                        {band.upper()}
                    </span>
                    <div style="font-size: 0.82rem; color: #9CA3AF; margin-top: 6px;">
                        Savings Rate: <strong style="color: #34D399;">{savings_rate}%</strong>
                    </div>
                </div>
            </div>
    """, unsafe_allow_html=True)
    
    st.progress(score / 100)
    st.caption("Evaluates 4 database vectors: 6-month historical savings rate, active asset diversification, goal funding coverage, and liquidity runway.")
    st.markdown("</div>", unsafe_allow_html=True)

# Two-Column Layout: Add Goal & Active Goals
col_new, col_sim = st.columns([1, 1])

with col_new:
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 16px;'>Create Financial Goal</h3>", unsafe_allow_html=True)
    with st.form("new_goal_form"):
        name = st.text_input("Goal Purpose", placeholder="e.g. Retirement Fund, Home Down Payment")
        c1, c2 = st.columns(2)
        with c1:
            target = st.number_input("Target Amount (₹)", min_value=1_000.0, value=1_000_000.0, step=25_000.0)
            rate = st.number_input("Expected Annual Return (%)", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
        with c2:
            current = st.number_input("Already Saved (₹)", min_value=0.0, value=50_000.0, step=10_000.0)
            target_date = st.date_input("Target Milestone Date", value=dt.date.today() + dt.timedelta(days=365 * 5), min_value=dt.date.today() + dt.timedelta(days=30))
        
        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("⚡ Add Goal Milestone", type="primary", use_container_width=True)
        
    if submitted:
        if not name:
            st.error("Please enter a goal name")
        else:
            response = create_goal({
                "goal_name": name, 
                "target_amount": target, 
                "current_amount": current,
                "target_date": target_date.isoformat(), 
                "expected_return_pct": rate
            })
            if response.status_code == 200:
                st.success("Financial goal created successfully!")
                st.rerun()
            else:
                st.error(f"Failed to create goal: {response.text}")

with col_sim:
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 4px;'>Active Goals & SIP Projections</h3>", unsafe_allow_html=True)
        st.caption("Geometric compounding model calculating monthly SIP requirements")
        
        goals_res = get_goals()
        if goals_res.status_code == 200 and goals_res.json():
            goals = goals_res.json()
            for goal in goals:
                simulation = get_goal_simulation(goal["goal_id"])
                if simulation.status_code == 200:
                    data = simulation.json()
                    st.markdown(f"""
                        <div class="vertex-metric-box" style="padding: 18px 20px; margin-top: 14px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <strong style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; color: #FFFFFF;">🎯 {data['goal_name']}</strong>
                                <span class="badge-chip badge-info">{data['months_remaining']} Months Left</span>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 12px;">
                                <div>
                                    <div style="font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;">Target Amount</div>
                                    <div style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: #E5E7EB;">₹{float(data['target_amount']):,.0f}</div>
                                </div>
                                <div>
                                    <div style="font-size: 0.72rem; color: #9CA3AF; text-transform: uppercase;">Already Saved</div>
                                    <div style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: #9CA3AF;">₹{float(data['current_amount']):,.0f}</div>
                                </div>
                                <div>
                                    <div style="font-size: 0.72rem; color: #34D399; text-transform: uppercase; font-weight: 600;">Monthly SIP</div>
                                    <div style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 800; color: #34D399;">₹{data['monthly_investment_needed']:,.0f}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No financial goals created yet. Use the form on the left to set your first milestone.")
