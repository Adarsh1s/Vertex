import streamlit as st

def render_theme_toggle():
    """Renders a clean Light/Dark theme toggle in the sidebar."""
    current_theme = st.session_state.get("theme_mode", "dark")
    is_light = (current_theme == "light")
    
    with st.sidebar:
        # Subtle separator before appearance control
        st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.06); margin: 16px 0 12px 0;'></div>", unsafe_allow_html=True)
        toggle_val = st.toggle("☀️ Light Mode" if is_light else "🌙 Dark Mode", value=is_light, key="app_theme_toggle")
        if toggle_val != is_light:
            st.session_state["theme_mode"] = "light" if toggle_val else "dark"
            st.rerun()


def apply_page_style():
    """Injects Vertex's global design system with Dark/Light theme and zero layout distortion."""
    theme = st.session_state.get("theme_mode", "dark")
    is_light = (theme == "light")
    
    # Colors per theme
    if is_light:
        bg_main = "#F8FAFC"
        sidebar_bg = "#FFFFFF"
        text_primary = "#0F172A"
        text_secondary = "#64748B"
        text_muted = "#94A3B8"
        card_bg = "#FFFFFF"
        card_border = "rgba(0, 0, 0, 0.08)"
        card_shadow = "0 4px 20px 0 rgba(0, 0, 0, 0.05)"
        metric_bg = "#F1F5F9"
        metric_border = "rgba(0, 0, 0, 0.06)"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"
        badge_bg = "rgba(99, 102, 241, 0.1)"
        badge_color = "#4F46E5"
        badge_border = "rgba(99, 102, 241, 0.25)"
    else:
        bg_main = "#0B0F19"
        sidebar_bg = "#0F172A"
        text_primary = "#F9FAFB"
        text_secondary = "#9CA3AF"
        text_muted = "#6B7280"
        card_bg = "rgba(17, 24, 39, 0.75)"
        card_border = "rgba(255, 255, 255, 0.08)"
        card_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
        metric_bg = "rgba(31, 41, 55, 0.6)"
        metric_border = "rgba(255, 255, 255, 0.06)"
        input_bg = "rgba(17, 24, 39, 0.9)"
        input_border = "rgba(255, 255, 255, 0.12)"
        badge_bg = "rgba(99, 102, 241, 0.15)"
        badge_color = "#818CF8"
        badge_border = "rgba(99, 102, 241, 0.3)"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

        :root {{
            --bg-main: {bg_main};
            --sidebar-bg: {sidebar_bg};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --text-muted: {text_muted};
            --card-bg: {card_bg};
            --card-border: {card_border};
            --card-shadow: {card_shadow};
            --metric-bg: {metric_bg};
            --metric-border: {metric_border};
            --input-bg: {input_bg};
            --input-border: {input_border};
        }}

        /* App Background & Typography */
        .stApp, html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-main) !important;
            color: var(--text-primary) !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
            color: var(--text-primary) !important;
        }}

        p, span, label, div {{
            color: var(--text-primary);
        }}

        /* Gradient Text Accents */
        .vertex-gradient-text {{
            background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }}

        /* Cards */
        .vertex-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 22px 24px;
            margin-bottom: 20px;
            box-shadow: var(--card-shadow);
            transition: border-color 0.2s ease;
        }}

        /* Mini Metric Box */
        .vertex-metric-box {{
            background: var(--metric-bg);
            border: 1px solid var(--metric-border);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
        }}
        .vertex-metric-label {{
            font-size: 0.82rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .vertex-metric-val {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .vertex-metric-delta-pos {{
            font-size: 0.85rem;
            color: #10B981;
            font-weight: 600;
        }}
        .vertex-metric-delta-neg {{
            font-size: 0.85rem;
            color: #EF4444;
            font-weight: 600;
        }}

        /* Status Badges */
        .badge-chip {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}
        .badge-success {{
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .badge-warning {{
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        .badge-info {{
            background: {badge_bg};
            color: {badge_color};
            border: 1px solid {badge_border};
        }}

        /* Inputs & Form Controls */
        .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {{
            background-color: var(--input-bg) !important;
            border: 1px solid var(--input-border) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
            padding: 10px 14px !important;
            box-sizing: border-box !important;
        }}
        .stTextInput input:focus, .stNumberInput input:focus {{
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
        }}

        /* Buttons */
        .stButton>button[kind="primary"] {{
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.35) !important;
        }}
        .stButton>button:not([kind="primary"]) {{
            background: var(--metric-bg) !important;
            border: 1px solid var(--card-border) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
        }}

        /* Clean Native Streamlit Form Card */
        [data-testid="stForm"] {{
            background: var(--card-bg) !important;
            border: 1px solid var(--card-border) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: var(--card-shadow) !important;
        }}

        /* Main Content Bordered Containers - Clean single border */
        .main div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: var(--card-bg) !important;
            border: 1px solid var(--card-border) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: var(--card-shadow) !important;
        }}
        .main div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }}

        /* Sidebar Styling - Completely Clean */
        section[data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--card-border) !important;
        }}
        /* Strictly eliminate ANY rogue box or card under sidebar options */
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"],
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        /* Question Item Separator */
        .vertex-question-item {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 8px;
        }}
        .vertex-question-item:last-child {{
            border-bottom: none;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent;
            border-bottom: 1px solid var(--card-border);
        }}
        .stTabs [data-baseweb="tab"] {{
            color: var(--text-secondary);
        }}
        .stTabs [aria-selected="true"] {{
            color: #6366F1 !important;
            border-bottom: 2px solid #6366F1 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Render Theme toggle in the sidebar
    render_theme_toggle()


def render_sidebar_brand():
    """Empty brand function preserved for backwards compatibility."""
    pass
