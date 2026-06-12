import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

DARK = dict(paper_bgcolor='#0a0e1a', plot_bgcolor='#0f1629',
            font=dict(color='#e2e8f0', family='Inter'),
            xaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b'),
            yaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b'),
            margin=dict(l=40, r=20, t=40, b=40))

COLORS = ['#00d4ff','#7c3aed','#f59e0b','#10b981','#ef4444',
          '#8b5cf6','#ec4899','#14b8a6','#f97316','#06b6d4',
          '#a78bfa','#34d399','#fbbf24','#f87171','#60a5fa']

def _base():
    fig = go.Figure()
    fig.update_layout(**DARK)
    return fig

# ── Financial Charts ──────────────────────────────────────────────
def candlestick(df, symbol=''):
    fig = go.Figure(go.Candlestick(
        x=df.index,
        open=df.get('open', df.iloc[:,0]),
        high=df.get('high', df.iloc[:,0]),
        low=df.get('low', df.iloc[:,0]),
        close=df.get('close', df.iloc[:,0]),
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444',
        name=symbol,
    ))
    fig.update_layout(**DARK, title=f'{symbol} Candlestick', height=400,
                      xaxis_rangeslider_visible=False)
    return fig

def ohlc_chart(df, symbol=''):
    fig = go.Figure(go.Ohlc(
        x=df.index,
        open=df.get('open', df.iloc[:,0]),
        high=df.get('high', df.iloc[:,0]),
        low=df.get('low', df.iloc[:,0]),
        close=df.get('close', df.iloc[:,0]),
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444',
    ))
    fig.update_layout(**DARK, title=f'{symbol} OHLC', height=400)
    return fig

def volume_chart(df, symbol=''):
    colors = ['#10b981' if c >= o else '#ef4444'
              for c, o in zip(df.get('close', df.iloc[:,0]), df.get('open', df.iloc[:,0]))]
    fig = go.Figure(go.Bar(x=df.index, y=df.get('volume', pd.Series()), marker_color=colors, name='Volume'))
    fig.update_layout(**DARK, title='Volume', height=200)
    return fig

def candlestick_volume(df, symbol=''):
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.02)
    fig.add_trace(go.Candlestick(
        x=df.index, open=df.get('open', df.iloc[:,0]),
        high=df.get('high', df.iloc[:,0]), low=df.get('low', df.iloc[:,0]),
        close=df.get('close', df.iloc[:,0]),
        increasing_line_color='#10b981', decreasing_line_color='#ef4444', name=symbol,
    ), row=1, col=1)
    vol = df.get('volume', None)
    if vol is not None:
        colors = ['#10b981' if c >= o else '#ef4444'
                  for c, o in zip(df.get('close', df.iloc[:,0]), df.get('open', df.iloc[:,0]))]
        fig.add_trace(go.Bar(x=df.index, y=vol, marker_color=colors, name='Vol', showlegend=False), row=2, col=1)
    fig.update_layout(**DARK, title=f'{symbol}', height=500, xaxis_rangeslider_visible=False)
    return fig

# ── Line / Area Charts ───────────────────────────────────────────
def line_chart(df, title='', height=400):
    fig = _base()
    if isinstance(df, pd.Series):
        fig.add_trace(go.Scatter(x=df.index, y=df.values, mode='lines',
                                 line=dict(color=COLORS[0], width=2), name=df.name or ''))
    else:
        for i, col in enumerate(df.columns):
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines',
                                     line=dict(color=COLORS[i % len(COLORS)], width=2), name=col))
    fig.update_layout(title=title, height=height)
    return fig

def area_chart(df, title='', height=400):
    fig = _base()
    if isinstance(df, pd.Series):
        fig.add_trace(go.Scatter(x=df.index, y=df.values, mode='lines',
                                 fill='tozeroy', line=dict(color=COLORS[0], width=2),
                                 fillcolor='rgba(0,212,255,0.1)', name=df.name or ''))
    else:
        for i, col in enumerate(df.columns):
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines',
                                     fill='tonexty' if i > 0 else 'tozeroy',
                                     line=dict(color=COLORS[i % len(COLORS)], width=2),
                                     fillcolor=f'rgba({_hex_to_rgb(COLORS[i % len(COLORS)])},0.1)',
                                     name=col))
    fig.update_layout(title=title, height=height)
    return fig

