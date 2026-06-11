import streamlit as st
import pandas as pd
import numpy as np
from config.styles import inject_css, page_header, metric_card, badge
from auth.auth_manager import current_user
from analytics.data_engine import get_market_overview, get_sector_performance, get_close_prices
from visualizations.charts import sector_heatmap, line_chart, gauge_chart
from database.db import get_watchlists
import json

def show():
    inject_css()
    page_header("Dashboard", "Your institutional intelligence command center", "🏠")
    user = current_user()

    # ── Welcome Banner ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="card" style="margin-bottom:20px">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0">
                    Welcome back, {user.get('full_name', user.get('username','')).split()[0]}
                </div>
                <div style="color:#64748b;margin-top:4px">
                    Today is {pd.Timestamp.now().strftime('%A, %B %d, %Y')}
                </div>
            </div>
            <div style="display:flex;gap:8px">
                {badge('Live', 'green')}
                {badge('Premium Access', 'purple')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top Metrics ─────────────────────────────────────────────
    overview = get_market_overview()
    idx_map = {'^GSPC':'S&P 500', '^IXIC':'Nasdaq', '^NSEI':'Nifty 50', '^VIX':'VIX', '^BSESN':'Sensex'}

    metrics_html = ""
    for item in overview[:5]:
        if item['symbol'] in idx_map:
            pct = item['change_pct']
            color = "#10b981" if pct >= 0 else "#ef4444"
            arrow = "▲" if pct >= 0 else "▼"
            metrics_html += f"""
            <div style="background:var(--bg-card);border:1px solid var(--border-secondary);
                border-radius:14px;padding:16px;text-align:center;transition:all 0.3s">
                <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:4px">{idx_map[item['symbol']]}</div>
                <div style="font-size:1.4rem;font-weight:700;color:var(--text-primary)">{item['price']:,.2f}</div>
                <div style="color:{color};font-size:0.85rem">{arrow} {abs(pct):.2f}%</div>
            </div>
            """
    
    st.markdown(f"""<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px">{metrics_html}</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Sector Performance & Watchlists ─────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("#### 🌡️ Sector Performance")
        sector_data = get_sector_performance()
        if sector_data:
            fig = sector_heatmap(sector_data)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Loading sector data…")

    with col_right:
        st.markdown("#### ⭐ My Watchlists")
        wls = get_watchlists(user['id'])
        if wls:
            for wl in wls[:4]:
                syms = json.loads(wl['symbols']) if isinstance(wl['symbols'], str) else wl['symbols']
                st.markdown(f"""
                <div class="card" style="padding:14px;margin:8px 0;cursor:pointer;transition:all 0.2s"
                     onclick="window.location.hash='watchlists'">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div style="font-weight:600;color:#e2e8f0">{wl['name']}</div>
                            <div style="font-size:0.75rem;color:#64748b;margin-top:4px">
                                {len(syms)} assets
                            </div>
                        </div>
                        {badge('Active', 'blue')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:24px">
                <div style="font-size:2rem;margin-bottom:8px">⭐</div>
                <div style="color:#64748b;font-size:0.9rem">No watchlists yet</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Market Monitor ───────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📈 Global Indices")
        if overview:
            df_ov = pd.DataFrame(overview)
            df_ov['Change %'] = df_ov['change_pct'].apply(lambda x: f"▲ {x:.2f}%" if x >= 0 else f"▼ {abs(x):.2f}%")
            df_ov['Price'] = df_ov['price'].apply(lambda x: f"{x:,.2f}")
            display = df_ov[['name','Price','Change %']].rename(columns={'name':'Index'})
            st.dataframe(display, use_container_width=True, hide_index=True, height=280)

    with col_b:
        st.markdown("#### 🎯 Market Sentiment")
        vix_val = 20.0
        for item in overview:
            if item['symbol'] == '^VIX':
                vix_val = item['price']
                break
        fig = gauge_chart(vix_val, 'VIX Fear Index', 0, 80, 30)
        st.plotly_chart(fig, use_container_width=True)

    # ── Quick Analysis ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ⚡ Quick Lead-Lag Snapshot")
    quick_syms = ['SPY', 'QQQ', 'GLD', '^VIX', 'TLT']
    with st.spinner("Loading price data…"):
        prices = get_close_prices(quick_syms, '6mo')
    if not prices.empty:
        rets = prices.pct_change().dropna()
        fig = line_chart(prices / prices.iloc[0] * 100, 'Normalized Price (Base=100)', height=350)
        st.plotly_chart(fig, use_container_width=True)

    # ── Platform Features ────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Platform Modules")
    features = [
        ("⚡", "Lead-Lag Discovery", "Cross-asset timing, correlation shifts, information flow detection"),
        ("🧠", "Causal Intelligence", "Statistical causality engines with Granger/Transfer Entropy"),
        ("🤖", "Forecast Lab", "ML models with SHAP explanations and scenario analysis"),
        ("🕸️", "Dependency Network", "PageRank, betweenness, and community detection"),
        ("📊", "50+ Visualizations", "Financial, statistical, and 3D charts"),
        ("💼", "Portfolio Impact", "Scenario analysis and stress testing"),
    ]
    
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:20px;height:140px;transition:all 0.3s">
                <div style="font-size:2rem;margin-bottom:8px">{icon}</div>
                <div style="font-weight:700;color:#00d4ff;font-size:0.9rem">{title}</div>
                <div style="font-size:0.75rem;color:#64748b;margin-top:6px;line-height:1.3">{desc}</div>
            </div>
            """, unsafe_allow_html=True)