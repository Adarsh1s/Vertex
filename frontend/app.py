import streamlit as st
from utils.auth import sign_in, sign_up, sign_out
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Vertex — Financial Lakehouse", page_icon="🔷", layout="centered")
apply_page_style()
render_sidebar_brand()

# Hero Header
st.markdown("""
    <div style="text-align: center; margin: 20px 0 32px 0;">
        <div style="display: inline-block; padding: 6px 16px; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; color: #1D4ED8; margin-bottom: 12px; letter-spacing: 0.05em;">
            🏛️ ADVANCED POSTGRESQL 16 LAKEHOUSE
        </div>
        <h1 style="font-size: 2.8rem; margin-bottom: 8px; font-weight: 800; letter-spacing: -0.03em;">
            <span class="vertex-gradient-text">VERTEX</span>
        </h1>
        <p style="font-size: 1.05rem; color: #475569; max-width: 540px; margin: 0 auto; line-height: 1.5;">
            Autonomous Multi-Tier Financial Lakehouse & Real-Time Portfolio Intelligence Engine
        </p>
    </div>
""", unsafe_allow_html=True)

if "token" in st.session_state:
    user_name = st.session_state.get('user', {}).get('name', 'User')
    user_email = st.session_state.get('user', {}).get('email', '')
    
    st.markdown(f"""
        <div class="vertex-card" style="text-align: center; padding: 32px 24px;">
            <div style="width: 56px; height: 56px; background: #2563EB; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; font-size: 1.6rem; color: #FFFFFF; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);">
                👤
            </div>
            <h2 style="margin-bottom: 4px; font-size: 1.5rem; color: #0F172A;">Welcome back, {user_name}!</h2>
            <div style="color: #64748B; font-size: 0.9rem; margin-bottom: 20px;">{user_email}</div>
            <div style="display: inline-block; padding: 4px 12px; background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 9999px; color: #15803D; font-size: 0.8rem; font-weight: 600;">
                🟢 Session Authenticated (HS256 Bearer JWT)
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/3_Dashboard.py", label="Open Dashboard", icon="📊", use_container_width=True)
    with col2:
        st.page_link("pages/7_Data_Hub.py", label="Data Hub", icon="🏛️", use_container_width=True)
    with col3:
        if st.button("Sign Out", use_container_width=True):
            sign_out()
            st.rerun()

else:
    # Feature Pillars Banner
    st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 28px;">
            <div class="vertex-metric-box" style="text-align: center; padding: 14px 10px;">
                <div style="font-size: 1.4rem; margin-bottom: 4px;">🕷️</div>
                <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary);">Stealth Crawler</div>
                <div style="font-size: 0.72rem; color: var(--text-secondary);">AMFI & NSE Live Feeds</div>
            </div>
            <div class="vertex-metric-box" style="text-align: center; padding: 14px 10px;">
                <div style="font-size: 1.4rem; margin-bottom: 4px;">🏛️</div>
                <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary);">3-Tier Lakehouse</div>
                <div style="font-size: 0.72rem; color: var(--text-secondary);">Bronze • Silver • Gold</div>
            </div>
            <div class="vertex-metric-box" style="text-align: center; padding: 14px 10px;">
                <div style="font-size: 1.4rem; margin-bottom: 4px;">⚡</div>
                <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary);">PL/pgSQL Engine</div>
                <div style="font-size: 0.72rem; color: var(--text-secondary);">In-Database Triggers</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_signin, tab_signup = st.tabs(["🔐 Sign In", "✨ Create Account"])

    with tab_signin:
        with st.container(border=True):
            st.markdown("<h3 style='margin-bottom: 16px; font-size: 1.25rem;'>Account Sign In</h3>", unsafe_allow_html=True)
            
            email = st.text_input("Email Address", key="si_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="si_pw", placeholder="••••••••")
            
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            if st.button("Sign In to Vertex", type="primary", use_container_width=True):
                if not email or not password:
                    st.error("Please provide both email and password")
                else:
                    with st.spinner("Authenticating credentials..."):
                        result = sign_in(email, password)
                    if "token" in result:
                        st.success("Authentication successful! Loading workspace...")
                        st.rerun()
                    elif "error" in result:
                        st.error(f"Login failed: {result['error']}")
                    else:
                        st.error("Invalid credentials")

    with tab_signup:
        with st.container(border=True):
            st.markdown("<h3 style='margin-bottom: 16px; font-size: 1.25rem;'>Create a New Account</h3>", unsafe_allow_html=True)
            
            su_name = st.text_input("Full Name", placeholder="e.g. Adarsh Singh")
            su_email = st.text_input("Email Address", key="su_email", placeholder="you@example.com")
            su_password = st.text_input("Password", type="password", key="su_pw", placeholder="At least 8 characters")
            
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            if st.button("Register & Create Account", type="primary", use_container_width=True):
                if not su_name or not su_email or not su_password:
                    st.error("Please fill in all fields")
                elif len(su_password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    with st.spinner("Creating account & generating cryptographic salt..."):
                        result = sign_up(su_name, su_email, su_password)
                    if "token" in result and "user" in result:
                        st.success("Account created successfully! Logging you in...")
                        st.rerun()
                    elif "error" in result:
                        st.error(f"Registration failed: {result['error']}")
                    else:
                        st.error("Registration failed. Please try again.")