def stacked_area_chart(df, title='', height=400):
    fig = _base()
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines',
                                 stackgroup='one', line=dict(color=COLORS[i % len(COLORS)], width=1),
                                 fillcolor=f'rgba({_hex_to_rgb(COLORS[i % len(COLORS)])},0.3)', name=col))
    fig.update_layout(title=title, height=height)
    return fig

# ── Statistical Charts ───────────────────────────────────────────
def histogram(series, title='', bins=50):
    fig = _base()
    fig.add_trace(go.Histogram(x=series, nbinsx=bins, marker_color=COLORS[0],
                               marker_line_color='rgba(255,255,255,0.1)', marker_line_width=0.5))
    fig.update_layout(title=title, height=350, bargap=0.05)
    return fig

def density_plot(series, title=''):
    from scipy.stats import gaussian_kde
    x = series.dropna().values
    kde = gaussian_kde(x)
    x_range = np.linspace(x.min(), x.max(), 200)
    fig = _base()
    fig.add_trace(go.Scatter(x=x_range, y=kde(x_range), mode='lines',
                             fill='tozeroy', line=dict(color=COLORS[0], width=2),
                             fillcolor='rgba(0,212,255,0.1)'))
    fig.update_layout(title=title, height=350)
    return fig

def box_plot(df, title=''):
    fig = _base()
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Box(y=df[col], name=col, marker_color=COLORS[i % len(COLORS)],
                             boxmean=True))
    fig.update_layout(title=title, height=400)
    return fig

def violin_plot(df, title=''):
    fig = _base()
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Violin(y=df[col], name=col, box_visible=True,
                                meanline_visible=True, line_color=COLORS[i % len(COLORS)],
                                fillcolor=f'rgba({_hex_to_rgb(COLORS[i % len(COLORS)])},0.3)'))
    fig.update_layout(title=title, height=400)
    return fig

def scatter_plot(x, y, title='', xlabel='', ylabel='', color=None):
    fig = _base()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers',
                             marker=dict(color=color or COLORS[0], size=6, opacity=0.7),
                             text=[f'({xi:.3f}, {yi:.3f})' for xi, yi in zip(x, y)],
                             hoverinfo='text'))
    # Trendline
    try:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        fig.add_trace(go.Scatter(x=x_line, y=p(x_line), mode='lines',
                                 line=dict(color='#f59e0b', width=2, dash='dash'), name='Trend'))
    except Exception:
        pass
    fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel, height=400)
    return fig

def bubble_chart(df, x_col, y_col, size_col, color_col=None, title=''):
    fig = _base()
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col],
        mode='markers',
        marker=dict(size=df[size_col], sizemode='area', sizeref=2*max(df[size_col])/(40**2),
                    color=df[color_col] if color_col else COLORS[0],
                    colorscale='Viridis', showscale=bool(color_col), opacity=0.7,
                    line=dict(color='white', width=0.5)),
        text=df.index, hoverinfo='text+x+y',
    ))
    fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col, height=450)
    return fig

# ── Matrix / Heatmaps ────────────────────────────────────────────
def correlation_heatmap(df, title='Correlation Matrix'):
    corr = df.corr()
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale=[[0,'#ef4444'],[0.5,'#0f1629'],[1,'#00d4ff']],
        zmid=0, text=np.round(corr.values, 2),
        texttemplate='%{text}', textfont_size=9,
        hoverongaps=False, colorbar=dict(thickness=12),
    ))
    fig.update_layout(**DARK, title=title, height=500)
    return fig

