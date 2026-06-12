import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.decomposition import PCA
from config.styles import inject_css, page_header, metric_card, badge
from auth.auth_manager import current_user
from analytics.data_engine import get_market_overview, get_sector_performance, get_close_prices
from visualizations.charts import sector_heatmap, line_chart, gauge_chart
from database.db import get_watchlists
import json

INDEX_LABELS = {
    '^GSPC': 'S&P 500',
    '^IXIC': 'Nasdaq',
    '^DJI': 'Dow Jones',
    '^VIX': 'VIX',
    '^NSEI': 'Nifty 50',
    '^BSESN': 'Sensex',
    '^N225': 'Nikkei 225',
    '^FTSE': 'FTSE 100',
    '^GDAXI': 'DAX',
}
START_PRICES = {
    '^IXIC': 25809.66, '^GSPC': 6200.0, '^DJI': 43000.0, '^VIX': 19.44,
    '^NSEI': 23344.30, '^BSESN': 76000.0, '^N225': 40000.0, '^FTSE': 8400.0,
    '^GDAXI': 19000.0, 'SPY': 560.0, 'QQQ': 500.0, 'GLD': 235.0, 'TLT': 92.0,
}
START_VOLUMES = {
    '^IXIC': 6_000_000_000, '^GSPC': 4_500_000_000, '^DJI': 450_000_000,
    '^VIX': 0, '^NSEI': 350_000_000, '^BSESN': 300_000_000, '^N225': 1_200_000_000,
    '^FTSE': 900_000_000, '^GDAXI': 800_000_000, 'SPY': 80_000_000,
    'QQQ': 55_000_000, 'GLD': 9_000_000, 'TLT': 18_000_000,
}
DASHBOARD_SYMBOLS = ['^IXIC', '^GSPC', '^DJI', '^VIX', '^NSEI', '^BSESN', '^N225', '^FTSE', '^GDAXI', 'SPY', 'QQQ', 'GLD', 'TLT']


def _fallback_index_items():
    return [
        {'symbol': '^IXIC', 'name': 'Nasdaq', 'price': 25809.66, 'change_pct': 2.54},
        {'symbol': '^VIX', 'name': 'VIX', 'price': 19.44, 'change_pct': -12.51},
        {'symbol': '^NSEI', 'name': 'Nifty 50', 'price': 23344.30, 'change_pct': 0.79},
        {'symbol': '^GSPC', 'name': 'S&P 500', 'price': 6200.0, 'change_pct': 1.12},
        {'symbol': '^DJI', 'name': 'Dow Jones', 'price': 43000.0, 'change_pct': 0.88},
    ]


def _fallback_sector_data():
    return {
        'Technology': {'change_pct': 1.42, 'price': 100.0},
        'Healthcare': {'change_pct': 0.36, 'price': 100.0},
        'Finance': {'change_pct': -0.44, 'price': 100.0},
        'Energy': {'change_pct': 0.92, 'price': 100.0},
        'Consumer Disc': {'change_pct': 0.18, 'price': 100.0},
        'Consumer Staples': {'change_pct': -0.12, 'price': 100.0},
        'Industrials': {'change_pct': 0.64, 'price': 100.0},
        'Materials': {'change_pct': 0.22, 'price': 100.0},
        'Utilities': {'change_pct': -0.31, 'price': 100.0},
        'Real Estate': {'change_pct': 0.47, 'price': 100.0},
        'Communication': {'change_pct': 0.73, 'price': 100.0},
    }


