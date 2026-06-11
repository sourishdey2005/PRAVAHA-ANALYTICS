import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="PRAVAHA Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.db import init_db
from config.styles import inject_css, sidebar_logo, auth_css
from auth.auth_manager import is_authenticated, login, logout, current_user
from database.db import get_watchlists

# Initialize DB
init_db()
inject_css()

# ── Session defaults ───────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

def show_login():
    auth_css()
    st.markdown(
        """
        <style>
          section[data-testid="stSidebar"] { display: none !important; }
          section.main { margin-left: 0 !important; }
          .block-container { padding-top: 0 !important; padding-bottom: 0 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="auth-brand-lockup">
            <div class="auth-logo"></div>
            <div>
                <div class="auth-title">PRAVAHA Analytics</div>
                <div class="auth-subtitle">Signal Gateway</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="auth-content-grid">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        st.markdown(
            """
            <div style="padding:10px">
                <div style="font-size:0.95rem;color:#cbd5e1;margin-bottom:20px;line-height:1.6">
                    Enter your command center for market intelligence, causal signals,
                    forecasting labs, and portfolio impact analytics.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        features = [
            ("⚡ Lead-Lag Discovery", "Cross-asset timing & correlation shifts"),
            ("🧠 Causal Intelligence", "Statistical causality engines"),
            ("🤖 Forecast Lab", "ML models with SHAP explanations"),
            ("🕸️ Network Analytics", "Dependency graphs & relationships"),
        ]
        st.markdown('<div class="auth-feature-grid">', unsafe_allow_html=True)
        for icon, desc in features:
            st.markdown(f"""
            <div class="auth-feature">
                <strong>{icon}</strong>
                <span>{desc}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(
            """
            <div class="auth-side-panel">
                <div class="auth-side-panel-title">Live Intelligence Stack</div>
                <div class="auth-metric-row">
                    <div class="auth-metric"><b>50+</b><span>Chart Types</span></div>
                    <div class="auth-metric"><b>7</b><span>Model Families</span></div>
                    <div class="auth-metric"><b>24/7</b><span>Signal Access</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        st.markdown(
            """
            <div class="auth-card-header">
                <div>
                    <div class="auth-card-title">Welcome back</div>
                    <div class="auth-card-subtitle">Sign in to continue exploring market intelligence.</div>
                </div>
                <div class="auth-status-pill"><span class="auth-status-dot"></span>Secure</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tabs = st.tabs(["Sign In", "Create Account"])

        with tabs[0]:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username or Email", placeholder="demo")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                remember = st.checkbox("Remember this session")
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if submitted:
                    if username and password:
                        ok, user = login(username, password, remember)
                        if ok:
                            st.session_state['user'] = user
                            st.success(f"Welcome back, {user['full_name'] or user['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Try demo / demo123")
                    else:
                        st.warning("Please fill all fields.")

            st.markdown(
                """
                <div class="auth-demo">
                    <strong>Demo access:</strong> username <code>demo</code>, password <code>demo123</code>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
                
                full_name = st.text_input("Full Name", placeholder="e.g. Arjun Rao")
                email = st.text_input("Email", placeholder="analyst@example.com")
                username = st.text_input("Username", placeholder="unique username")
                password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
                password2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

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

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_sidebar():
    sidebar_logo()
    user = current_user()

    st.sidebar.markdown(f"""
    <div style="padding:16px 20px;margin:12px 16px;background:#151d35;border-radius:12px;border:1px solid #253452">
        <div style="font-weight:600;color:#e2e8f0;margin-bottom:4px">{user.get('full_name', user.get('username',''))}</div>
        <div style="font-size:0.8rem;color:#64748b">{user.get('email','')}</div>
    </div>
    """, unsafe_allow_html=True)

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
        active = st.session_state.get('page') == key
        style = "background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(0,212,255,0.2));border:1px solid rgba(0,212,255,0.2);" if active else ""
        if st.sidebar.button(f"{icon} {label}", key=f"nav_{key}",
                              use_container_width=True):
            st.session_state['page'] = key
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
    page = st.session_state.get('page', 'dashboard')

    if page == 'dashboard':
        from pages.dashboard import show
        show()
    elif page == 'market_overview':
        from pages.market_overview import show
        show()
    elif page == 'asset_explorer':
        from pages.asset_explorer import show
        show()
    elif page == 'lead_lag':
        from pages.lead_lag_page import show
        show()
    elif page == 'causal':
        from pages.causal_page import show
        show()
    elif page == 'forecast':
        from pages.forecast_page import show
        show()
    elif page == 'network':
        from pages.network_page import show
        show()
    elif page == 'visuals':
        from pages.visuals_page import show
        show()
    elif page == 'analytics_3d':
        from pages.analytics_3d import show
        show()
    elif page == 'portfolio':
        from pages.portfolio_page import show
        show()
    elif page == 'reports':
        from pages.reports_page import show
        show()
    elif page == 'watchlists':
        from pages.watchlists_page import show
        show()
    elif page == 'settings':
        from pages.settings_page import show
        show()

if __name__ == "__main__":
    main()