def lag_heatmap(lag_matrix, title='Lag Heatmap'):
    fig = go.Figure(go.Heatmap(
        z=lag_matrix.values, x=lag_matrix.columns, y=lag_matrix.index,
        colorscale='RdBu', zmid=0,
        text=np.round(lag_matrix.values, 2), texttemplate='%{text}',
        textfont_size=8, colorbar=dict(thickness=12),
    ))
    fig.update_layout(**DARK, title=title, height=500)
    return fig

def rolling_corr_heatmap(df, pairs, windows=[10, 20, 30, 60], title='Rolling Correlation'):
    rows = []
    for w in windows:
        for s1, s2 in pairs:
            if s1 in df.columns and s2 in df.columns:
                rc = df[s1].rolling(w).corr(df[s2]).iloc[-1]
                rows.append({'window': f'{w}d', 'pair': f'{s1}/{s2}', 'correlation': rc})
    if not rows:
        return _base()
    rdf = pd.DataFrame(rows).pivot(index='window', columns='pair', values='correlation')
    return correlation_heatmap(rdf, title)

# ── Bar Charts ───────────────────────────────────────────────────
def bar_chart(x, y, title='', color=None, horizontal=False):
    fig = _base()
    colors = [COLORS[i % len(COLORS)] for i in range(len(x))]
    if color:
        colors = ['#10b981' if v >= 0 else '#ef4444' for v in y]
    if horizontal:
        fig.add_trace(go.Bar(y=x, x=y, orientation='h', marker_color=colors))
    else:
        fig.add_trace(go.Bar(x=x, y=y, marker_color=colors))
    fig.update_layout(title=title, height=400)
    return fig

def grouped_bar(df, title=''):
    fig = _base()
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Bar(x=df.index, y=df[col], name=col,
                             marker_color=COLORS[i % len(COLORS)]))
    fig.update_layout(title=title, barmode='group', height=400)
    return fig

def stacked_bar(df, title=''):
    fig = _base()
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Bar(x=df.index, y=df[col], name=col,
                             marker_color=COLORS[i % len(COLORS)]))
    fig.update_layout(title=title, barmode='stack', height=400)
    return fig

def waterfall_chart(categories, values, title='Waterfall'):
    fig = go.Figure(go.Waterfall(
        x=categories, y=values,
        connector=dict(line=dict(color='#64748b')),
        increasing=dict(marker_color='#10b981'),
        decreasing=dict(marker_color='#ef4444'),
        totals=dict(marker_color='#00d4ff'),
    ))
    fig.update_layout(**DARK, title=title, height=400)
    return fig

# ── Advanced Charts ──────────────────────────────────────────────
def treemap(labels, parents, values, title='Treemap'):
    fig = go.Figure(go.Treemap(
        labels=labels, parents=parents, values=values,
        textinfo='label+value+percent root',
        marker=dict(colorscale='Viridis'),
    ))
    fig.update_layout(**DARK, title=title, height=500)
    return fig

def sunburst(labels, parents, values, title='Sunburst'):
    fig = go.Figure(go.Sunburst(
        labels=labels, parents=parents, values=values,
        branchvalues='total',
    ))
    fig.update_layout(**DARK, title=title, height=500)
    return fig

def radar_chart(categories, values_dict, title='Radar'):
    fig = _base()
    cats = categories + [categories[0]]
    for name, vals in values_dict.items():
        v = list(vals) + [vals[0]]
        fig.add_trace(go.Scatterpolar(r=v, theta=cats, fill='toself', name=name))
    fig.update_layout(title=title, polar=dict(
        bgcolor='#0f1629',
        radialaxis=dict(gridcolor='#1e293b', color='#64748b'),
        angularaxis=dict(gridcolor='#1e293b', color='#64748b'),
    ), height=450)
    return fig