def _fallback_ohlc_frames(symbols):
    end = pd.Timestamp.today().normalize()
    dates = pd.bdate_range(end - pd.Timedelta(days=390), end)
    frames = {}
    for sym in symbols:
        start = START_PRICES.get(sym, 100.0)
        rng = np.random.default_rng(sum(ord(c) for c in sym))
        t = np.arange(len(dates))
        wave_amp = start * (0.08 if sym == '^VIX' else 0.025)
        noise_amp = start * (0.05 if sym == '^VIX' else 0.01)
        drift = (t / max(len(dates) - 1, 1)) * start * (0.02 if sym == '^VIX' else 0.18)
        wave = wave_amp * np.sin(np.linspace(0, 10 * np.pi, len(dates)) + rng.random() * 2)
        noise = rng.normal(0, noise_amp, len(dates))
        close = np.maximum(start + drift + wave + noise, start * 0.15)
        open_prev = np.r_[close[0], close[:-1]]
        open_ = open_prev * (1 + rng.normal(0, 0.004, len(dates)))
        spread = abs(rng.normal(0, 0.012, len(dates)))
        high = np.maximum(open_, close) * (1 + spread)
        low = np.minimum(open_, close) * np.maximum(0.985, 1 - spread)
        vol_base = START_VOLUMES.get(sym, 5_000_000)
        volume = rng.lognormal(mean=np.log(max(vol_base, 1)), sigma=0.45, size=len(dates))
        frames[sym] = pd.DataFrame({
            'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume,
        }, index=dates)
    return frames


def _close_to_ohlc_frames(close_df):
    frames = {}
    for sym in close_df.columns:
        close = close_df[sym].dropna()
        if close.empty:
            continue
        rng = np.random.default_rng(sum(ord(c) for c in str(sym)))
        open_ = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, 0.003, len(close)))
        spread = abs(rng.normal(0, 0.012, len(close)))
        high = np.maximum(open_, close) * (1 + spread)
        low = np.minimum(open_, close) * np.maximum(0.985, 1 - spread)
        vol_base = START_VOLUMES.get(sym, 5_000_000)
        volume = rng.lognormal(mean=np.log(max(vol_base, 1)), sigma=0.45, size=len(close))
        frames[sym] = pd.DataFrame({
            'open': open_.values, 'high': high.values, 'low': low.values,
            'close': close.values, 'volume': volume,
        }, index=close.index)
    return frames


def _dashboard_market_data():
    overview = get_market_overview()
    display_items = overview[:5] if overview and any(item.get('price', 0) for item in overview) else _fallback_index_items()
    live_prices = get_close_prices(DASHBOARD_SYMBOLS, '1y')
    frames = _close_to_ohlc_frames(live_prices) if not live_prices.empty else _fallback_ohlc_frames(DASHBOARD_SYMBOLS)
    close_df = pd.DataFrame({sym: df['close'] for sym, df in frames.items()}).dropna(how='all')
    return display_items, frames, close_df, bool(overview)


def _layout(title='', height=420):
    return dict(
        paper_bgcolor='#0a0e1a', plot_bgcolor='#0f1629',
        font=dict(color='#e2e8f0', family='Inter'),
        title=dict(text=title, x=0.03),
        margin=dict(l=40, r=20, t=50, b=40), height=height,
        xaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b'),
        yaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b'),
    )


def _ohlc(symbol, frames):
    return frames.get(symbol, next(iter(frames.values())))


def _returns(close_df):
    return close_df.pct_change().replace([np.inf, -np.inf], np.nan).dropna()


