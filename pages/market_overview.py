import streamlit as st
import pandas as pd
from config.styles import inject_css, page_header, badge
from analytics.data_engine import get_market_overview, get_sector_performance, get_close_prices
from visualizations.charts import (line_chart, sector_heatmap, bar_chart, gauge_chart,
                                     area_chart, histogram)
from config.constants import MACRO_INSTRUMENTS

def show():
    inject_css()
    page_header("Market Overview", "Global markets at a glance", "🌍")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Indices", "🌡️ Sectors", "💱 Forex & Commodities", "🔐 Crypto", "📈 Charts"])

    with tab1:
        overview = get_market_overview()
        if overview:
            df = pd.DataFrame(overview)
            for _, row in df.iterrows():
                pct = row['change_pct']
                color = "#10b981" if pct >= 0 else "#ef4444"
                delta_sign = "+" if pct >= 0 else ""
                st.markdown(f"""
                <div class="card" style="display:flex;justify-content:space-between;align-items:center;padding:18px 24px;transition:all 0.2s">
                    <div>
                        <div style="font-weight:700;color:#e2e8f0;font-size:1.05rem">{row['name']}</div>
                        <div style="font-size:0.8rem;color:#64748b;margin-top:4px">{row['symbol']}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:1.3rem;font-weight:700;color:#e2e8f0">{row['price']:,.2f}</div>
                        <div style="color:{color};font-size:0.9rem">{delta_sign}{pct:.2f}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Loading market data…")

    with tab2:
        sectors = get_sector_performance()
        if sectors:
            fig = sector_heatmap(sectors)
            st.plotly_chart(fig, use_container_width=True)
            
            df_sec = pd.DataFrame([
                {'Sector': k, 'Change %': v['change_pct']}
                for k, v in sorted(sectors.items(), key=lambda x: x[1]['change_pct'], reverse=True)
            ])
            fig2 = bar_chart(df_sec['Sector'].tolist(), df_sec['Change %'].tolist(),
                             'Sector Returns (%)', color=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Loading sector data…")

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💱 Forex")
            forex_syms = MACRO_INSTRUMENTS['Forex']
            prices = get_close_prices(forex_syms[:6], '1mo')
            if not prices.empty:
                rets = prices.pct_change().iloc[-1] * 100
                for sym in rets.index:
                    val = rets[sym]
                    color = "#10b981" if val >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:10px 14px;
                    background:#151d35;border-radius:10px;margin:4px 0;border:1px solid #253452">
                        <span style="color:#e2e8f0;font-weight:500">{sym}</span>
                        <span style="color:{color};font-weight:600">{val:+.2f}%</span>
                    </div>""", unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🛢️ Commodities")
            comm_syms = MACRO_INSTRUMENTS['Commodities']
            prices2 = get_close_prices(comm_syms[:6], '1mo')
            if not prices2.empty:
                rets2 = prices2.pct_change().iloc[-1] * 100
                for sym in rets2.index:
                    val = rets2[sym]
                    color = "#10b981" if val >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:10px 14px;
                    background:#151d35;border-radius:10px;margin:4px 0;border:1px solid #253452">
                        <span style="color:#e2e8f0;font-weight:500">{sym}</span>
                        <span style="color:{color};font-weight:600">{val:+.2f}%</span>
                    </div>""", unsafe_allow_html=True)

    with tab4:
        crypto_syms = MACRO_INSTRUMENTS['Crypto']
        prices3 = get_close_prices(crypto_syms, '1mo')
        if not prices3.empty:
            col_a, col_b = st.columns(2)
            rets3 = prices3.pct_change().iloc[-1] * 100
            cols = [col_a, col_b]
            for i, sym in enumerate(rets3.index):
                val = rets3[sym]
                price = prices3[sym].iloc[-1]
                color = "#10b981" if val >= 0 else "#ef4444"
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="card" style="text-align:center;padding:20px">
                        <div style="font-weight:700;color:#e2e8f0;font-size:1rem">{sym.replace('-USD','')}</div>
                        <div style="font-size:1.5rem;font-weight:800;color:#00d4ff;margin:8px 0">${price:,.2f}</div>
                        <span class="badge badge-{('green' if val >= 0 else 'red')}">{val:+.2f}%</span>
                    </div>""", unsafe_allow_html=True)
            fig = line_chart(prices3 / prices3.iloc[0] * 100, 'Crypto Normalized (Base=100)', height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Loading crypto data…")

    with tab5:
        st.markdown("#### 📈 Historical Chart")
        col1, col2 = st.columns([2, 1])
        with col2:
            chart_sym = st.selectbox("Symbol", ["SPY", "QQQ", "GLD", "BTC-USD", "^NSEI", "AAPL"], key="chart_sym")
            period = st.selectbox("Period", ["1mo","3mo","6mo","1y","2y"], key="chart_period")
        with col1:
            with st.spinner("Loading chart…"):
                data = get_close_prices([chart_sym], period)
            if not data.empty:
                fig = area_chart(data, f'{chart_sym} Price History', height=420)
                st.plotly_chart(fig, use_container_width=True)