def gauge_chart(value, title='', min_val=0, max_val=100, threshold=None):
    steps = [
        dict(range=[min_val, max_val*0.33], color='#ef4444'),
        dict(range=[max_val*0.33, max_val*0.66], color='#f59e0b'),
        dict(range=[max_val*0.66, max_val], color='#10b981'),
    ]
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=value,
        title=dict(text=title, font=dict(color='#e2e8f0', size=14)),
        gauge=dict(axis=dict(range=[min_val, max_val], tickcolor='#64748b'),
                   bar=dict(color='#00d4ff'), steps=steps,
                   threshold=dict(line=dict(color='white', width=2),
                                  thickness=0.75, value=threshold or max_val*0.75),
                   bgcolor='#0f1629', bordercolor='#1e293b'),
        number=dict(font=dict(color='#e2e8f0')),
    ))
    fig.update_layout(**DARK, height=280)
    return fig

def sankey_chart(source, target, value, labels, title='Sankey'):
    fig = go.Figure(go.Sankey(
        node=dict(label=labels, color=COLORS[:len(labels)],
                  pad=15, thickness=20,
                  line=dict(color='#1e293b', width=0.5)),
        link=dict(source=source, target=target, value=value,
                  color='rgba(0,212,255,0.2)'),
    ))
    fig.update_layout(**DARK, title=title, height=500)
    return fig

# ── ML / Forecast Charts ─────────────────────────────────────────
def feature_importance_chart(fi_series, title='Feature Importance', top_n=20):
    fi = fi_series.head(top_n).sort_values()
    return bar_chart(fi.index.tolist(), fi.values.tolist(), title=title, horizontal=True)

def shap_chart(shap_series, title='SHAP Values', top_n=15):
    shap = shap_series.head(top_n).sort_values()
    colors = ['#10b981' if v >= 0 else '#ef4444' for v in shap.values]
    fig = _base()
    fig.add_trace(go.Bar(y=shap.index, x=shap.values, orientation='h', marker_color=colors))
    fig.update_layout(title=title, height=400)
    return fig

def backtest_chart(actual, predicted, title='Backtest: Actual vs Predicted'):
    fig = _base()
    fig.add_trace(go.Scatter(x=actual.index, y=actual.values, mode='lines',
                             line=dict(color='#e2e8f0', width=1.5), name='Actual'))
    fig.add_trace(go.Scatter(x=predicted.index, y=predicted.values, mode='lines',
                             line=dict(color='#00d4ff', width=1.5, dash='dot'), name='Predicted'))
    fig.update_layout(title=title, height=400)
    return fig

def monte_carlo_chart(mc_result, dates=None, title='Monte Carlo Forecast'):
    n = len(mc_result['mean'])
    x = list(range(n)) if dates is None else dates
    fig = _base()
    # Fan chart
    fig.add_trace(go.Scatter(x=list(x)+list(x)[::-1],
        y=list(mc_result['p95'])+list(mc_result['p5'])[::-1],
        fill='toself', fillcolor='rgba(124,58,237,0.1)',
        line=dict(color='transparent'), name='90% CI'))
    fig.add_trace(go.Scatter(x=list(x)+list(x)[::-1],
        y=list(mc_result['p75'])+list(mc_result['p25'])[::-1],
        fill='toself', fillcolor='rgba(124,58,237,0.2)',
        line=dict(color='transparent'), name='50% CI'))
    fig.add_trace(go.Scatter(x=x, y=mc_result['mean'], mode='lines',
                             line=dict(color='#00d4ff', width=2), name='Mean'))
    # Sample paths
    for i in range(min(50, len(mc_result['simulations']))):
        fig.add_trace(go.Scatter(x=x, y=mc_result['simulations'][i], mode='lines',
                                 line=dict(color='rgba(0,212,255,0.05)', width=0.5),
                                 showlegend=False))
    fig.update_layout(title=title, height=450)
    return fig

def volatility_cone_chart(vol_result, title='Volatility Cone'):
    fig = _base()
    fig.add_trace(go.Scatter(x=vol_result['historical_vol'].index,
                             y=vol_result['historical_vol'].values * 100,
                             mode='lines', line=dict(color='#e2e8f0', width=1.5), name='Historical Vol'))
    fig.add_trace(go.Scatter(x=vol_result['ewm_vol'].index,
                             y=vol_result['ewm_vol'].values * 100,
                             mode='lines', line=dict(color='#00d4ff', width=2, dash='dot'), name='EWM Vol'))
    fig.update_layout(title=title, yaxis_title='Annualized Volatility (%)', height=400)
    return fig

