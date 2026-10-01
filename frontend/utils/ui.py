import streamlit as st

def apply_page_style():
    """Injects Vertex's clean, high-contrast, pure Light Mode design system."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');

        :root {
            --bg-main: #F8FAFC;
            --sidebar-bg: #FFFFFF;
            --text-primary: #0F172A;
            --text-secondary: #475569;
            --text-muted: #64748B;
            --card-bg: #FFFFFF;
            --card-border: #E2E8F0;
            --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04);
            --metric-bg: #F8FAFC;
            --metric-border: #E2E8F0;
            --input-bg: #FFFFFF;
            --input-border: #CBD5E1;
            --primary-accent: #2563EB;
        }

        /* App Background & Typography */
        .stApp, html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-main) !important;
            color: var(--text-primary) !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
            color: var(--text-primary) !important;
        }

        p, span, label, div {
            color: var(--text-primary);
        }

        /* Corporate Gradient Text Accents */
        .vertex-gradient-text {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #2563EB 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }

        /* Surface Cards */
        .vertex-card {
            background: #FFFFFF;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 22px 24px;
            margin-bottom: 20px;
            box-shadow: var(--card-shadow);
        }

        /* Mini Metric Box */
        .vertex-metric-box {
            background: var(--metric-bg);
            border: 1px solid var(--metric-border);
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 12px;
        }
        .vertex-metric-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .vertex-metric-val {
            font-family: 'Outfit', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--text-primary);
        }
        .vertex-metric-delta-pos {
            font-size: 0.85rem;
            color: #15803D;
            font-weight: 600;
        }
        .vertex-metric-delta-neg {
            font-size: 0.85rem;
            color: #DC2626;
            font-weight: 600;
        }

        /* Status Badges */
        .badge-chip {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        .badge-success {
            background: #F0FDF4;
            color: #15803D;
            border: 1px solid #BBF7D0;
        }
        .badge-warning {
            background: #FFFBEB;
            color: #B45309;
            border: 1px solid #FDE68A;
        }
        .badge-info {
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
        }

        /* Inputs & Form Controls */
        .stTextInput input, .stSelectbox select, .stDateInput input {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            color: #0F172A !important;
            padding: 10px 14px !important;
            box-sizing: border-box !important;
        }
        .stNumberInput input {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            color: #0F172A !important;
            padding: 8px 10px !important;
            box-sizing: border-box !important;
            font-size: 0.95rem !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
        }

        /* Primary Button */
        .stButton>button[kind="primary"] {
            background: #2563EB !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
            transition: background-color 0.15s ease !important;
        }
        .stButton>button[kind="primary"]:hover {
            background: #1D4ED8 !important;
            color: #FFFFFF !important;
        }

        /* Secondary Button */
        .stButton>button:not([kind="primary"]) {
            background: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            color: #1E293B !important;
            font-weight: 500 !important;
        }
        .stButton>button:not([kind="primary"]):hover {
            background: #F1F5F9 !important;
            border-color: #94A3B8 !important;
        }

        /* Page Links as Action Buttons in Main */
        .main [data-testid="stPageLink-NavLink"] {
            background: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            padding: 6px 14px !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
            transition: all 0.15s ease !important;
            text-align: center !important;
            justify-content: center !important;
        }
        .main [data-testid="stPageLink-NavLink"]:hover {
            background: #F8FAFC !important;
            border-color: #2563EB !important;
        }
        .main [data-testid="stPageLink-NavLink"] a {
            color: #0F172A !important;
            font-weight: 600 !important;
            text-decoration: none !important;
        }
        .main [data-testid="stPageLink-NavLink"] span {
            color: #0F172A !important;
        }

        /* Neutralize all columns so they act purely as transparent layout grids */
        [data-testid="column"],
        [data-testid="column"] > div,
        [data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        /* Forms should have a single outer card border without internal child borders */
        [data-testid="stForm"] {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 24px !important;
            box-shadow: var(--card-shadow) !important;
        }
        [data-testid="stForm"] [data-testid="column"] > div,
        [data-testid="stForm"] div[data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        /* Sidebar Clean White Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        /* Completely eliminate rogue squares or boxes in sidebar */
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"],
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Sidebar Navigation links styling */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span {
            color: #1E293B !important;
            font-weight: 500 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover span {
            color: #2563EB !important;
        }

        /* Question Item Separator */
        .vertex-question-item {
            padding: 12px 14px;
            border-bottom: 1px solid #E2E8F0;
            margin-bottom: 8px;
        }
        .vertex-question-item:last-child {
            border-bottom: none;
        }

        /* Streamlit Dataframe / Table styling */
        [data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            background: #FFFFFF !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent;
            border-bottom: 1px solid #E2E8F0;
        }
        .stTabs [data-baseweb="tab"] {
            color: #64748B;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #2563EB !important;
            border-bottom: 2px solid #2563EB !important;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)


def render_sidebar_brand():
    """Empty brand function preserved for backwards compatibility."""
    pass