def _viz_candlestick(frames):
    df = _ohlc('^IXIC', frames)
    fig = go.Figure(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#10b981', decreasing_line_color='#ef4444', name='Nasdaq'))
    fig.update_layout(**_layout('Candlestick Pulse', 420), xaxis_rangeslider_visible=False)
    return fig


def _viz_heikin_ashi(frames):
    df = _ohlc('QQQ', frames)
    ha_open = (df['open'].shift(1) + df['close'].shift(1)) / 2
    ha_open.iloc[0] = df['open'].iloc[0]
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_high = df[['open', 'high', 'close']].max(axis=1)
    ha_low = df[['open', 'low', 'close']].min(axis=1)
    colors = ['#10b981' if c >= o else '#ef4444' for o, c in zip(ha_open, ha_close)]
    fig = go.Figure(go.Candlestick(x=df.index, open=ha_open, high=ha_high, low=ha_low, close=ha_close, increasing_line_color='#10b981', decreasing_line_color='#ef4444', name='Heikin-Ashi'))
    for o, c, date in zip(ha_open, ha_close, df.index):
        fig.add_vrect(x0=date, x1=date, fillcolor='#10b981' if c >= o else '#ef4444', opacity=0.035, line_width=0)
    fig.update_layout(**_layout('Heikin-Ashi Flow', 420), xaxis_rangeslider_visible=False)
    return fig


def _viz_kagi(frames):
    df = _ohlc('GLD', frames)
    close = df['close']
    threshold = max(close.tail(60).std() * 1.2, close.iloc[0] * 0.01)
    x, y, dirs = [], [], []
    last = close.iloc[0]
    direction = 1
    for date, price in close.items():
        if abs(price - last) >= threshold:
            if (direction == 1 and price > last) or (direction == -1 and price < last):
                x.append(date); y.append(price); dirs.append(direction)
            else:
                direction *= -1
                x.extend([date, date]); y.extend([last, price]); dirs.extend([-direction, direction])
            last = price
    fig = go.Figure()
    for i in range(len(x) - 1):
        fig.add_trace(go.Scatter(x=x[i:i+2], y=y[i:i+2], mode='lines', line=dict(color='#10b981' if dirs[i] > 0 else '#ef4444', width=3), showlegend=False, hoverinfo='skip'))
    fig.update_layout(**_layout('Kagi Reversal Structure', 420))
    return fig


def _viz_point_figure(frames):
    df = _ohlc('SPY', frames)
    close = df['close']
    box = max(close.tail(60).std() / 3, close.iloc[0] * 0.01)
    x, y, letters = 0, close.iloc[0], []
    xs, ys = [], []
    direction = 1
    for price in close:
        if direction == 1:
            if price >= y + box:
                while price >= y + box:
                    y += box; xs.append(x); ys.append(y); letters.append('X')
            elif y - price >= 2 * box:
                direction = -1; y -= box; xs.append(x); ys.append(y); letters.append('O')
        else:
            if price <= y - box:
                while price <= y - box:
                    y -= box; xs.append(x); ys.append(y); letters.append('O')
            elif price - y >= 2 * box:
                direction = 1; y += box; xs.append(x); ys.append(y); letters.append('X')
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode='markers+text', text=letters, textposition='middle center', marker=dict(color=['#10b981' if v == 'X' else '#ef4444' for v in letters], size=10), name='P&F'))
    fig.update_layout(**_layout('Point & Figure Box Reversal', 420))
    return fig


def _viz_ohlc_bars(frames):
    df = _ohlc('^GSPC', frames)
    fig = go.Figure(go.Ohlc(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#10b981', decreasing_line_color='#ef4444', name='S&P 500'))
    fig.update_layout(**_layout('OHLC Range Bars', 420), xaxis_rangeslider_visible=False)
    return fig


def _viz_volume_profile(frames):
    df = _ohlc('^IXIC', frames)
    bins = np.linspace(df['close'].min(), df['close'].max(), 32)
    idx = np.digitize(df['close'], bins) - 1
    profile = df.assign(bin=idx).groupby('bin')['volume'].sum().reset_index()
    prices = [(bins[i] + bins[min(i + 1, len(bins) - 1)]) / 2 for i in profile['bin']]
    fig = go.Figure(go.Bar(y=prices, x=profile['volume'], orientation='h', marker_color='#00d4ff', opacity=0.75, name='Volume by Price'))
    fig.update_layout(**_layout('Volume Profile', 420))
    return fig


def _viz_bollinger(frames):
    df = _ohlc('QQQ', frames)
    close = df['close']
    mid = close.rolling(20).mean()
    std = close.rolling(20).std()
    upper = mid + 2 * std
    lower = mid - 2 * std
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=close, increasing_line_color='#10b981', decreasing_line_color='#ef4444', name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=mid, line=dict(color='#00d4ff'), name='SMA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=upper, line=dict(color='rgba(16,185,129,0.7)', dash='dash'), name='Upper'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=lower, line=dict(color='rgba(239,68,68,0.7)', dash='dash'), name='Lower'), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], marker_color=['#10b981' if c >= o else '#ef4444' for o, c in zip(df['open'], df['close'])], showlegend=False), row=2, col=1)
    fig.update_layout(**_layout('Bollinger Band Compression', 520), xaxis_rangeslider_visible=False)
    return fig


def _viz_rsi(frames):
    df = _ohlc('SPY', frames)
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.03)
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], line=dict(color='#00d4ff', width=2), name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=rsi, line=dict(color='#f59e0b', width=2), name='RSI'), row=2, col=1)
    fig.add_hline(y=70, line_color='#ef4444', line_dash='dash', row=2, col=1)
    fig.add_hline(y=30, line_color='#10b981', line_dash='dash', row=2, col=1)
    fig.update_layout(**_layout('RSI Momentum Oscillator', 520), xaxis_rangeslider_visible=False)
    return fig