# ── Cross-Correlation Chart ──────────────────────────────────────
def cross_correlation_chart(xcorr_dict, title='Cross-Correlation'):
    lags = sorted(xcorr_dict.keys())
    corrs = [xcorr_dict[l] for l in lags]
    colors = ['#10b981' if c >= 0 else '#ef4444' for c in corrs]
    fig = _base()
    fig.add_trace(go.Bar(x=lags, y=corrs, marker_color=colors, name='Correlation'))
    fig.add_hline(y=0, line_color='#64748b')
    opt_lag = max(xcorr_dict, key=lambda k: abs(xcorr_dict[k]))
    fig.add_vline(x=opt_lag, line_color='#f59e0b', line_dash='dash',
                  annotation_text=f'Optimal: {opt_lag}d', annotation_font_color='#f59e0b')
    fig.update_layout(title=title, xaxis_title='Lag (days)', yaxis_title='Correlation', height=380)
    return fig

# ── 3D Charts ────────────────────────────────────────────────────
def surface_3d(z_matrix, x_labels=None, y_labels=None, title='3D Surface'):
    fig = go.Figure(go.Surface(
        z=z_matrix,
        x=x_labels or list(range(z_matrix.shape[1])),
        y=y_labels or list(range(z_matrix.shape[0])),
        colorscale='Viridis', opacity=0.9,
    ))
    fig.update_layout(
        title=title, paper_bgcolor='#0a0e1a',
        scene=dict(bgcolor='#0a0e1a',
                   xaxis=dict(backgroundcolor='#0a0e1a', gridcolor='#1e293b', color='#e2e8f0'),
                   yaxis=dict(backgroundcolor='#0a0e1a', gridcolor='#1e293b', color='#e2e8f0'),
                   zaxis=dict(backgroundcolor='#0a0e1a', gridcolor='#1e293b', color='#e2e8f0')),
        font=dict(color='#e2e8f0'), height=550,
    )
    return fig

def lead_lag_surface_3d(returns_df, max_lag=20):
    """3D Lead-Lag correlation surface."""
    symbols = list(returns_df.columns)[:8]
    lags = list(range(-max_lag, max_lag + 1))
    z = np.zeros((len(symbols), len(lags)))
    for i, s1 in enumerate(symbols):
        for j, lag in enumerate(lags):
            try:
                a = returns_df[s1].values
                ref = returns_df[symbols[0]].values
                if lag < 0:
                    c = np.corrcoef(a[:lag], ref[-lag:])[0,1]
                elif lag == 0:
                    c = np.corrcoef(a, ref)[0,1]
                else:
                    c = np.corrcoef(a[lag:], ref[:-lag])[0,1]
                z[i, j] = c if not np.isnan(c) else 0
            except Exception:
                z[i, j] = 0
    return surface_3d(z, lags, symbols, '3D Lead-Lag Surface')

