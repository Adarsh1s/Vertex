import streamlit as st
from utils.auth import sign_in, sign_up, sign_out

st.set_page_config(page_title="FinPulse", page_icon="💓", layout="centered")

st.title("💓 FinPulse")
st.caption("Personal investment intelligence for better financial decisions")

if "token" in st.session_state:
    st.success("You are logged in!")
    user_name = st.session_state.get('user', {}).get('name', 'User')
    st.write(f"Welcome, {user_name}")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/3_Dashboard.py")
    if st.button("Sign Out"):
        sign_out()
        st.rerun()
else:
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    with tab1:
        st.header("Welcome Back")
        email = st.text_input("Email", key="si_email")
        password = st.text_input("Password", type="password", key="si_pw")
        if st.button("Sign In"):
            if not email or not password:
                st.error("Please provide both email and password")
            else:
                with st.spinner("Signing in..."):
                    result = sign_in(email, password)
                if "token" in result:
                    st.success("Logged in!")
                    st.rerun()
                elif "error" in result:
                    st.error(f"Login failed: {result['error']}")
                else:
                    st.error("Invalid credentials")

    with tab2:
        st.header("Create an Account")
        su_name = st.text_input("Full Name")
        su_email = st.text_input("Email", key="su_email")
        su_password = st.text_input("Password", type="password", key="su_pw")
        if st.button("Sign Up"):
            if not su_name or not su_email or not su_password:
                st.error("Please fill all fields")
            else:
                with st.spinner("Signing up..."):
                    result = sign_up(su_name, su_email, su_password)
                if "token" in result and "user" in result:
                    st.success("Account created successfully! Logging you in...")
                    st.rerun()
                elif "user" in result:
                    st.success("Account created! Please sign in using the Sign In tab.")
                elif "error" in result:
                    st.error(f"Sign up failed: {result['error']}")
                else:
                    st.error("Sign up failed for unknown reason")
