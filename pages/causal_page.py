import streamlit as st
import pandas as pd
import numpy as np
from config.styles import inject_css, page_header, badge
from analytics.data_engine import get_close_prices
from analytics.lead_lag import (granger_causality, transfer_entropy, mutual_information,
                                   rolling_correlation, regime_detection, change_point_detection,
                                   cointegration_test)
from visualizations.charts import line_chart, cross_correlation_chart, regime_chart

def show():
    inject_css()
    page_header("Causal Intelligence", "AI-powered causal inference with regime-aware analysis", "🧠")

    col_ctrl, col_main = st.columns([1, 3], gap="large")

    with col_ctrl:
        st.markdown("#### ⚙️ Configuration")
        assets_input = st.text_input("Assets (comma-sep)", "SPY,GLD,TLT,^VIX,GC=F", key="assets_input")
        period = st.selectbox("Time Period", ["6mo","1y","2y","3y"], index=1)
        max_lag = st.slider("Max Lag (days)", 5, 30, 10, help="Lags to test for Granger causality")
        run = st.button("▶ Run Causal Analysis", type="primary", use_container_width=True)

    symbols = [s.strip() for s in assets_input.split(',') if s.strip()]

    with col_main:
        if not run:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px">
                <div style="font-size:2.5rem">🧠</div>
                <div style="font-size:1.3rem;font-weight:700;color:#00d4ff;margin-top:16px">Causal Intelligence Engine</div>
                <div style="color:#64748b;margin-top:8px">Configure assets in the sidebar and click "Run Causal Analysis"</div>
                <div style="margin-top:24px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
                    <span class="badge badge-blue">Granger Causality</span>
                    <span class="badge badge-green">Transfer Entropy</span>
                    <span class="badge badge-gold">Rolling Causality</span>
                    <span class="badge badge-purple">Regime Detection</span>
                    <span class="badge badge-pink">Change Point Detection</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        with st.spinner("Running causal analysis…"):
            prices = get_close_prices(symbols, period)

        if prices.empty:
            st.markdown("""
            <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
                <div style="font-size:2rem;color:#ef4444">❌</div>
                <div style="color:#ef4444;margin-top:8px">No data available for the selected assets</div>
            </div>
            """, unsafe_allow_html=True)
            return

        rets = prices.pct_change().dropna()
        tab1, tab2, tab3, tab4 = st.tabs(["🔗 Granger", "📡 Transfer Entropy", "🔄 Rolling Causality", "🌊 Regime Analysis"])

        with tab1:
            st.markdown("#### Granger Causality Matrix")
            st.markdown("*P-values: < 0.05 = significant causal relationship*")
            syms = [s for s in symbols if s in rets.columns]
            gc_results = {}
            for s1 in syms:
                for s2 in syms:
                    if s1 != s2:
                        gc = granger_causality(rets[s1], rets[s2], max_lag)
                        gc_results[(s1, s2)] = gc['p_value'] if gc else 1.0

            gc_df = pd.DataFrame(index=syms, columns=syms, dtype=float)
            for (s1, s2), p in gc_results.items():
                gc_df.loc[s1, s2] = p

            from visualizations.charts import _base, DARK
            import plotly.graph_objects as go
            z = gc_df.values.astype(float)
            fig = go.Figure(go.Heatmap(
                z=z, x=syms, y=syms,
                colorscale=[[0,'#10b981'],[0.05,'#f59e0b'],[1,'#0f1629']],
                zmin=0, zmax=1,
                text=np.round(z, 3), texttemplate='%{text}', textfont_size=10,
                colorbar=dict(title='p-value', thickness=12),
            ))
            fig.update_layout(**DARK, title='Granger Causality P-values (← causes →)', height=450)
            st.plotly_chart(fig, use_container_width=True)

            sig_pairs = [(s1, s2, p) for (s1, s2), p in gc_results.items() if p < 0.05]
            if sig_pairs:
                st.markdown("#### Significant Causal Pairs (p < 0.05)")
                for s1, s2, p in sorted(sig_pairs, key=lambda x: x[2]):
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:10px 14px;
                    background:#151d35;border-radius:10px;margin:4px 0;border-left:3px solid #10b981">
                        <span><b style="color:#00d4ff">{s1}</b> <span style="color:#64748b">→ causes →</span>
                        <b style="color:#7c3aed">{s2}</b></span>
                        <span class="badge badge-green">p={p:.4f}</span>
                    </div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown("#### Transfer Entropy Analysis")
            st.markdown("*Transfer Entropy measures directional information flow between assets.*")
            te_rows = []
            for s1 in syms[:6]:
                for s2 in syms[:6]:
                    if s1 != s2:
                        te = transfer_entropy(rets[s1], rets[s2])
                        if te is not None:
                            te_rows.append({'From': s1, 'To': s2, 'Transfer Entropy': round(te, 4)})
            if te_rows:
                te_df = pd.DataFrame(te_rows).sort_values('Transfer Entropy', ascending=False)
                st.dataframe(te_df, use_container_width=True, hide_index=True)
                st.markdown("#### Top Information Flows")
                for _, row in te_df.head(5).iterrows():
                    st.markdown(f"""
                    <div class="lead-lag-result">
                        <span style="color:#00d4ff;font-weight:700">{row['From']}</span>
                        <span style="color:#64748b"> → (TE={row['Transfer Entropy']:.4f}) → </span>
                        <span style="color:#7c3aed;font-weight:700">{row['To']}</span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("Insufficient data for Transfer Entropy calculation")

        with tab3:
            st.markdown("#### Rolling Causality Windows")
            if len(syms) >= 2:
                s1 = st.selectbox("Asset 1", syms, index=0, key='rc1')
                s2 = st.selectbox("Asset 2", syms, index=min(1, len(syms)-1), key='rc2')
                windows = [20, 30, 60]
                for w in windows:
                    rc = rolling_correlation(rets[s1], rets[s2], w)
                    if not rc.empty:
                        fig = line_chart(rc.rename(f'Rolling Corr (w={w})'), f'{s1} ↔ {s2} Rolling {w}d Correlation', 300)
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need at least 2 assets for rolling causality")

        with tab4:
            st.markdown("#### Regime-Aware Analysis")
            sym_regime = st.selectbox("Asset for Regime Detection", syms, key='regime_sym')
            if sym_regime in prices.columns:
                states = regime_detection(prices[sym_regime])
                if states is not None:
                    fig = regime_chart(prices[sym_regime], states, f'{sym_regime} Market Regimes')
                    st.plotly_chart(fig, use_container_width=True)
                    bkps = change_point_detection(prices[sym_regime])
                    if bkps:
                        st.markdown(f"**{len(bkps)} structural breakpoints detected**")
                        bkp_dates = [str(prices.index[min(b-1, len(prices)-1)].date()) for b in bkps if b < len(prices)]
                        st.write(", ".join(bkp_dates))
                else:
                    st.warning("Regime detection requires hmmlearn package.")
            else:
                st.info("Select an asset for regime analysis")