def pca_3d(returns_df, n_components=3):
    """3D PCA scatter."""
    from sklearn.decomposition import PCA
    clean = returns_df.dropna()
    if clean.empty or clean.shape[1] < 3:
        return _base()
    pca = PCA(n_components=n_components)
    comps = pca.fit_transform(clean.T)
    fig = go.Figure(go.Scatter3d(
        x=comps[:,0], y=comps[:,1], z=comps[:,2],
        mode='markers+text', text=returns_df.columns,
        marker=dict(size=8, color=comps[:,0], colorscale='Viridis', opacity=0.8,
                    line=dict(color='white', width=0.5)),
    ))
    fig.update_layout(
        title='3D PCA Asset Space', paper_bgcolor='#0a0e1a', font=dict(color='#e2e8f0'),
        scene=dict(bgcolor='#0a0e1a',
                   xaxis=dict(title=f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', backgroundcolor='#0a0e1a'),
                   yaxis=dict(title=f'PC2 ({pca.explained_variance_ratio_[1]:.1%})', backgroundcolor='#0a0e1a'),
                   zaxis=dict(title=f'PC3 ({pca.explained_variance_ratio_[2]:.1%})', backgroundcolor='#0a0e1a')),
        height=550,
    )
    return fig

def regime_chart(prices, states, title='Market Regimes'):
    fig = _base()
    colors_r = {0:'rgba(239,68,68,0.3)', 1:'rgba(245,158,11,0.3)', 2:'rgba(16,185,129,0.3)'}
    labels_r = {0:'Bear', 1:'Neutral', 2:'Bull'}
    if states is not None and len(states) == len(prices) - 1:
        idx = prices.index[1:]
        for state in np.unique(states):
            mask = states == state
            state_idx = idx[mask]
            if len(state_idx) > 0:
                for i in range(len(state_idx)):
                    fig.add_vrect(x0=state_idx[i], x1=state_idx[i],
                                  fillcolor=colors_r.get(state,'rgba(100,116,139,0.2)'), opacity=0.3,
                                  layer='below', line_width=0)
    fig.add_trace(go.Scatter(x=prices.index, y=prices.values, mode='lines',
                             line=dict(color='#00d4ff', width=2), name='Price'))
    fig.update_layout(title=title, height=400)
    return fig

# ── Sector Charts ─────────────────────────────────────────────────
def sector_heatmap(sector_data):
    sectors = list(sector_data.keys())
    changes = [sector_data[s]['change_pct'] for s in sectors]
    abs_changes = [abs(c) for c in changes]
    fig = go.Figure(go.Treemap(
        labels=sectors,
        parents=['']*len(sectors),
        values=[max(v, 0.1) for v in abs_changes],
        customdata=changes,
        texttemplate='<b>%{label}</b><br>%{customdata:.2f}%',
        marker=dict(
            colors=changes,
            colorscale=[[0,'#ef4444'],[0.5,'#1e293b'],[1,'#10b981']],
            cmid=0,
        ),
    ))
    fig.update_layout(**DARK, title='Sector Heatmap', height=400)
    return fig

# ── Utilities ────────────────────────────────────────────────────
def _hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return ','.join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))

def returns_distribution(returns_series, title='Returns Distribution'):
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Histogram', 'Q-Q Plot'])
    vals = returns_series.dropna().values
    fig.add_trace(go.Histogram(x=vals, nbinsx=60, marker_color='#00d4ff',
                               marker_line_width=0.3, name='Returns'), row=1, col=1)
    # Q-Q
    from scipy import stats
    (osm, osr), (slope, intercept, r) = stats.probplot(vals, dist='norm')
    fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers',
                             marker=dict(color='#7c3aed', size=4), name='Data'), row=1, col=2)
    fig.add_trace(go.Scatter(x=osm, y=slope*np.array(osm)+intercept, mode='lines',
                             line=dict(color='#f59e0b', dash='dash'), name='Normal'), row=1, col=2)
    fig.update_layout(**DARK, title=title, height=400)
    return fig

def pair_plot(returns_df, title='Pair Plot'):
    cols = list(returns_df.columns)[:6]
    n = len(cols)
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=n, cols=n, shared_xaxes=False, shared_yaxes=False,
                        horizontal_spacing=0.03, vertical_spacing=0.03)
    for i, c1 in enumerate(cols):
        for j, c2 in enumerate(cols):
            if i == j:
                fig.add_trace(go.Histogram(x=returns_df[c1], marker_color=COLORS[i],
                                           showlegend=False, nbinsx=30), row=i+1, col=j+1)
            else:
                fig.add_trace(go.Scatter(x=returns_df[c2], y=returns_df[c1], mode='markers',
                                         marker=dict(size=3, color=COLORS[i], opacity=0.5),
                                         showlegend=False), row=i+1, col=j+1)
    fig.update_layout(**DARK, title=title, height=700, showlegend=False)
    return fig
