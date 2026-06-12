import streamlit as st
from config.styles import inject_css, page_header
from auth.auth_manager import current_user
from database.db import get_settings, update_settings, log_audit

def show():
    inject_css()
    page_header("Settings", "Customize your PRAVAHA experience", "⚙️")

    user = current_user()
    settings = get_settings(user['id'])

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🎨 Preferences", "🔒 Security"])

    with tab1:
        st.markdown("#### User Profile")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div style="background:#151d35;border:1px solid #253452;border-radius:50%;
            width:80px;height:80px;display:flex;align-items:center;justify-content:center;
            font-size:2rem;font-weight:700;color:#00d4ff;margin:0 auto 16px">
                {user.get('username','?')[0].upper()}
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Username:** {user.get('username','')}")
            st.markdown(f"**Email:** {user.get('email','')}")
            st.markdown(f"**Role:** {user.get('role','user').title()}")
            st.markdown(f"**Last Login:** {user.get('last_login','N/A')}")

        st.markdown("---")
        st.markdown("#### Update Profile")
        with st.form("profile_form"):
            new_name = st.text_input("Full Name", value=user.get('full_name',''))
            new_email = st.text_input("Email", value=user.get('email',''))
            if st.form_submit_button("Save Profile", use_container_width=True):
                from database.db import get_conn
                conn = get_conn()
                conn.execute("UPDATE users SET full_name=?, email=? WHERE id=?",
                             (new_name, new_email, user['id']))
                conn.commit()
                conn.close()
                st.session_state['user']['full_name'] = new_name
                st.session_state['user']['email'] = new_email
                log_audit(user['id'], 'profile_update')
                st.success("Profile updated!")

    with tab2:
        st.markdown("#### Preferences")
        with st.form("pref_form"):
            col1, col2 = st.columns(2)
            with col1:
                default_exchange = st.selectbox("Default Exchange",
                    ["NSE","BSE","NYSE","NASDAQ","ALL"],
                    index=["NSE","BSE","NYSE","NASDAQ","ALL"].index(settings.get('default_exchange','NSE')))
                default_period = st.selectbox("Default Period",
                    ["1mo","3mo","6mo","1y","2y","3y"],
                    index=["1mo","3mo","6mo","1y","2y","3y"].index(settings.get('default_period','1y')))
            with col2:
                notifs = st.toggle("Enable Notifications", value=bool(settings.get('notifications', 1)))
                theme = st.selectbox("Theme", ["dark","light"], index=0)

            if st.form_submit_button("Save Preferences", use_container_width=True):
                update_settings(user['id'],
                    default_exchange=default_exchange,
                    default_period=default_period,
                    notifications=int(notifs),
                    theme=theme)
                log_audit(user['id'], 'settings_update')
                st.success("Preferences saved!")

        st.markdown("---")
        st.markdown("#### Keyboard Shortcuts")
        shortcuts = [
            ("Ctrl+D", "Go to Dashboard"),
            ("Ctrl+M", "Market Overview"),
            ("Ctrl+L", "Lead-Lag Discovery"),
            ("Ctrl+F", "Forecast Lab"),
            ("Ctrl+N", "Dependency Network"),
            ("Ctrl+R", "Reports"),
        ]
        for k, v in shortcuts:
            col1, col2 = st.columns(2)
            col1.markdown(f'<span class="badge badge-blue mono">{k}</span>', unsafe_allow_html=True)
            col2.write(v)

    with tab3:
        st.markdown("#### Change Password")
        with st.form("pwd_form"):
            current_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Change Password", use_container_width=True):
                from auth.auth_manager import verify_password
                from database.db import get_conn
                import bcrypt
                if not verify_password(user['username'], current_pwd):
                    st.error("Current password is incorrect.")
                elif new_pwd != confirm_pwd:
                    st.error("New passwords don't match.")
                elif len(new_pwd) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    new_hash = bcrypt.hashpw(new_pwd.encode(), bcrypt.gensalt()).decode()
                    conn = get_conn()
                    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (new_hash, user['id']))
                    conn.commit()
                    conn.close()
                    log_audit(user['id'], 'password_change')
                    st.success("Password changed successfully!")

        st.markdown("---")
        st.markdown("#### Audit Log")
        from database.db import get_conn
        conn = get_conn()
        logs = conn.execute(
            "SELECT action, details, created_at FROM audit_logs WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
            (user['id'],)
        ).fetchall()
        conn.close()
        if logs:
            for log in logs:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:6px 12px;
                background:#151d35;border-radius:6px;margin:3px 0;font-size:0.82rem">
                    <span style="color:#e2e8f0">{log['action']}</span>
                    <span style="color:#64748b">{log['created_at'][:16]}</span>
                </div>""", unsafe_allow_html=True)
