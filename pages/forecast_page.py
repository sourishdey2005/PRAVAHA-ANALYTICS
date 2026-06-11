import streamlit as st
import pandas as pd
import numpy as np
from config.styles import inject_css, page_header, badge, metric_card
from analytics.data_engine import get_close_prices
from ml_models.forecasting import (run_forecast, monte_carlo_forecast,
                                     volatility_forecast, MODEL_MAP)
from visualizations.charts import (feature_importance_chart, shap_chart, backtest_chart,
                                     monte_carlo_chart, volatility_cone_chart, line_chart)

def show():
    inject_css()
    page_header("Forecast Lab", "ML-powered return & volatility forecasting with SHAP explanations", "🤖")

    col_ctrl, col_main = st.columns([1, 3], gap="large")

    with col_ctrl:
        st.markdown("#### ⚙️ Configuration")
        assets_input = st.text_input("Assets (comma-sep)", "AAPL,MSFT,SPY,GLD", key="assets_input")
        symbols = [s.strip() for s in assets_input.split(',') if s.strip()]
        target = st.selectbox("Target Asset", symbols, index=0, key="target_asset")
        model_name = st.selectbox("ML Model", list(MODEL_MAP.keys()), key="model_name")
        period = st.selectbox("Time Period", ["1y","2y","3y"], index=1)
        forecast_days = st.slider("Forecast Days", 5, 60, 20, help="Number of trading days to forecast")
        mc_sims = st.slider("Monte Carlo Simulations", 100, 2000, 500, step=100, help="Number of price paths to simulate")

        st.markdown("---")
        run_ml = st.button("🤖 Run ML Forecast", type="primary", use_container_width=True)
        run_mc = st.button("🎲 Monte Carlo", use_container_width=True)
        run_vol = st.button("📉 Volatility Forecast", use_container_width=True)

    with col_main:
        if run_ml:
            _run_ml_forecast(symbols, target, model_name, period, forecast_days)
        elif run_mc:
            _run_monte_carlo(target, period, mc_sims, forecast_days)
        elif run_vol:
            _run_volatility(target, period)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px">
                <div style="font-size:2.5rem">🤖</div>
                <div style="font-size:1.3rem;font-weight:700;color:#00d4ff;margin-top:16px">ML Forecast Lab</div>
                <div style="color:#64748b;margin-top:8px">
                    Configure assets & model in the sidebar, then choose an analysis type
                </div>
                <div style="margin-top:24px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
                    <span class="badge badge-blue">XGBoost</span>
                    <span class="badge badge-green">LightGBM</span>
                    <span class="badge badge-gold">CatBoost</span>
                    <span class="badge badge-purple">Random Forest</span>
                    <span class="badge badge-pink">SHAP Explainability</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def _run_ml_forecast(symbols, target, model_name, period, forecast_days):
    with st.spinner(f"Training {model_name} on {target}…"):
        prices = get_close_prices(symbols, period)
        if prices.empty or target not in prices.columns:
            st.markdown("""
            <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
                <div style="font-size:2rem;color:#ef4444">❌</div>
                <div style="color:#ef4444;margin-top:8px">No data available for {target}</div>
            </div>
            """, unsafe_allow_html=True)
            return
        result = run_forecast(prices, target, model_name, forecast_days)

    if result is None:
        st.error("Insufficient data for forecasting.")
        return

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Model", model_name)
    c2.metric("Direction Accuracy", f"{result['direction_accuracy']:.1%}")
    c3.metric("CV RMSE", f"{result['cv_rmse']:.6f}" if result['cv_rmse'] else 'N/A')
    c4.metric("MAE (In-Sample)", f"{result['in_sample_mae']:.6f}")

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Backtest", "🎯 Feature Importance", "🔬 SHAP", "🔮 Forecast"])

    with tab1:
        fig = backtest_chart(result['backtest_actual'], result['backtest_predicted'],
                             f'{model_name} Backtest: {target}')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if not result['feature_importance'].empty:
            fig = feature_importance_chart(result['feature_importance'], f'{model_name} Feature Importance')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(result['feature_importance'].reset_index().rename(columns={'index':'Feature', 0:'Importance'}),
                         use_container_width=True, hide_index=True)

    with tab3:
        if not result['shap_values'].empty:
            fig = shap_chart(result['shap_values'], f'SHAP Values — {target}')
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        future_rets = result['future_returns']
        prices_series = get_close_prices([target], period)[target]
        last_price = prices_series.iloc[-1]
        forecast_prices = [last_price]
        for r in future_rets:
            forecast_prices.append(forecast_prices[-1] * (1 + r))
        forecast_prices = forecast_prices[1:]
        import pandas as pd
        from pandas.tseries.offsets import BDay
        future_dates = pd.date_range(prices_series.index[-1] + BDay(1), periods=forecast_days, freq='B')
        forecast_s = pd.Series(forecast_prices, index=future_dates, name='Forecast')
        hist_s = prices_series.iloc[-60:].rename('Historical')
        combined = pd.concat([hist_s, forecast_s])
        fig = line_chart(pd.DataFrame({'Historical': hist_s, 'Forecast': forecast_s}),
                         f'{target} {forecast_days}-Day Forecast', 420)
        st.plotly_chart(fig, use_container_width=True)

        cumulative_return = (forecast_prices[-1] / last_price - 1) * 100
        direction = "▲ Bullish" if cumulative_return > 0 else "▼ Bearish"
        color = "#10b981" if cumulative_return > 0 else "#ef4444"
        st.markdown(f"""
        <div class="lead-lag-result">
            <div style="font-size:1.1rem;font-weight:700;color:{color}">{direction}</div>
            <div style="color:#94a3b8;margin-top:6px">
                Projected {forecast_days}-day return: <b style="color:{color}">{cumulative_return:+.2f}%</b>
                &nbsp;|&nbsp; Target price: <b style="color:#e2e8f0">{forecast_prices[-1]:,.2f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

def _run_monte_carlo(target, period, n_sims, forecast_days):
    with st.spinner("Running Monte Carlo simulation…"):
        prices = get_close_prices([target], period)
        if prices.empty or target not in prices.columns:
            st.markdown("""
            <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
                <div style="font-size:2rem;color:#ef4444">❌</div>
                <div style="color:#ef4444;margin-top:8px">No data available for {target}</div>
            </div>
            """, unsafe_allow_html=True)
            return
        mc = monte_carlo_forecast(prices[target], n_sims, forecast_days)
    fig = monte_carlo_chart(mc, title=f'{target} Monte Carlo ({n_sims} paths, {forecast_days}d)')
    st.plotly_chart(fig, use_container_width=True)

    last = mc['last_price']
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Price", f"{last:,.2f}")
    c2.metric("Mean Forecast", f"{mc['mean'][-1]:,.2f}")
    c3.metric("5th Percentile", f"{mc['p5'][-1]:,.2f}")
    c4.metric("95th Percentile", f"{mc['p95'][-1]:,.2f}")

def _run_volatility(target, period):
    with st.spinner("Computing volatility forecast…"):
        prices = get_close_prices([target], period)
        if prices.empty or target not in prices.columns:
            st.markdown("""
            <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
                <div style="font-size:2rem;color:#ef4444">❌</div>
                <div style="color:#ef4444;margin-top:8px">No data available for {target}</div>
            </div>
            """, unsafe_allow_html=True)
            return
        vol = volatility_forecast(prices[target])
    fig = volatility_cone_chart(vol, f'{target} Volatility Analysis')
    st.plotly_chart(fig, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Vol (Ann.)", f"{vol['current_vol']*100:.2f}%")
    c2.metric("EWM Vol Forecast", f"{vol['forecast_vol']*100:.2f}%")
    c3.metric("Regime", "High" if vol['current_vol'] > 0.3 else "Low" if vol['current_vol'] < 0.15 else "Medium")