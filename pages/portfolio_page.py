import streamlit as st
import pandas as pd
import numpy as np
from config.styles import inject_css, page_header, badge
from analytics.data_engine import get_close_prices
from visualizations.charts import (line_chart, area_chart, bar_chart,
                                     scatter_plot, gauge_chart, correlation_heatmap)

def show():
    inject_css()
    page_header("Portfolio Impact", "Scenario analysis, stress testing & dependency risk", "💼")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio Builder", "⚡ Scenario Analysis", "🔥 Stress Test", "🔗 Dependency Risk"])

    with tab1:
        st.markdown("#### Build Your Portfolio")
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            assets_input = st.text_input("Assets", "AAPL,MSFT,GOOGL,AMZN,GLD,TLT", key="port_assets")
            symbols = [s.strip() for s in assets_input.split(',') if s.strip()]
            period = st.selectbox("Time Period", ["1y","2y","3y"], index=1, key="port_period")

            weights_input = {}
            st.markdown("**Weights (must sum to 100%)**")
            default_w = round(100/len(symbols), 1)
            for sym in symbols:
                weights_input[sym] = st.slider(f"{sym}", 0.0, 100.0, default_w, step=0.5, key=f"w_{sym}")

            total_w = sum(weights_input.values())
            if abs(total_w - 100) > 1:
                st.markdown(f'<span class="badge badge-red">Weights sum to {total_w:.1f}% (need 100%)</span>', unsafe_allow_html=True)

            analyze = st.button("📊 Analyze Portfolio", type="primary", use_container_width=True)

        with col2:
            if analyze:
                _analyze_portfolio(symbols, weights_input, period)

    with tab2:
        st.markdown("#### Scenario Analysis")
        col_a, col_b = st.columns([1, 2], gap="large")
        with col_a:
            scenario_assets = st.text_input("Assets", "SPY,GLD,TLT,BTC-USD", key="sc_assets")
            sc_syms = [s.strip() for s in scenario_assets.split(',') if s.strip()]
            scenario = st.selectbox("Scenario", [
                "2008 Financial Crisis", "2020 COVID Crash", "2022 Rate Hike",
                "Inflation Spike +20%", "Dollar Collapse -20%", "Custom"
            ])
            run_sc = st.button("▶ Run Scenario", type="primary", use_container_width=True)
        with col_b:
            if run_sc:
                _run_scenario(sc_syms, scenario)

    with tab3:
        st.markdown("#### Stress Testing")
        stress_assets = st.text_input("Portfolio Assets", "SPY,QQQ,GLD,TLT", key="stress_assets")
        st_syms = [s.strip() for s in stress_assets.split(',') if s.strip()]
        col_x, col_y = st.columns(2)
        with col_x:
            shock_pct = st.slider("Market Shock (%)", -50, 50, -20)
        with col_y:
            vol_mult = st.slider("Volatility Multiplier", 1.0, 5.0, 2.0, step=0.5)
        if st.button("🔥 Run Stress Test", type="primary"):
            _run_stress_test(st_syms, shock_pct, vol_mult)

    with tab4:
        st.markdown("#### Dependency Risk Dashboard")
        dep_assets = st.text_input("Portfolio Assets", "AAPL,MSFT,GOOGL,TSLA,NVDA,AMZN", key="dep_assets")
        dep_syms = [s.strip() for s in dep_assets.split(',') if s.strip()]
        if st.button("🔗 Compute Dependency Risk"):
            _dependency_risk(dep_syms)

def _analyze_portfolio(symbols, weights, period):
    prices = get_close_prices(symbols, period)
    if prices.empty:
        st.markdown("""
        <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
            <div style="font-size:2rem;color:#ef4444">❌</div>
            <div style="color:#ef4444;margin-top:8px">No data available</div>
        </div>
        """, unsafe_allow_html=True)
        return
    total = sum(weights.values())
    w = {k: v/total for k, v in weights.items()}
    rets = prices.pct_change().dropna()
    avail = [s for s in symbols if s in rets.columns]
    w_arr = np.array([w.get(s, 0) for s in avail])
    if w_arr.sum() == 0:
        st.error("No valid assets.")
        return
    w_arr /= w_arr.sum()
    port_rets = rets[avail].dot(w_arr)
    cum_rets = (1 + port_rets).cumprod()

    c1, c2, c3, c4 = st.columns(4)
    total_ret = (cum_rets.iloc[-1] - 1) * 100
    ann_ret = ((cum_rets.iloc[-1]) ** (252/len(cum_rets)) - 1) * 100
    ann_vol = port_rets.std() * np.sqrt(252) * 100
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    c1.metric("Total Return", f"{total_ret:.2f}%")
    c2.metric("Ann. Return", f"{ann_ret:.2f}%")
    c3.metric("Ann. Volatility", f"{ann_vol:.2f}%")
    c4.metric("Sharpe Ratio", f"{sharpe:.2f}")

    fig = line_chart(cum_rets.rename('Portfolio Value'), 'Portfolio Cumulative Return', 380)
    st.plotly_chart(fig, use_container_width=True)

    ind_rets = {}
    for sym, wi in zip(avail, w_arr):
        ind_rets[sym] = (prices[sym].iloc[-1]/prices[sym].iloc[0]-1)*100 * wi
    fig2 = bar_chart(list(ind_rets.keys()), list(ind_rets.values()), 'Weighted Contribution (%)', color=True)
    st.plotly_chart(fig2, use_container_width=True)

