import jwt
import streamlit as st
from datetime import datetime, timedelta
from database.db import get_user, verify_password, update_last_login, log_audit

SECRET = "pravaha_secret_key_2024"

def generate_token(user_id, username, remember=False):
    exp = datetime.utcnow() + (timedelta(days=30) if remember else timedelta(hours=8))
    payload = {'user_id': user_id, 'username': username, 'exp': exp}
    return jwt.encode(payload, SECRET, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except Exception:
        return None

def login(username, password, remember=False):
    if verify_password(username, password):
        user = get_user(username)
        token = generate_token(user['id'], user['username'], remember)
        update_last_login(user['id'])
        log_audit(user['id'], 'login', f"Login from session")
        st.session_state['authenticated'] = True
        st.session_state['user'] = user
        st.session_state['token'] = token
        return True, user
    return False, None

def logout():
    for k in ['authenticated', 'user', 'token']:
        st.session_state.pop(k, None)

def is_authenticated():
    if st.session_state.get('authenticated') and st.session_state.get('user'):
        return True
    token = st.session_state.get('token')
    if token:
        data = decode_token(token)
        if data:
            user = get_user(data['username'])
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user
                return True
    return False

def require_auth():
    if not is_authenticated():
        st.switch_page("app.py")
        st.stop()

def current_user():
    return st.session_state.get('user', {})
