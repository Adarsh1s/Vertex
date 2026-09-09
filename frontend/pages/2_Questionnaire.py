import streamlit as st
from utils.auth import require_auth
from utils.api import submit_questionnaire

st.set_page_config(page_title="Risk Questionnaire", page_icon="📝")
require_auth()

st.title("Risk Tolerance Questionnaire")
st.write("Answer the following 7 questions to determine your risk profile.")

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
        "opts": ["Not secure at all", "Somewhat secure", "Very secure", "Extremely secure (e.g. Govt job/Tenured)"],
        "scores": [0, 5, 10, 14]
    },
    {
        "q": "7. Imagine a hypothetical investment where you can either gain 50% or lose 20%. Would you take it?",
        "opts": ["Never", "Maybe, with a small amount", "Probably, with a moderate amount", "Absolutely"],
        "scores": [0, 5, 8, 13]
    }
]


with st.form("questionnaire"):
    answers = []
    for idx, q_data in enumerate(questions):
        st.subheader(q_data["q"])
        ans = st.radio(f"Select one for Q{idx+1}", options=q_data["opts"], key=f"q_{idx}")
        answers.append((ans, q_data))
        
    submitted = st.form_submit_button("Submit Answers")
    
if submitted:
    answers_idx = [q["scores"][q["opts"].index(ans)] for ans, q in answers]
    with st.spinner("Calculating Risk Score..."):
        res = submit_questionnaire(answers_idx)
        if res.status_code == 200:
            data = res.json()
            st.success(f"Score calculated successfully: {data['risk_score']}/100")
            st.info("You're all set! Now you can generate your portfolio.")
        else:
            st.error(f"Failed to submit: {res.text}")