def _run_scenario(symbols, scenario):
    shocks = {
        "2008 Financial Crisis": {'SPY': -55, 'QQQ': -50, 'GLD': +25, 'TLT': +20, 'default': -40},
        "2020 COVID Crash": {'SPY': -35, 'QQQ': -30, 'GLD': +15, 'TLT': +25, 'default': -30},
        "2022 Rate Hike": {'SPY': -20, 'QQQ': -33, 'GLD': -5, 'TLT': -30, 'default': -15},
        "Inflation Spike +20%": {'GLD': +30, 'TLT': -25, 'SPY': -15, 'default': -10},
        "Dollar Collapse -20%": {'GLD': +40, 'default': -5},
    }
    shock_map = shocks.get(scenario, {})
    impacts = []
    for sym in symbols:
        impact = shock_map.get(sym, shock_map.get('default', -10))
        impacts.append({'Asset': sym, 'Scenario Impact (%)': impact})
    df = pd.DataFrame(impacts)
    st.markdown(f"#### {scenario} — Estimated Impact")
    fig = bar_chart(df['Asset'].tolist(), df['Scenario Impact (%)'].tolist(),
                    f'{scenario} Portfolio Impact', color=True)
    st.plotly_chart(fig, use_container_width=True)
    portfolio_impact = df['Scenario Impact (%)'].mean()
    color = "#ef4444" if portfolio_impact < 0 else "#10b981"
    st.markdown(f"""
    <div class="lead-lag-result">
        <div style="font-size:1.1rem;font-weight:700;color:{color}">
            Portfolio Impact: {portfolio_impact:+.1f}%
        </div>
        <div style="color:#94a3b8;margin-top:6px">Estimated portfolio loss/gain under {scenario}</div>
    </div>
    """, unsafe_allow_html=True)

def _run_stress_test(symbols, shock_pct, vol_mult):
    prices = get_close_prices(symbols, '1y')
    if prices.empty:
        st.markdown("""
        <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
            <div style="font-size:2rem;color:#ef4444">❌</div>
            <div style="color:#ef4444;margin-top:8px">No data available</div>
        </div>
        """, unsafe_allow_html=True)
        return
    rets = prices.pct_change().dropna()
    st.markdown(f"#### Stress Test: {shock_pct:+.0f}% Shock, {vol_mult}x Volatility")
    results = []
    for sym in symbols:
        if sym not in rets.columns: continue
        base_ret = rets[sym].mean() * 252 * 100
        base_vol = rets[sym].std() * np.sqrt(252) * 100
        stressed_ret = base_ret + shock_pct
        stressed_vol = base_vol * vol_mult
        results.append({'Asset': sym, 'Base Return (%)': round(base_ret,2),
                        'Stressed Return (%)': round(stressed_ret,2),
                        'Base Vol (%)': round(base_vol,2),
                        'Stressed Vol (%)': round(stressed_vol,2)})
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True, hide_index=True)
    fig = bar_chart(df['Asset'].tolist(), df['Stressed Return (%)'].tolist(),
                    'Stressed Returns (%)', color=True)
    st.plotly_chart(fig, use_container_width=True)

def _dependency_risk(symbols):
    prices = get_close_prices(symbols, '1y')
    if prices.empty:
        st.markdown("""
        <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
            <div style="font-size:2rem;color:#ef4444">❌</div>
            <div style="color:#ef4444;margin-top:8px">No data available</div>
        </div>
        """, unsafe_allow_html=True)
        return
    rets = prices.pct_change().dropna()
    avail = [s for s in symbols if s in rets.columns]
    corr = rets[avail].corr()
    fig = correlation_heatmap(rets[avail], 'Portfolio Dependency Matrix')
    st.plotly_chart(fig, use_container_width=True)
    avg_corr = (corr.values.sum() - len(avail)) / (len(avail)**2 - len(avail))
    risk_score = avg_corr * 100
    fig2 = gauge_chart(max(0, risk_score), 'Concentration Risk Score', 0, 100, 60)
    st.plotly_chart(fig2, use_container_width=True)
    if avg_corr > 0.6:
        st.markdown('<span class="badge badge-red">High portfolio concentration — assets are highly correlated</span>', unsafe_allow_html=True)
    elif avg_corr > 0.3:
        st.markdown('<span class="badge badge-gold">Moderate diversification — consider adding uncorrelated assets</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-green">Well diversified portfolio</span>', unsafe_allow_html=True)