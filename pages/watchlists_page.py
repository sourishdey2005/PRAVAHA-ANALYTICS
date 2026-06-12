import streamlit as st
import pandas as pd
import json
from config.styles import inject_css, page_header
from auth.auth_manager import current_user
from database.db import get_watchlists, save_watchlist, update_watchlist, delete_watchlist
from analytics.data_engine import get_close_prices
from visualizations.charts import line_chart

def show():
    inject_css()
    page_header("Watchlists", "Track and monitor your curated asset baskets", "⭐")

    user = current_user()
    wls = get_watchlists(user['id'])

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### 📋 My Watchlists")
        if wls:
            for wl in wls:
                syms = json.loads(wl['symbols']) if isinstance(wl['symbols'], str) else wl['symbols']
                with st.expander(f"⭐ {wl['name']} ({len(syms)} assets)"):
                    st.write(f"*{wl.get('description', '')}*")
                    st.write(", ".join(syms))
                    if st.button(f"📊 View", key=f"view_{wl['id']}"):
                        st.session_state['active_wl'] = wl['id']
                        st.session_state['active_wl_syms'] = syms
                        st.session_state['active_wl_name'] = wl['name']
                    if st.button(f"🗑️ Delete", key=f"del_{wl['id']}"):
                        delete_watchlist(wl['id'])
                        st.rerun()
        else:
            st.info("No watchlists. Create one below.")

        st.markdown("---")
        st.markdown("#### ➕ Create Watchlist")
        with st.form("create_wl"):
            wl_name = st.text_input("Name", placeholder="My Watchlist")
            wl_desc = st.text_input("Description")
            wl_syms = st.text_area("Symbols (comma-separated)", placeholder="AAPL,MSFT,GOOGL")
            submitted = st.form_submit_button("Create", use_container_width=True)
            if submitted and wl_name and wl_syms:
                syms_list = [s.strip() for s in wl_syms.split(',') if s.strip()]
                save_watchlist(user['id'], wl_name, syms_list, wl_desc)
                st.success(f"Watchlist '{wl_name}' created!")
                st.rerun()

    with col2:
        active_syms = st.session_state.get('active_wl_syms')
        active_name = st.session_state.get('active_wl_name', 'Watchlist')

        if active_syms:
            st.markdown(f"#### 📊 {active_name}")
            period = st.selectbox("Period", ["1mo","3mo","6mo","1y"], index=2, key='wl_period')

            with st.spinner("Loading prices…"):
                prices = get_close_prices(active_syms, period)

            if not prices.empty:
                # Normalized chart
                norm = prices / prices.iloc[0] * 100
                fig = line_chart(norm, f'{active_name} — Normalized Performance (Base=100)', 380)
                st.plotly_chart(fig, use_container_width=True)

                # Summary table
                rows = []
                rets = prices.pct_change().dropna()
                for sym in prices.columns:
                    s = prices[sym].dropna()
                    r = rets[sym].dropna() if sym in rets.columns else pd.Series()
                    chg_1d = r.iloc[-1]*100 if len(r) > 0 else 0
                    chg_total = (s.iloc[-1]/s.iloc[0]-1)*100
                    rows.append({
                        'Symbol': sym,
                        'Price': f"{s.iloc[-1]:,.4f}",
                        '1D %': f"{'▲' if chg_1d>=0 else '▼'} {abs(chg_1d):.2f}%",
                        'Total %': f"{'▲' if chg_total>=0 else '▼'} {abs(chg_total):.2f}%",
                        'Vol (Ann.)': f"{r.std()*252**0.5*100:.2f}%" if len(r) > 0 else 'N/A',
                    })
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True, height=280)
            else:
                st.warning("No price data available for these symbols.")
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px">
                <div style="font-size:3rem">⭐</div>
                <div style="font-size:1.1rem;font-weight:700;color:#00d4ff;margin-top:16px">Select a Watchlist</div>
                <div style="color:#64748b;margin-top:8px">Click "View" on any watchlist to see its performance</div>
            </div>""", unsafe_allow_html=True)