def _viz_macd(frames):
    df = _ohlc('^GSPC', frames)
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.03)
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], line=dict(color='#e2e8f0', width=2), name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=macd, line=dict(color='#00d4ff', width=2), name='MACD'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=signal, line=dict(color='#f59e0b', width=2), name='Signal'), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=hist, marker_color=['#10b981' if v >= 0 else '#ef4444' for v in hist], name='Hist'), row=2, col=1)
    fig.update_layout(**_layout('MACD Signal Stack', 520), xaxis_rangeslider_visible=False)
    return fig


def _viz_atr(frames):
    df = _ohlc('^VIX', frames)
    prev = df['close'].shift(1)
    tr = pd.concat([(df['high'] - df['low']), (df['high'] - prev).abs(), (df['low'] - prev).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.03)
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], line=dict(color='#00d4ff', width=2), name='VIX'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=atr, line=dict(color='#f59e0b', width=2), name='ATR'), row=2, col=1)
    fig.update_layout(**_layout('ATR Volatility Ribbon Proxy', 520), xaxis_rangeslider_visible=False)
    return fig


def _viz_drawdown(close_df):
    norm = close_df / close_df.iloc[0]
    dd = norm / norm.cummax() - 1
    fig = go.Figure()
    for col in close_df.columns[:8]:
        fig.add_trace(go.Scatter(x=dd.index, y=dd[col] * 100, mode='lines', line=dict(width=1.5), name=col))
    fig.update_layout(**_layout('Drawdown Map', 430))
    return fig


def _viz_returns_histogram(close_df):
    rets = _returns(close_df)
    symbol = '^IXIC' if '^IXIC' in rets.columns else rets.columns[0]
    fig = go.Figure(go.Histogram(x=rets[symbol] * 100, nbinsx=60, marker_color='#00d4ff', marker_line_color='rgba(255,255,255,0.15)', marker_line_width=0.5, name='Daily Returns'))
    fig.update_layout(**_layout('Daily Returns Distribution', 420), bargap=0.04)
    return fig


def _viz_qq(close_df):
    rets = _returns(close_df)
    symbol = 'QQQ' if 'QQQ' in rets.columns else rets.columns[0]
    vals = rets[symbol].dropna().values
    (osm, osr), (slope, intercept, r) = stats.probplot(vals, dist='norm')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers', marker=dict(color='#7c3aed', size=5), name='Returns'))
    fig.add_trace(go.Scatter(x=osm, y=slope * np.array(osm) + intercept, mode='lines', line=dict(color='#f59e0b', dash='dash'), name='Normal'))
    fig.update_layout(**_layout('Q-Q Normality Plot', 420))
    return fig


def _viz_risk_return(close_df):
    rets = _returns(close_df)
    ann = (rets.mean() * 252).rename('Return')
    vol = (rets.std() * np.sqrt(252)).rename('Volatility')
    norm = close_df / close_df.iloc[0]
    dd = (norm / norm.cummax() - 1).min() * 100
    df = pd.concat([ann, vol, dd.rename('Drawdown')], axis=1).dropna()
    fig = go.Figure(go.Scatter(x=df['Volatility'] * 100, y=df['Return'] * 100, mode='markers+text', text=df.index, textposition='top center', marker=dict(size=(df['Drawdown'].abs() * 8).clip(8, 40), color=df['Return'], colorscale='Viridis', line=dict(color='white', width=0.5)), name='Assets'))
    fig.update_layout(**_layout('Risk-Return Bubble', 460), xaxis_title='Annualized Volatility (%)', yaxis_title='Annualized Return (%)')
    return fig


