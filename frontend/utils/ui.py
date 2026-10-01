import streamlit as st

def apply_page_style():
    """Injects Vertex's global design system: Google Fonts, Glassmorphism, and custom component CSS."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

        /* Global Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #F9FAFB;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }

        /* Gradient Text Accents */
        .vertex-gradient-text {
            background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }

        /* Glassmorphic Surface Cards */
        .vertex-card {
            background: rgba(17, 24, 39, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .vertex-card:hover {
            border-color: rgba(99, 102, 241, 0.35);
            transform: translateY(-2px);
        }

        /* Mini Metric Pill Cards */
        .vertex-metric-box {
            background: rgba(31, 41, 55, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
        }
        .vertex-metric-label {
            font-size: 0.82rem;
            color: #9CA3AF;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .vertex-metric-val {
            font-family: 'Outfit', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: #FFFFFF;
        }
        .vertex-metric-delta-pos {
            font-size: 0.85rem;
            color: #34D399;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .vertex-metric-delta-neg {
            font-size: 0.85rem;
            color: #F87171;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
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
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-warning {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-info {
            background: rgba(99, 102, 241, 0.15);
            color: #818CF8;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        /* Streamlit Input & Form Upgrades */
        .stTextInput input, .stNumberInput input, .stSelectbox select {
            background-color: rgba(17, 24, 39, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            color: #F9FAFB !important;
            padding: 10px 14px !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
        }

        /* Primary Button Glow */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.35) !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px 0 rgba(79, 70, 229, 0.5) !important;
        }

        /* Secondary Button */
        .stButton>button:not([kind="primary"]) {
            background: rgba(31, 41, 55, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            color: #E5E7EB !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:not([kind="primary"]):hover {
            border-color: #818CF8 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px) !important;
        }

        /* Tabs Polish */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 18px;
            font-weight: 600;
            color: #9CA3AF;
        }
        .stTabs [aria-selected="true"] {
            color: #818CF8 !important;
            border-bottom: 2px solid #818CF8 !important;
            background-color: rgba(99, 102, 241, 0.08) !important;
        }

        /* Glassmorphic Form & Bordered Container Upgrades */
        [data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background: rgba(17, 24, 39, 0.75) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0B0F19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }

        /* Custom Scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(11, 15, 25, 0.5);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.5);
        }
        </style>
    """, unsafe_allow_html=True)


def render_sidebar_brand():
    """Clean sidebar without persistent lakehouse widget (removed per user preference)."""
    pass

