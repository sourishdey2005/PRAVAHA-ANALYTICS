import streamlit as st
import pandas as pd
import numpy as np
from config.styles import inject_css, page_header, badge
from analytics.data_engine import get_close_prices, search_assets, get_asset_info
from visualizations.charts import (candlestick_volume, line_chart, histogram,
                                     returns_distribution, correlation_heatmap, box_plot)
from config.constants import NIFTY50, SP500_SAMPLE

def show():
    inject_css()
    page_header("Asset Explorer", "Deep-dive into any asset or basket", "🔍")

    col_ctrl, col_main = st.columns([1, 3], gap="large")

    with col_ctrl:
        st.markdown("#### ⚙️ Configuration", help="Configure your asset analysis parameters")
        search_q = st.text_input("🔍 Search", placeholder="AAPL, Reliance, Gold…", key="search_q")
        universe = st.selectbox("Asset Universe", ["Custom", "Nifty 50", "S&P 500 Sample", "Macro Instruments"], key="universe")
        period = st.selectbox("Time Period", ["1mo","3mo","6mo","1y","2y","3y"], index=3, key="period")
        chart_type = st.selectbox("Chart Type", ["Candlestick+Volume", "Line", "Area", "Returns Distribution"], key="chart_type")

        symbols = []
        if universe == "Nifty 50":
            symbols = NIFTY50[:20]
        elif universe == "S&P 500 Sample":
            symbols = SP500_SAMPLE[:20]
        elif universe == "Macro Instruments":
            from config.constants import MACRO_INSTRUMENTS
            symbols = MACRO_INSTRUMENTS['Indices'] + MACRO_INSTRUMENTS['Commodities'][:5]

        if search_q:
            results = search_assets(search_q, 10)
            if results:
                found = [r['symbol'] for r in results[:10]]
                selected_search = st.multiselect("Search Results", found, default=found[:3], key="search_results")
                symbols = selected_search if selected_search else symbols

        if not symbols:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

        selected = st.multiselect("Selected Assets", symbols, default=symbols[:4], max_selections=10, key="selected_assets")
        if not selected:
            selected = symbols[:4]

    with col_main:
        with st.spinner("Fetching data…"):
            prices = get_close_prices(selected, period)

        if prices.empty:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px">
                <div style="font-size:2.5rem">⚠️</div>
                <div style="font-size:1.1rem;color:#64748b;margin-top:12px">No price data available for selected symbols</div>
            </div>
            """, unsafe_allow_html=True)
            return

        tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Chart", "📊 Statistics", "🔄 Returns", "🔗 Correlation"])

        with tab1:
            sym_chart = st.selectbox("Primary Asset", selected, key='primary_asset')
            from analytics.data_engine import get_prices
            raw = get_prices([sym_chart], period)
            df_raw = raw.get(sym_chart, prices[[sym_chart]])
            if chart_type == "Candlestick+Volume":
                from visualizations.charts import candlestick_volume
                fig = candlestick_volume(df_raw, sym_chart)
            elif chart_type == "Line":
                fig = line_chart(prices[selected[:6]], f"{', '.join(selected[:6])} Prices", 400)
            elif chart_type == "Area":
                from visualizations.charts import area_chart
                fig = area_chart(prices[selected[:4]], "Normalized Prices", 400)
            else:
                rets = prices[sym_chart].pct_change().dropna()
                fig = returns_distribution(rets, f'{sym_chart} Returns Distribution')
            st.plotly_chart(fig, use_container_width=True)

            # Normalized comparison
            if len(selected) > 1:
                norm = prices / prices.iloc[0] * 100
                fig2 = line_chart(norm[selected[:6]], 'Normalized Performance (Base=100)', 350)
                st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            rets = prices.pct_change().dropna()
            stats_rows = []
            for sym in selected:
                if sym not in prices.columns:
                    continue
                s = prices[sym].dropna()
                r = rets[sym].dropna() if sym in rets.columns else pd.Series()
                stats_rows.append({
                    'Symbol': sym,
                    'Current Price': f"{s.iloc[-1]:,.4f}",
                    'Return (Total)': f"{(s.iloc[-1]/s.iloc[0]-1)*100:.2f}%",
                    'Ann. Return': f"{(((s.iloc[-1]/s.iloc[0])**(252/len(s)))-1)*100:.2f}%",
                    'Volatility (Ann.)': f"{r.std()*np.sqrt(252)*100:.2f}%" if len(r) > 0 else 'N/A',
                    'Sharpe': f"{(r.mean()/r.std()*np.sqrt(252)):.2f}" if len(r) > 0 and r.std() > 0 else 'N/A',
                    'Max Drawdown': f"{_max_drawdown(s)*100:.2f}%" if len(s) > 0 else 'N/A',
                    'Skewness': f"{r.skew():.3f}" if len(r) > 0 else 'N/A',
                    'Kurtosis': f"{r.kurtosis():.3f}" if len(r) > 0 else 'N/A',
                })
            st.dataframe(pd.DataFrame(stats_rows), use_container_width=True, hide_index=True)

        with tab3:
            rets2 = prices.pct_change().dropna()
            if len(selected) > 1:
                fig = box_plot(rets2[selected[:8]], 'Returns Distribution Box Plot')
            else:
                fig = histogram(rets2[selected[0]], f'{selected[0]} Daily Returns', bins=60)
            st.plotly_chart(fig, use_container_width=True)

        with tab4:
            rets3 = prices.pct_change().dropna()
            if len(selected) >= 2:
                fig = correlation_heatmap(rets3[selected[:10]], f'Correlation Matrix')
                st.plotly_chart(fig, use_container_width=True)
                # Show table
                corr = rets3[selected[:10]].corr().round(4)
                st.dataframe(corr, use_container_width=True)
            else:
                st.info("Select at least 2 assets for correlation analysis.")

def _max_drawdown(prices):
    roll_max = prices.cummax()
    drawdown = prices / roll_max - 1
    return drawdown.min()