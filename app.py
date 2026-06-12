import os
import textwrap
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="PRAVAHA Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from auth.auth_manager import current_user, is_authenticated, login, logout
from config.styles import auth_css, inject_css, sidebar_logo
from database.db import init_db


init_db()
inject_css()

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"


def show_login():
    auth_css()
    st.markdown(
        """
        <style>
          html, body { overflow: auto !important; }
          [data-testid="stMain"] { padding-top: 0 !important; }
          [data-testid="stAppViewContainer"] .main .block-container { padding-top: 0 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="auth-shell">
          <div class="auth-page">
            <div class="auth-header-center">
              <div class="auth-hero-badge"><span class="auth-hero-dot"></span>PRAVAHA Analytics Command Center</div>
              <div class="auth-brand-line">PRAVAHA<span>Market Intelligence Platform</span></div>
              <div class="auth-hero-copy">
                Analyze market structure, trace causal relationships, and translate signals into decisions with a clean workspace built for modern research teams.
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="auth-landing-grid">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.08, 0.92], gap="small")

    with col1:
        features = [
            ("Signals", "Lead-Lag Discovery", "Spot timing shifts across instruments and regimes."),
            ("Causal", "Causal Intelligence", "Trace relationships beyond simple correlation."),
            ("Forecast", "Forecast Lab", "Test models with transparent, explainable outputs."),
            ("Network", "Dependency Maps", "See how assets, sectors, and drivers connect."),
        ]

        features_html = "".join(
            textwrap.dedent(
                f"""
                <div class="auth-feature">
                    <strong>{title}</strong>
                    <span>{desc}</span>
                </div>
                """
            ).strip()
            for _, title, desc in features
        )

        left_panel_html = textwrap.dedent(f"""
            <div class="auth-left-panel">
                <div class="auth-logo-section">
                    <div class="auth-logo-icon">PA</div>
                    <div>
                        <div class="auth-logo-text">PRAVAHA</div>
                        <div class="auth-logo-subtitle">Market Intelligence Platform</div>
                    </div>
                </div>
                <div class="auth-intro">
                    A premium workspace for analysts who need a sharper landing point, faster context, and a more focused route into market research.
                </div>
                <div class="auth-mini-list">
                    <div class="auth-mini-item">
                        <div class="auth-mini-icon">01</div>
                        <div><strong>Decision-ready views</strong><span>See what moved, why it moved, and what to watch next.</span></div>
                    </div>
                    <div class="auth-mini-item">
                        <div class="auth-mini-icon">02</div>
                        <div><strong>Built for analysts</strong><span>Keep signal context, model outputs, and portfolio impact aligned.</span></div>
                    </div>
                </div>
                <div class="auth-feature-grid">
                    {features_html}
                </div>
                <div class="auth-side-panel">
                    <div class="auth-side-panel-title">Live Intelligence Stack</div>
                    <div class="auth-metric-row">
                        <div class="auth-metric"><b>50+</b><span>Chart Types</span></div>
                        <div class="auth-metric"><b>7</b><span>Model Families</span></div>
                        <div class="auth-metric"><b>24/7</b><span>Signal Access</span></div>
                    </div>
                </div>
            </div>
        """).strip()
        st.markdown(left_panel_html, unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="auth-card">
              <div class="auth-card-header">
                <div>
                  <div class="auth-card-title">Welcome back</div>
                  <div class="auth-card-subtitle">Sign in to continue your market research session.</div>
                </div>
                <div class="auth-status-pill"><span class="auth-status-dot"></span>Secure access</div>
              </div>
              <div class="auth-form-note">Use your workspace credentials. Demo access is available with <code>demo / demo123</code>.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tabs = st.tabs(["Sign In", "Create Account"])

        with tabs[0]:
            with st.form("login_form", clear_on_submit=False):
                st.markdown('<div class="auth-form-shell">', unsafe_allow_html=True)
                username = st.text_input("Username or Email", placeholder="demo")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                remember = st.checkbox("Remember this session")
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if submitted:
                if username and password:
                    ok, user = login(username, password, remember)
                    if ok:
                        st.session_state["user"] = user
                        st.success(f"Welcome back, {user['full_name'] or user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Try demo / demo123")
                else:
                    st.warning("Please fill all fields.")

        with tabs[1]:
            with st.form("reg_form", clear_on_submit=False):
                st.markdown(
                    """
                    <div style="margin-bottom:10px">
                        <div class="auth-card-title">Create your workspace</div>
                        <div class="auth-card-subtitle">Set up a new analyst profile for PRAVAHA Analytics.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="auth-form-shell">', unsafe_allow_html=True)
                full_name = st.text_input("Full Name", placeholder="e.g. Arjun Rao")
                email = st.text_input("Email", placeholder="analyst@example.com")
                username = st.text_input("Username", placeholder="unique username")
                password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
                password2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                if submitted:
                    from database.db import create_user

                    if not all([full_name, email, username, password]):
                        st.warning("Please fill all fields.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif password != password2:
                        st.error("Passwords don't match.")
                    else:
                        ok, msg = create_user(username, email, password, full_name)
                        if ok:
                            st.success("Account created. Switch to Sign In to continue.")
                        else:
                            st.error(f"Error: {msg}")

    st.markdown("</div>", unsafe_allow_html=True)


def show_sidebar():
    sidebar_logo()
    user = current_user()

    st.sidebar.markdown(
        f"""
    <div style="padding:16px 20px;margin:12px 16px;background:#151d35;border-radius:12px;border:1px solid #253452">
        <div style="font-weight:600;color:#e2e8f0;margin-bottom:4px">{user.get('full_name', user.get('username',''))}</div>
        <div style="font-size:0.8rem;color:#64748b">{user.get('email','')}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    pages = [
        ("🏠", "Dashboard", "dashboard"),
        ("🌍", "Market Overview", "market_overview"),
        ("🔍", "Asset Explorer", "asset_explorer"),
        ("⚡", "Lead-Lag Discovery", "lead_lag"),
        ("🧠", "Causal Intelligence", "causal"),
        ("🤖", "Forecast Lab", "forecast"),
        ("🕸️", "Dependency Network", "network"),
        ("📊", "Visual Analytics", "visuals"),
        ("🌐", "3D Analytics", "analytics_3d"),
        ("💼", "Portfolio Impact", "portfolio"),
        ("📋", "Reports", "reports"),
        ("⭐", "Watchlists", "watchlists"),
        ("⚙️", "Settings", "settings"),
    ]

    st.sidebar.markdown("**NAVIGATION**")
    for icon, label, key in pages:
        if st.sidebar.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state["page"] = key
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        logout()
        st.rerun()


def main():
    if not is_authenticated():
        show_login()
        return

    show_sidebar()
    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        from pages.dashboard import show

        show()
    elif page == "market_overview":
        from pages.market_overview import show

        show()
    elif page == "asset_explorer":
        from pages.asset_explorer import show

        show()
    elif page == "lead_lag":
        from pages.lead_lag_page import show

        show()
    elif page == "causal":
        from pages.causal_page import show

        show()
    elif page == "forecast":
        from pages.forecast_page import show

        show()
    elif page == "network":
        from pages.network_page import show

        show()
    elif page == "visuals":
        from pages.visuals_page import show

        show()
    elif page == "analytics_3d":
        from pages.analytics_3d import show

        show()
    elif page == "portfolio":
        from pages.portfolio_page import show

        show()
    elif page == "reports":
        from pages.reports_page import show

        show()
    elif page == "watchlists":
        from pages.watchlists_page import show

        show()
    elif page == "settings":
        from pages.settings_page import show

        show()


if __name__ == "__main__":
    main()