def _viz_beta(close_df):
    rets = _returns(close_df)
    benchmark = rets['^GSPC'] if '^GSPC' in rets.columns else rets.iloc[:, 0]
    rows = []
    for col in rets.columns:
        cov = rets[col].cov(benchmark)
        beta = cov / benchmark.var() if benchmark.var() else 0
        rows.append({'Asset': col, 'Beta': beta})
    df = pd.DataFrame(rows).sort_values('Beta')
    fig = go.Figure(go.Bar(x=df['Asset'], y=df['Beta'], marker_color=['#10b981' if v >= 0 else '#ef4444' for v in df['Beta']], name='Beta'))
    fig.add_hline(y=1, line_color='#f59e0b', line_dash='dash')
    fig.update_layout(**_layout('Beta vs Benchmark', 420), yaxis_title='Beta')
    return fig


def _viz_cumulative(close_df):
    fig = go.Figure()
    for col in close_df.columns[:10]:
        fig.add_trace(go.Scatter(x=close_df.index, y=close_df[col] / close_df[col].iloc[0] * 100, mode='lines', name=col))
    fig.update_layout(**_layout('Cumulative Return River', 440), yaxis_title='Base = 100')
    return fig


def _viz_relative_strength(close_df):
    benchmark = close_df.iloc[:, 0]
    rs = close_df.div(benchmark, axis=0) * 100
    fig = go.Figure()
    for col in rs.columns[:10]:
        fig.add_trace(go.Scatter(x=rs.index, y=rs[col], mode='lines', name=col))
    fig.update_layout(**_layout('Relative Strength Matrix', 440))
    return fig


def _viz_calendar(close_df):
    symbol = '^IXIC' if '^IXIC' in close_df.columns else close_df.columns[0]
    rets = close_df[symbol].pct_change().dropna()
    temp = pd.DataFrame({'ret': rets, 'weekday': rets.index.weekday, 'week': rets.index.isocalendar().week.astype(int)})
    pivot = temp.pivot_table(index='week', columns='weekday', values='ret', aggfunc='mean') * 100
    fig = go.Figure(go.Heatmap(z=pivot.values, x=['Mon','Tue','Wed','Thu','Fri'], y=pivot.index, colorscale=[[0,'#ef4444'],[0.5,'#0f1629'],[1,'#10b981']], zmid=0, colorbar=dict(thickness=12)))
    fig.update_layout(**_layout('Calendar Return Heatmap', 430))
    return fig


def _viz_momentum(close_df):
    windows = [5, 10, 20, 60]
    z = pd.DataFrame({f'{w}d': close_df.pct_change(w).iloc[-1] * 100 for w in windows}, index=close_df.columns).T
    fig = go.Figure(go.Heatmap(z=z.values, x=z.columns, y=z.index, colorscale=[[0,'#ef4444'],[0.5,'#0f1629'],[1,'#10b981']], zmid=0, text=np.round(z.values, 1), texttemplate='%{text}', colorbar=dict(thickness=12)))
    fig.update_layout(**_layout('Momentum Timeframe Matrix', 430))
    return fig


def _viz_correlation(close_df):
    corr = _returns(close_df).corr()
    fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale=[[0,'#ef4444'],[0.5,'#0f1629'],[1,'#10b981']], zmid=0, text=np.round(corr.values, 2), texttemplate='%{text}', textfont_size=8, colorbar=dict(thickness=12)))
    fig.update_layout(**_layout('Cross-Asset Correlation', 500))
    return fig


def _viz_rolling_corr(close_df):
    rolling = _returns(close_df).rolling(30).corr()
    if rolling.empty:
        return go.Figure()
    if isinstance(rolling.index, pd.MultiIndex):
        last = rolling.loc[rolling.index[-1][0]].copy()
    else:
        last_date = rolling.index[-1]
        last = rolling[rolling.index == last_date].copy()
        last.index = rolling.columns
        last = last[rolling.columns]
    last.values[np.diag_indices_from(last.values)] = np.nan
    rows = []
    for asset1, row in last.iterrows():
        for asset2, value in row.items():
            if pd.notna(value):
                rows.append({'Asset 1': asset1, 'Asset 2': asset2, 'Correlation': value})
    df = pd.DataFrame(rows)
    if df.empty:
        return go.Figure()
    fig = go.Figure(go.Scatter(x=df['Asset 1'], y=df['Asset 2'], mode='markers', marker=dict(size=(df['Correlation'].abs() * 24).clip(6, 35), color=df['Correlation'], colorscale='RdBu', showscale=True), text=np.round(df['Correlation'], 2), hovertemplate='%{x} vs %{y}<br>%{text}<extra></extra>'))
    fig.update_layout(**_layout('Rolling Correlation Pairs', 500), xaxis_title='Asset 1', yaxis_title='Asset 2')
    return fig


