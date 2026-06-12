import streamlit as st
import numpy as np
import pandas as pd
from config.styles import inject_css, page_header
from analytics.data_engine import get_close_prices
from visualizations.charts import (surface_3d, lead_lag_surface_3d, pca_3d,
                                    correlation_heatmap, monte_carlo_chart)
from network_engine.network import network_3d, build_lead_lag_network, compute_network_metrics

def show():
    inject_css()
    page_header("3D Analytics Lab", "Immersive 3D financial visualization", "🌐")

    col_ctrl, col_main = st.columns([1, 3])
    with col_ctrl:
        assets_input = st.text_input("Assets", "SPY,QQQ,GLD,TLT,^VIX,GC=F,CL=F,DX-Y.NYB")
        symbols = [s.strip() for s in assets_input.split(',') if s.strip()]
        period = st.selectbox("Period", ["6mo","1y","2y"], index=1)
        chart_3d = st.selectbox("3D Chart", [
            "Correlation Surface", "Lead-Lag Surface", "PCA Space",
            "Volatility Surface", "Network 3D", "Regime Clusters"
        ])
        load = st.button("🌐 Render 3D", type="primary", use_container_width=True)

    with col_main:
        if not load:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px">
                <div style="font-size:4rem">🌐</div>
                <div style="font-size:1.4rem;font-weight:700;color:#00d4ff;margin-top:16px">3D Analytics Lab</div>
                <div style="color:#64748b;margin-top:8px">Configure assets and select a 3D chart type</div>
            </div>""", unsafe_allow_html=True)
            return

        with st.spinner("Computing 3D visualization…"):
            prices = get_close_prices(symbols, period)
        if prices.empty:
            st.error("No data."); return
        rets = prices.pct_change().dropna()
        syms = [s for s in symbols if s in rets.columns]

        if chart_3d == "Correlation Surface":
            corr = rets[syms[:12]].corr()
            fig = surface_3d(corr.values, list(corr.columns), list(corr.index), '3D Correlation Surface')
            st.plotly_chart(fig, use_container_width=True)
            st.info("Z-axis represents correlation coefficient between asset pairs. Colors indicate strength.")

        elif chart_3d == "Lead-Lag Surface":
            fig = lead_lag_surface_3d(rets[syms[:8]], max_lag=20)
            st.plotly_chart(fig, use_container_width=True)
            st.info("Surface shows cross-correlation at each lag between assets and the reference asset.")

        elif chart_3d == "PCA Space":
            if len(syms) >= 3:
                fig = pca_3d(rets[syms])
                st.plotly_chart(fig, use_container_width=True)
                from sklearn.decomposition import PCA
                pca = PCA(n_components=3)
                pca.fit(rets[syms].dropna().T)
                ev = pca.explained_variance_ratio_
                c1, c2, c3 = st.columns(3)
                c1.metric("PC1 Variance", f"{ev[0]:.1%}")
                c2.metric("PC2 Variance", f"{ev[1]:.1%}")
                c3.metric("PC3 Variance", f"{ev[2]:.1%}")
            else:
                st.warning("Need at least 3 assets for PCA.")

        elif chart_3d == "Volatility Surface":
            windows = [5, 10, 20, 30, 60]
            vol_matrix = np.zeros((len(syms[:8]), len(windows)))
            for i, sym in enumerate(syms[:8]):
                for j, w in enumerate(windows):
                    vol_matrix[i, j] = rets[sym].rolling(w).std().iloc[-1] * np.sqrt(252) * 100
            fig = surface_3d(vol_matrix, [f'{w}d' for w in windows], syms[:8], '3D Volatility Surface')
            st.plotly_chart(fig, use_container_width=True)
            st.info("X: rolling window, Y: asset, Z: annualized volatility (%)")

        elif chart_3d == "Network 3D":
            from analytics.lead_lag import compute_lead_lag_matrix
            with st.spinner("Building network…"):
                ll_df = compute_lead_lag_matrix(rets[syms[:10]], max_lag=15)
            G = build_lead_lag_network(ll_df, min_confidence=0.2)
            metrics = compute_network_metrics(G)
            fig = network_3d(G, metrics)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_3d == "Regime Clusters":
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            import plotly.graph_objects as go
            feat_df = rets[syms].dropna()
            if len(feat_df) < 30:
                st.warning("Not enough data."); return
            from sklearn.decomposition import PCA
            pca = PCA(n_components=3)
            pca_vals = pca.fit_transform(feat_df)
            n_clusters = 3
            km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = km.fit_predict(pca_vals)
            colors_c = ['#00d4ff','#7c3aed','#f59e0b','#10b981','#ef4444']
            fig = go.Figure()
            for c in range(n_clusters):
                mask = labels == c
                fig.add_trace(go.Scatter3d(
                    x=pca_vals[mask,0], y=pca_vals[mask,1], z=pca_vals[mask,2],
                    mode='markers', marker=dict(size=4, color=colors_c[c], opacity=0.7),
                    name=f'Regime {c+1}'
                ))
            fig.update_layout(
                title='3D Market Regime Clusters', paper_bgcolor='#0a0e1a',
                font=dict(color='#e2e8f0'),
                scene=dict(bgcolor='#0a0e1a',
                           xaxis=dict(title='PC1', backgroundcolor='#0a0e1a', gridcolor='#1e293b'),
                           yaxis=dict(title='PC2', backgroundcolor='#0a0e1a', gridcolor='#1e293b'),
                           zaxis=dict(title='PC3', backgroundcolor='#0a0e1a', gridcolor='#1e293b')),
                height=600,
            )
            st.plotly_chart(fig, use_container_width=True)
