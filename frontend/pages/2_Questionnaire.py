import streamlit as st
from utils.auth import require_auth
from utils.api import submit_questionnaire
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Risk Questionnaire — Vertex", page_icon="📝", layout="centered")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">STEP 2 OF 2</span>
            <span class="badge-chip badge-success">ASSET ALLOCATION CLASSIFIER</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">Risk Tolerance</span> Questionnaire
        </h1>
        <p style="color: #475569; font-size: 0.95rem; margin: 0;">
            Answer these 7 psychometric risk questions to map your profile to an asset allocation model.
        </p>
    </div>
""", unsafe_allow_html=True)

questions = [
    {
        "q": "1. What is your primary investment goal?",
        "opts": ["Capital preservation (Safest)", "Steady growth with regular income", "Capital appreciation", "Aggressive wealth creation"],
        "scores": [0, 5, 10, 15]
    },
    {
        "q": "2. How would you react if your portfolio lost 20% in a month?",
        "opts": ["Sell everything immediately", "Sell some investments", "Do nothing and wait", "Buy more at a discount"],
        "scores": [0, 4, 10, 15]
    },
    {
        "q": "3. What is your primary source of income?",
        "opts": ["Unstable / Freelance", "Retirement / Pension", "Stable Salary", "High Net Worth / Business"],
        "scores": [0, 5, 10, 15]
    },
    {
        "q": "4. How soon will you need to withdraw a significant portion of your investment?",
        "opts": ["Less than 1 year", "1-3 years", "3-7 years", "More than 7 years"],
        "scores": [0, 5, 10, 14]
    },
    {
        "q": "5. Which statement best describes your financial knowledge?",
        "opts": ["Novice: I keep my money in the bank", "Basic: I understand FDs and Gold", "Intermediate: I know about MFs and Stocks", "Advanced: I understand market cycles"],
        "scores": [0, 4, 10, 14]
    },
    {
        "q": "6. How secure is your current primary income?",
        "opts": ["Not secure at all", "Somewhat secure", "Very secure", "Extremely secure (Govt job / Established career)"],
        "scores": [0, 5, 10, 14]
    },
    {
        "q": "7. If an investment offers a potential 50% upside but with 20% drawdown risk, would you take it?",
        "opts": ["Never take risk", "Maybe with a tiny speculative amount", "Probably with moderate allocation", "Absolutely, maximize growth"],
        "scores": [0, 5, 8, 13]
    }
]

with st.form("questionnaire_form"):
    answers = []
    for idx, q_data in enumerate(questions):
        st.markdown(f"<div style='font-size: 1.05rem; font-weight: 700; margin-top: 14px; margin-bottom: 6px;'>{q_data['q']}</div>", unsafe_allow_html=True)
        ans = st.radio(f"Select option for question {idx+1}", options=q_data["opts"], key=f"q_{idx}", label_visibility="collapsed")
        answers.append((ans, q_data))
        if idx < len(questions) - 1:
            st.markdown("<div style='height: 1px; background: var(--card-border); margin: 14px 0;'></div>", unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("⚡ Submit Answers & Calculate Model", type="primary", use_container_width=True)
    
if submitted:
    answers_idx = [q["scores"][q["opts"].index(ans)] for ans, q in answers]
    with st.spinner("Classifying risk profile in PostgreSQL engine..."):
        res = submit_questionnaire(answers_idx)
        if res.status_code == 200:
            st.session_state["questionnaire_result"] = res.json()
            st.rerun()
        else:
            st.error(f"Failed to submit questionnaire: {res.text}")

if "questionnaire_result" in st.session_state:
    data = st.session_state["questionnaire_result"]
    score = data.get('risk_score', 0)
    profile_name = data.get('risk_profile_name', 'Moderate')
    
    st.markdown(f"""
        <div class="vertex-card" style="text-align: center; padding: 28px; border: 1px solid #BBF7D0; background: #F0FDF4; margin-top: 20px;">
            <div style="font-size: 0.82rem; color: #15803D; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">CALCULATED RISK SCORE</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 800; color: #15803D; margin: 4px 0;">{score} / 100</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">Assigned Model: <span style="color: #2563EB;">{profile_name}</span></div>
            <p style="color: #475569; font-size: 0.9rem; max-width: 480px; margin: 0 auto 16px auto;">Your risk score has been permanently linked to your profile in PostgreSQL. You can now generate your versioned investment portfolio.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.page_link("pages/3_Dashboard.py", label="🚀 Open Dashboard & Generate Portfolio →", icon="📊", use_container_width=True)
