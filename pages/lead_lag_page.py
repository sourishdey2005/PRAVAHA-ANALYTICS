import streamlit as st
import pandas as pd
import numpy as np
from config.styles import inject_css, page_header, badge
from analytics.data_engine import get_close_prices, get_returns
from analytics.lead_lag import (cross_correlation, find_optimal_lag, granger_causality,
                                   transfer_entropy, mutual_information, compute_lead_lag_matrix,
                                   rolling_correlation, cointegration_test)
from visualizations.charts import (cross_correlation_chart, line_chart, correlation_heatmap,
                                     rolling_corr_heatmap, lag_heatmap, scatter_plot)
from config.constants import NIFTY50, SP500_SAMPLE, MACRO_INSTRUMENTS

def show():
    inject_css()
    page_header("Lead-Lag Discovery", "Detect temporal predictive relationships between assets", "⚡")

    col_ctrl, col_main = st.columns([1, 3], gap="large")

    with col_ctrl:
        st.markdown("#### ⚙️ Configuration")
        mode = st.radio("Analysis Mode", ["Pair Analysis", "Matrix Analysis"], index=0, help="Pair: analyze two assets. Matrix: scan all pairs.")
        universe_choice = st.selectbox("Asset Universe", ["Custom", "Nifty 50", "S&P 500", "Macro"], key="universe_choice")
        period = st.selectbox("Time Period", ["6mo","1y","2y","3y"], index=1)
        max_lag = st.slider("Max Lag (days)", 5, 60, 20, help="Maximum number of trading days to scan for lead-lag relationship")
        min_conf = st.slider("Min Confidence", 0.0, 1.0, 0.3, help="Minimum confidence threshold for matrix analysis")

        if universe_choice == "Nifty 50":
            universe = NIFTY50[:20]
        elif universe_choice == "S&P 500":
            universe = SP500_SAMPLE[:20]
        elif universe_choice == "Macro":
            universe = (MACRO_INSTRUMENTS['Indices'] + MACRO_INSTRUMENTS['Commodities'] +
                        MACRO_INSTRUMENTS['Forex'][:4] + MACRO_INSTRUMENTS['ETFs'][:5])
        else:
            universe = ['SPY','QQQ','GLD','TLT','^VIX','GC=F','CL=F','DX-Y.NYB']

        if mode == "Pair Analysis":
            lead_sym = st.selectbox("Lead Asset", universe, index=0, key='lead_sym')
            lag_sym = st.selectbox("Lag Asset", universe, index=min(1, len(universe)-1), key='lag_sym')
            run = st.button("🔍 Analyze Pair", use_container_width=True, type="primary")
        else:
            selected = st.multiselect("Assets", universe, default=universe[:8], max_selections=15, key='matrix_assets')
            run = st.button("🚀 Run Matrix Analysis", use_container_width=True, type="primary")

    with col_main:
        if mode == "Pair Analysis":
            if run:
                _pair_analysis(lead_sym, lag_sym, period, max_lag)
            else:
                st.markdown("""
                <div class="card" style="text-align:center;padding:60px">
                    <div style="font-size:2.5rem">⚡</div>
                    <div style="font-size:1.2rem;font-weight:700;color:#00d4ff;margin-top:16px">Lead-Lag Discovery Engine</div>
                    <div style="color:#64748b;margin-top:8px">Select two assets and click "Analyze Pair" to detect leading/lagging relationships</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            if run and 'matrix_assets' in dir():
                selected = st.session_state.get('matrix_assets', universe[:8])
                if len(selected) >= 2:
                    _matrix_analysis(selected, period, max_lag, min_conf)
                else:
                    st.markdown("""
                    <div class="card" style="text-align:center;padding:40px">
                        <div style="font-size:2rem;color:#ef4444">⚠️</div>
                        <div style="color:#ef4444;margin-top:8px">Select at least 2 assets for matrix analysis</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="card" style="text-align:center;padding:60px">
                    <div style="font-size:2.5rem">🕸️</div>
                    <div style="font-size:1.2rem;font-weight:700;color:#00d4ff;margin-top:16px">Matrix Analysis</div>
                    <div style="color:#64748b;margin-top:8px">Select multiple assets to discover all lead-lag relationships</div>
                </div>
                """, unsafe_allow_html=True)

def _pair_analysis(lead_sym, lag_sym, period, max_lag):
    with st.spinner("Computing lead-lag relationships…"):
        prices = get_close_prices([lead_sym, lag_sym], period)

    if prices.empty or lead_sym not in prices.columns or lag_sym not in prices.columns:
        st.markdown("""
        <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
            <div style="font-size:2rem;color:#ef4444">❌</div>
            <div style="color:#ef4444;margin-top:8px">Could not fetch price data for selected assets</div>
        </div>
        """, unsafe_allow_html=True)
        return

    rets = prices.pct_change().dropna()
    r1, r2 = rets[lead_sym], rets[lag_sym]

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    opt = find_optimal_lag(r1, r2, max_lag)
    if opt:
        col1.metric("Optimal Lag", f"{opt['optimal_lag']} days", help="Days lead asset predicts lag asset")
        col2.metric("Correlation", f"{opt['correlation']:.4f}", help="Cross-correlation coefficient")
    gc = granger_causality(r1, r2, min(10, max_lag))
    if gc:
        col3.metric("Granger P-value", f"{gc['p_value']:.4f}", help="Statistical significance (p < 0.05 = significant)")
        col4.metric("Significant", "✅ Yes" if gc['significant'] else "❌ No")

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Cross-Correlation", "🔄 Rolling Corr", "📈 Price Chart", "📋 Full Report"])

    with tab1:
        xcorr = cross_correlation(r1, r2, max_lag)
        if xcorr:
            fig = cross_correlation_chart(xcorr, f'Cross-Correlation: {lead_sym} → {lag_sym}')
            st.plotly_chart(fig, use_container_width=True)
        # Result card
        if opt:
            lag_d = opt['optimal_lag']
            corr = opt['correlation']
            direction = "leads" if lag_d > 0 else "lags"
            st.markdown(f"""
            <div class="lead-lag-result">
                <div style="font-size:1.2rem;font-weight:700;color:#00d4ff">
                    {lead_sym} {direction} {lag_sym} by {abs(lag_d)} trading days
                </div>
                <div style="color:#94a3b8;margin-top:8px">
                    When <b style="color:#e2e8f0">{lead_sym}</b> moves today,
                    <b style="color:#e2e8f0">{lag_sym}</b> tends to follow in {abs(lag_d)} day(s)
                    with {abs(corr):.1%} correlation.
                </div>
                <div class="confidence-bar" style="margin-top:12px">
                    <div class="confidence-fill" style="width:{min(abs(corr)*100,100):.0f}%"></div>
                </div>
                <div style="color:#64748b;font-size:0.8rem">{abs(corr):.1%} predictive strength</div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        rc = rolling_correlation(r1, r2, 20)
        if not rc.empty:
            fig = line_chart(rc.rename('Rolling(20d) Corr'), 'Rolling 20-Day Correlation', 350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for rolling correlation")

    with tab3:
        fig = line_chart(prices / prices.iloc[0] * 100, 'Normalized Prices', 380)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("#### Full Analysis Report")
        metrics = {
            'Lead Asset': lead_sym, 'Lag Asset': lag_sym,
            'Optimal Lag': f"{opt['optimal_lag']} days" if opt else 'N/A',
            'Correlation': f"{opt['correlation']:.4f}" if opt else 'N/A',
            'P-Value': f"{gc['p_value']:.6f}" if gc else 'N/A',
            'Granger Significant': str(gc['significant']) if gc else 'N/A',
        }
        mi = mutual_information(r1, r2)
        metrics['Mutual Information'] = f"{mi:.4f}"
        coint = cointegration_test(prices[lead_sym], prices[lag_sym])
        if coint:
            metrics['Cointegration P'] = f"{coint['p_value']:.4f}"
            metrics['Cointegrated'] = str(coint['cointegrated'])
        for k, v in metrics.items():
            c1, c2 = st.columns(2)
            c1.markdown(f"**{k}**")
            c2.write(v)

def _matrix_analysis(selected, period, max_lag, min_conf):
        with st.spinner("Fetching prices and computing pairwise lead-lag matrix…"):
            prices = get_close_prices(selected, period)
            if prices.empty:
                st.error("No data.")
                return
            rets = prices.pct_change().dropna()
            result_df = compute_lead_lag_matrix(rets, max_lag)

        if result_df.empty:
            st.markdown("""
            <div class="card" style="text-align:center;padding:40px">
                <div style="font-size:2rem;color:#f59e0b">🔍</div>
                <div style="color:#f59e0b;margin-top:8px">No significant lead-lag relationships found. Try more assets or longer period.</div>
            </div>
            """, unsafe_allow_html=True)
            return

        st.success(f"Found {len(result_df)} lead-lag relationships!")
        st.dataframe(result_df.head(50), use_container_width=True, hide_index=True)

        # Visualize top relationships
        st.markdown("#### Top Lead-Lag Pairs")
        top = result_df.head(10)
        for _, row in top.iterrows():
            conf = row['confidence']
            lag = row['optimal_lag']
            corr = row['correlation']
            st.markdown(f"""
            <div class="lead-lag-result" style="margin:8px 0">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span style="color:#00d4ff;font-weight:700">{row['lead']}</span>
                        <span style="color:#64748b;margin:0 10px">→ leads {lag}d →</span>
                        <span style="color:#7c3aed;font-weight:700">{row['lag_asset']}</span>
                    </div>
                    <div style="display:flex;gap:6px">
                        <span class="badge badge-blue">Conf: {conf:.2f}</span>
                        <span class="badge badge-green">Corr: {corr:.3f}</span>
                    </div>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width:{conf*100:.0f}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Correlation heatmap
        st.markdown("#### Correlation Heatmap")
        fig = correlation_heatmap(rets[selected[:12]])
        st.plotly_chart(fig, use_container_width=True)

        # Download
        csv = result_df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "lead_lag_results.csv", "text/csv")