import datetime as dt
import pandas as pd
import streamlit as st

from utils.api import create_goal, get_goal_simulation, get_goals, get_health
from utils.auth import require_auth

st.set_page_config(page_title="FinPulse Goals", page_icon="🎯", layout="wide")
require_auth()

st.title("Goals & Financial Health")
health_res = get_health()
if health_res.status_code == 200:
    health = health_res.json()
    col1, col2 = st.columns(2)
    col1.metric("FinPulse Health Score", f"{health['score']} / 100", health["band"])
    col2.metric("Latest savings rate", f"{health['savings_rate_pct']}%")
    st.progress(health["score"] / 100)
    st.caption("Score combines diversification, savings habit, goal progress, and financial readiness.")

with st.form("new_goal"):
    st.subheader("Create a financial goal")
    name = st.text_input("Goal", placeholder="Home down payment")
    c1, c2, c3 = st.columns(3)
    target = c1.number_input("Target amount (₹)", min_value=1_000.0, value=1_000_000.0, step=10_000.0)
    current = c2.number_input("Already saved (₹)", min_value=0.0, value=0.0, step=10_000.0)
    rate = c3.number_input("Expected annual return (%)", min_value=0.0, max_value=30.0, value=8.0)
    target_date = st.date_input("Target date", value=dt.date.today() + dt.timedelta(days=365 * 5), min_value=dt.date.today() + dt.timedelta(days=1))
    submitted = st.form_submit_button("Add goal")
if submitted:
    response = create_goal({"goal_name": name, "target_amount": target, "current_amount": current,
                            "target_date": target_date.isoformat(), "expected_return_pct": rate})
    if response.status_code == 200:
        st.success("Goal added.")
        st.rerun()
    else:
        st.error(response.text)

goals_res = get_goals()
st.subheader("Goal simulator")
if goals_res.status_code == 200 and goals_res.json():
    goals = goals_res.json()
    for goal in goals:
        simulation = get_goal_simulation(goal["goal_id"])
        if simulation.status_code == 200:
            data = simulation.json()
            with st.container(border=True):
                st.markdown(f"### {data['goal_name']}")
                a, b, c = st.columns(3)
                a.metric("Target", f"₹{float(data['target_amount']):,.0f}")
                b.metric("Time remaining", f"{data['months_remaining']} months")
                c.metric("Invest each month", f"₹{data['monthly_investment_needed']:,.0f}")
else:
    st.info("Create your first goal to see a personalized monthly investment plan.")