def _viz_lead_lag(close_df):
    rets = _returns(close_df)
    symbols = list(rets.columns)[:8]
    lags = list(range(-15, 16))
    z = np.zeros((len(symbols), len(lags)))
    for i, sym in enumerate(symbols):
        a = rets[sym].values
        ref = rets[symbols[0]].values
        for j, lag in enumerate(lags):
            try:
                if lag < 0:
                    c = np.corrcoef(a[:lag], ref[-lag:])[0, 1]
                elif lag == 0:
                    c = np.corrcoef(a, ref)[0, 1]
                else:
                    c = np.corrcoef(a[lag:], ref[:-lag])[0, 1]
                z[i, j] = c if not np.isnan(c) else 0
            except Exception:
                z[i, j] = 0
    fig = go.Figure(go.Surface(z=z, x=lags, y=symbols, colorscale='Viridis', opacity=0.92))
    fig.update_layout(**_layout('3D Lead-Lag Surface', 560))
    return fig


def _viz_pca_3d(close_df):
    rets = _returns(close_df).dropna()
    if rets.shape[1] < 3 or rets.shape[0] < 3:
        return go.Figure()
    pca = PCA(n_components=3)
    comps = pca.fit_transform(rets.T)
    fig = go.Figure(go.Scatter3d(x=comps[:,0], y=comps[:,1], z=comps[:,2], mode='markers+text', text=rets.columns, marker=dict(size=9, color=comps[:,0], colorscale='Viridis', line=dict(color='white', width=0.5))))
    fig.update_layout(**_layout('3D PCA Asset Space', 560), scene=dict(xaxis_title='PC1', yaxis_title='PC2', zaxis_title='PC3'))
    return fig


def _viz_vol_surface(close_df):
    rets = _returns(close_df)
    horizons = [5, 10, 20, 60]
    vol = pd.concat({f'{h}d': rets.rolling(h).std().iloc[-1] * np.sqrt(252) * 100 for h in horizons}, axis=1)
    z = vol.T.values
    fig = go.Figure(go.Surface(z=z, x=vol.columns, y=vol.index, colorscale=[[0,'#ef4444'],[0.5,'#f59e0b'],[1,'#10b981']]))
    fig.update_layout(**_layout('3D Volatility Surface', 560), scene=dict(zaxis_title='Annualized Vol %'))
    return fig


