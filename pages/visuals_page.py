import streamlit as st
import pandas as pd
import numpy as np
from config.styles import inject_css, page_header
from analytics.data_engine import get_close_prices
from visualizations import charts as C

def show():
    inject_css()
    page_header("Visual Analytics Lab", "50+ interactive charts for financial analysis", "📊")

    col_ctrl, col_main = st.columns([1, 3])
    with col_ctrl:
        assets_input = st.text_input("Assets", "AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA")
        symbols = [s.strip() for s in assets_input.split(',') if s.strip()]
        period = st.selectbox("Period", ["3mo","6mo","1y","2y"], index=2)
        load = st.button("📊 Load & Visualize", type="primary", use_container_width=True)

    with col_main:
        if not load:
            _chart_gallery()
            return

        with st.spinner("Loading data…"):
            prices = get_close_prices(symbols, period)
        if prices.empty:
            st.error("No data."); return
        rets = prices.pct_change().dropna()

        cat = st.selectbox("Chart Category", [
            "💰 Financial", "📈 Line & Area", "📊 Statistical",
            "🟥 Matrix & Heatmaps", "📉 Bar Charts", "🧩 Advanced",
            "🤖 ML Charts", "🌐 3D Charts"
        ])

        if cat == "💰 Financial":
            sym = st.selectbox("Symbol", symbols, key='fin_sym')
            from analytics.data_engine import get_prices
            raw = get_prices([sym], period).get(sym, prices[[sym]])
            fig = C.candlestick_volume(raw, sym)
            st.plotly_chart(fig, use_container_width=True)
            fig2 = C.ohlc_chart(raw, sym)
            st.plotly_chart(fig2, use_container_width=True)

        elif cat == "📈 Line & Area":
            st.plotly_chart(C.line_chart(prices[symbols[:6]], 'Prices'), use_container_width=True)
            st.plotly_chart(C.area_chart(prices[symbols[:4]], 'Area Chart'), use_container_width=True)
            norm = prices / prices.iloc[0] * 100
            st.plotly_chart(C.stacked_area_chart(norm[symbols[:4]], 'Stacked Area'), use_container_width=True)

        elif cat == "📊 Statistical":
            sym = st.selectbox("Symbol", symbols, key='stat_sym')
            r = rets[sym]
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(C.histogram(r, f'{sym} Returns Histogram'), use_container_width=True)
                st.plotly_chart(C.density_plot(r, f'{sym} Density'), use_container_width=True)
            with c2:
                st.plotly_chart(C.box_plot(rets[symbols[:6]], 'Box Plot'), use_container_width=True)
                st.plotly_chart(C.violin_plot(rets[symbols[:4]], 'Violin Plot'), use_container_width=True)
            st.plotly_chart(C.returns_distribution(r, f'{sym} Full Distribution'), use_container_width=True)
            if len(symbols) >= 2:
                st.plotly_chart(C.scatter_plot(rets[symbols[0]], rets[symbols[1]],
                                               f'{symbols[0]} vs {symbols[1]}',
                                               symbols[0], symbols[1]), use_container_width=True)

        elif cat == "🟥 Matrix & Heatmaps":
            st.plotly_chart(C.correlation_heatmap(rets[symbols[:8]], 'Correlation Matrix'), use_container_width=True)
            pairs = [(symbols[0], symbols[1])] if len(symbols) >= 2 else []
            st.plotly_chart(C.rolling_corr_heatmap(rets, pairs[:3], title='Rolling Correlation Heatmap'), use_container_width=True)

        elif cat == "📉 Bar Charts":
            last_rets = rets.iloc[-1] * 100
            st.plotly_chart(C.bar_chart(list(last_rets.index), list(last_rets.values),
                                         'Last Day Returns (%)', color=True), use_container_width=True)
            monthly = rets.resample('ME').sum() * 100
            st.plotly_chart(C.grouped_bar(monthly.tail(12), 'Monthly Returns (%)'), use_container_width=True)
            wf_vals = list(rets[symbols[0]].resample('ME').sum().tail(8) * 100)
            wf_cats = [f'M{i+1}' for i in range(len(wf_vals))]
            st.plotly_chart(C.waterfall_chart(wf_cats, wf_vals, f'{symbols[0]} Waterfall'), use_container_width=True)

        elif cat == "🧩 Advanced":
            # Treemap: market cap proxy = volatility
            vols = rets.std() * 100
            fig = C.treemap(list(vols.index), ['']*len(vols), list(vols.values), 'Asset Volatility Treemap')
            st.plotly_chart(fig, use_container_width=True)
            fig2 = C.sunburst(list(vols.index), ['']*len(vols), list(vols.values), 'Asset Sunburst')
            st.plotly_chart(fig2, use_container_width=True)
            # Radar
            r_data = {sym: [abs(rets[sym].mean()*252)*100, rets[sym].std()*np.sqrt(252)*100,
                             (rets[sym].mean()/rets[sym].std()*np.sqrt(252)) if rets[sym].std()>0 else 0,
                             abs(rets[sym].skew()), rets[sym].kurtosis()+3]
                      for sym in symbols[:4] if sym in rets.columns}
            fig3 = C.radar_chart(['Return','Volatility','Sharpe','Skew','Kurtosis'], r_data, 'Asset Radar')
            st.plotly_chart(fig3, use_container_width=True)
            fig4 = C.gauge_chart(50, 'Sample Gauge', 0, 100)
            st.plotly_chart(fig4, use_container_width=True)

        elif cat == "🤖 ML Charts":
            from sklearn.linear_model import ElasticNet
            from sklearn.preprocessing import StandardScaler
            sym = symbols[0]
            r = rets[sym].dropna()
            X = pd.DataFrame({f'lag_{i}': r.shift(i) for i in range(1,11)}).dropna()
            y = r[X.index]
            scaler = StandardScaler()
            Xs = scaler.fit_transform(X)
            model = ElasticNet().fit(Xs, y)
            import pandas as pd_inner
            fi = pd_inner.Series(np.abs(model.coef_), index=X.columns)
            st.plotly_chart(C.feature_importance_chart(fi.sort_values(ascending=False), 'Feature Importance'), use_container_width=True)
            preds = pd_inner.Series(model.predict(Xs), index=y.index)
            st.plotly_chart(C.backtest_chart(y, preds, 'ElasticNet Backtest'), use_container_width=True)

        elif cat == "🌐 3D Charts":
            corr = rets[symbols[:8]].corr()
            fig = C.surface_3d(corr.values, list(corr.columns), list(corr.index), '3D Correlation Surface')
            st.plotly_chart(fig, use_container_width=True)
            fig2 = C.lead_lag_surface_3d(rets[symbols[:8]], max_lag=15)
            st.plotly_chart(fig2, use_container_width=True)
            if len(symbols) >= 3:
                fig3 = C.pca_3d(rets[symbols])
                st.plotly_chart(fig3, use_container_width=True)

def _chart_gallery():
    categories = [
        ("💰", "Financial Charts", "Candlestick, OHLC, Volume Profile"),
        ("📈", "Line & Area", "Line, Area, Stacked Area"),
        ("📊", "Statistical", "Histogram, Density, Box, Violin, Scatter"),
        ("🟥", "Matrix & Heatmaps", "Correlation, Lag, Rolling Heatmaps"),
        ("📉", "Bar Charts", "Bar, Grouped, Stacked, Waterfall"),
        ("🧩", "Advanced", "Treemap, Sunburst, Radar, Gauge, Sankey"),
        ("🤖", "ML Charts", "Feature Importance, SHAP, Backtest"),
        ("🌐", "3D Charts", "Surface, PCA, Network 3D"),
    ]
    cols = st.columns(4)
    for i, (icon, name, desc) in enumerate(categories):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:20px;height:130px">
                <div style="font-size:2rem">{icon}</div>
                <div style="font-weight:700;color:#00d4ff;font-size:0.9rem;margin-top:6px">{name}</div>
                <div style="font-size:0.7rem;color:#64748b;margin-top:4px">{desc}</div>
            </div>""", unsafe_allow_html=True)
    st.info("Load assets using the sidebar controls above to explore all chart types.")