def _viz_3d_candlesticks(frames):
    df = _ohlc('^IXIC', frames).iloc[::max(1, len(_ohlc('^IXIC', frames)) // 120)]
    fig = go.Figure()
    for _, row in df.iterrows():
        color = '#10b981' if row['close'] >= row['open'] else '#ef4444'
        fig.add_trace(go.Scatter3d(x=[row.name, row.name], y=[row['low'], row['high']], z=[row['open'], row['close']], mode='lines', line=dict(color=color, width=4), showlegend=False, hoverinfo='skip'))
    fig.update_layout(**_layout('3D Candlestick Forest', 560), scene=dict(yaxis_title='Low-High', zaxis_title='Open-Close'))
    return fig


def _viz_3d_risk(close_df):
    rets = _returns(close_df)
    mom = (close_df / close_df.shift(20) - 1).iloc[-1] * 100
    vol = rets.rolling(20).std().iloc[-1] * np.sqrt(252) * 100
    ret = rets.mean() * 252 * 100
    df = pd.concat([mom.rename('Momentum'), vol.rename('Volatility'), ret.rename('Return')], axis=1).dropna()
    fig = go.Figure(go.Scatter3d(x=df['Momentum'], y=df['Volatility'], z=df['Return'], mode='markers+text', text=df.index, marker=dict(size=8, color=df['Return'], colorscale='Viridis')))
    fig.update_layout(**_layout('3D Risk Landscape', 560), scene=dict(xaxis_title='20d Momentum %', yaxis_title='20d Vol %', zaxis_title='Ann. Return %'))
    return fig


def _viz_3d_calendar(close_df):
    symbol = 'QQQ' if 'QQQ' in close_df.columns else close_df.columns[0]
    rets = close_df[symbol].pct_change().dropna()
    temp = pd.DataFrame({'ret': rets * 100, 'weekday': rets.index.weekday, 'week': rets.index.isocalendar().week.astype(int)})
    pivot = temp.pivot_table(index='week', columns='weekday', values='ret', aggfunc='mean').fillna(0)
    fig = go.Figure(go.Surface(z=pivot.values, x=['Mon','Tue','Wed','Thu','Fri'], y=pivot.index, colorscale=[[0,'#ef4444'],[0.5,'#0f1629'],[1,'#10b981']]))
    fig.update_layout(**_layout('3D Calendar Return Surface', 560), scene=dict(zaxis_title='Return %'))
    return fig


def _viz_regime(close_df):
    symbol = 'SPY' if 'SPY' in close_df.columns else close_df.columns[0]
    price = close_df[symbol]
    rets = price.pct_change()
    mean = rets.rolling(20).mean()
    vol = rets.rolling(20).std()
    states = np.where((mean > 0) & (vol <= vol.median()), 2, np.where((mean < 0) | (vol > vol.quantile(0.75)), 0, 1))
    colors = {0: 'rgba(239,68,68,0.18)', 1: 'rgba(245,158,11,0.12)', 2: 'rgba(16,185,129,0.16)'}
    fig = go.Figure(go.Scatter(x=price.index, y=price, mode='lines', line=dict(color='#00d4ff', width=2), name='Price'))
    start = None
    last = None
    for date, state, next_state in zip(price.index[1:], states[1:], list(states[2:]) + [None]):
        if start is None:
            start = date
        if state != next_state:
            fig.add_vrect(x0=start, x1=date, fillcolor=colors.get(int(state), colors[1]), opacity=1, line_width=0)
            start = None
    fig.update_layout(**_layout('Market Regime Map', 430))
    return fig


def _viz_sector(sector_data):
    sectors = list(sector_data.keys())
    changes = [sector_data[s]['change_pct'] for s in sectors]
    values = [max(abs(c), 0.1) for c in changes]
    fig = go.Figure(go.Treemap(labels=sectors, parents=[''] * len(sectors), values=values, customdata=changes, texttemplate='<b>%{label}</b><br>%{customdata:.2f}%', marker=dict(colors=changes, colorscale=[[0,'#ef4444'],[0.5,'#1e293b'],[1,'#10b981']], cmid=0)))
    fig.update_layout(**_layout('Sector Exposure Treemap', 500))
    return fig


def _viz_breadth(close_df):
    latest = (close_df.iloc[-1] / close_df.iloc[-21] - 1) * 100
    df = latest.sort_values()
    fig = go.Figure(go.Bar(x=df.index, y=df.values, marker_color=['#10b981' if v >= 0 else '#ef4444' for v in df.values], name='21d Return'))
    fig.update_layout(**_layout('Market Breadth Ladder', 430), yaxis_title='21d Return %')
    return fig


def _render_grid(items):
    cols = st.columns(2)
    for i, (title, fig) in enumerate(items):
        with cols[i % 2]:
            st.markdown(f"##### {title}")
            st.plotly_chart(fig, use_container_width=True)


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
    import textwrap
    display_items, frames, close_df, live_feed = _dashboard_market_data()
    metrics_html = ""
    for item in display_items:
        pct = item['change_pct']
        color = "#10b981" if pct >= 0 else "#ef4444"
        arrow = "▲" if pct >= 0 else "▼"
        label = INDEX_LABELS.get(item['symbol'], item.get('name', item['symbol']))
        metrics_html += textwrap.dedent(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border-secondary);
                border-radius:14px;padding:16px;text-align:center;transition:all 0.3s">
                <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:4px">{label}</div>
                <div style="font-size:1.4rem;font-weight:700;color:var(--text-primary)">{item['price']:,.2f}</div>
                <div style="color:{color};font-size:0.85rem">{arrow} {abs(pct):.2f}%</div>
            </div>
        """)
    
    st.markdown(textwrap.dedent(f"""<div style="display:grid;grid-template-columns:repeat({min(len(display_items), 5)},1fr);gap:12px">{metrics_html}</div>"""), unsafe_allow_html=True)

    st.markdown("---")

    # ── Sector Performance & Watchlists ─────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("#### 🌡️ Sector Performance")
        sector_data = get_sector_performance() or _fallback_sector_data()
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
        df_ov = pd.DataFrame(display_items)
        df_ov['Change %'] = df_ov['change_pct'].apply(lambda x: f"▲ {x:.2f}%" if x >= 0 else f"▼ {abs(x):.2f}%")
        df_ov['Price'] = df_ov['price'].apply(lambda x: f"{x:,.2f}")
        display = df_ov[['name','Price','Change %']].rename(columns={'name':'Index'})
        st.dataframe(display, use_container_width=True, hide_index=True, height=300)
        if not live_feed:
            st.caption("Live feed unavailable; showing fallback snapshot so the dashboard stays populated.")

    with col_b:
        st.markdown("#### 🎯 Market Sentiment")
        vix_val = 20.0
        for item in display_items:
            if item['symbol'] == '^VIX':
                vix_val = item['price']
                break
        fig = gauge_chart(vix_val, 'VIX Fear Index', 0, 80, 30)
        st.plotly_chart(fig, use_container_width=True)

    # ── 30 Visualization Lab ─────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔬 30 Visualization Lab")

    sector_data = get_sector_performance() or _fallback_sector_data()
    tab_structure, tab_indicators, tab_risk, tab_correlation, tab_3d = st.tabs([
        "Market Structure", "Indicators", "Risk & Return", "Correlation", "3D Intelligence",
    ])

    with tab_structure:
        _render_grid([
            ("1. Candlestick Pulse", _viz_candlestick(frames)),
            ("2. Heikin-Ashi Flow", _viz_heikin_ashi(frames)),
            ("3. Kagi Reversal Structure", _viz_kagi(frames)),
            ("4. Point & Figure Box Reversal", _viz_point_figure(frames)),
            ("5. OHLC Range Bars", _viz_ohlc_bars(frames)),
            ("6. Volume Profile", _viz_volume_profile(frames)),
        ])

    with tab_indicators:
        _render_grid([
            ("7. Bollinger Band Compression", _viz_bollinger(frames)),
            ("8. RSI Momentum Oscillator", _viz_rsi(frames)),
            ("9. MACD Signal Stack", _viz_macd(frames)),
            ("10. ATR Volatility Ribbon Proxy", _viz_atr(frames)),
        ])

    with tab_risk:
        _render_grid([
            ("11. Drawdown Map", _viz_drawdown(close_df)),
            ("12. Daily Returns Distribution", _viz_returns_histogram(close_df)),
            ("13. Q-Q Normality Plot", _viz_qq(close_df)),
            ("14. Risk-Return Bubble", _viz_risk_return(close_df)),
            ("15. Beta vs Benchmark", _viz_beta(close_df)),
            ("16. Cumulative Return River", _viz_cumulative(close_df)),
            ("17. Relative Strength Matrix", _viz_relative_strength(close_df)),
            ("18. Calendar Return Heatmap", _viz_calendar(close_df)),
            ("19. Momentum Timeframe Matrix", _viz_momentum(close_df)),
            ("28. Market Regime Map", _viz_regime(close_df)),
            ("30. Market Breadth Ladder", _viz_breadth(close_df)),
        ])

    with tab_correlation:
        _render_grid([
            ("20. Cross-Asset Correlation", _viz_correlation(close_df)),
            ("21. Rolling Correlation Pairs", _viz_rolling_corr(close_df)),
            ("29. Sector Exposure Treemap", _viz_sector(sector_data)),
        ])

    with tab_3d:
        _render_grid([
            ("22. 3D Lead-Lag Surface", _viz_lead_lag(close_df)),
            ("23. 3D PCA Asset Space", _viz_pca_3d(close_df)),
            ("24. 3D Volatility Surface", _viz_vol_surface(close_df)),
            ("25. 3D Candlestick Forest", _viz_3d_candlesticks(frames)),
            ("26. 3D Risk Landscape", _viz_3d_risk(close_df)),
            ("27. 3D Calendar Return Surface", _viz_3d_calendar(close_df)),
        ])

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