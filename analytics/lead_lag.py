import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import correlate
import warnings
warnings.filterwarnings('ignore')

def cross_correlation(s1, s2, max_lag=30):
    """Returns dict of lag -> correlation."""
    s1, s2 = s1.dropna(), s2.dropna()
    df = pd.concat([s1, s2], axis=1).dropna()
    if len(df) < 30:
        return {}
    a, b = df.iloc[:,0].values, df.iloc[:,1].values
    a = (a - a.mean()) / (a.std() + 1e-9)
    b = (b - b.mean()) / (b.std() + 1e-9)
    result = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            corr = np.corrcoef(a[:lag], b[-lag:])[0,1]
        elif lag == 0:
            corr = np.corrcoef(a, b)[0,1]
        else:
            corr = np.corrcoef(a[lag:], b[:-lag])[0,1]
        result[lag] = corr if not np.isnan(corr) else 0.0
    return result

def find_optimal_lag(s1, s2, max_lag=30):
    """Find the lag where s1 best predicts s2."""
    xcorr = cross_correlation(s1, s2, max_lag)
    if not xcorr:
        return None
    # Positive lag means s1 leads s2
    best_lag = max(xcorr, key=lambda k: abs(xcorr[k]))
    best_corr = xcorr[best_lag]
    return {
        'optimal_lag': best_lag,
        'correlation': best_corr,
        'all_lags': xcorr
    }

def granger_causality(s1, s2, max_lag=10):
    """Test if s1 Granger-causes s2. Returns best lag and p-value."""
    from statsmodels.tsa.stattools import grangercausalitytests
    df = pd.concat([s2, s1], axis=1).dropna()
    if len(df) < max_lag * 3 + 10:
        return None
    try:
        results = grangercausalitytests(df, maxlag=max_lag, verbose=False)
        best_lag, best_p = 1, 1.0
        for lag, res in results.items():
            p = res[0]['ssr_ftest'][1]
            if p < best_p:
                best_p, best_lag = p, lag
        return {
            'lag': best_lag,
            'p_value': best_p,
            'significant': best_p < 0.05,
            'all_results': {lag: res[0]['ssr_ftest'][1] for lag, res in results.items()}
        }
    except Exception:
        return None

def transfer_entropy(s1, s2, lag=1, bins=10):
    """Estimate transfer entropy from s1 to s2."""
    try:
        import pyinform
        x = pd.Series(s1).dropna()
        y = pd.Series(s2).dropna()
        df = pd.concat([x, y], axis=1).dropna()
        if len(df) < 50:
            return None
        # Discretize
        x_d = pd.cut(df.iloc[:,0], bins=bins, labels=False).fillna(0).astype(int).values
        y_d = pd.cut(df.iloc[:,1], bins=bins, labels=False).fillna(0).astype(int).values
        te = pyinform.transfer_entropy(x_d, y_d, k=lag)
        return float(te)
    except Exception:
        try:
            # Fallback: manual TE estimate
            return _manual_transfer_entropy(s1, s2, lag, bins)
        except Exception:
            return None

def _manual_transfer_entropy(s1, s2, lag=1, bins=8):
    """Manual transfer entropy using joint histograms."""
    df = pd.concat([pd.Series(s1), pd.Series(s2)], axis=1).dropna()
    if len(df) < 40:
        return None
    x = pd.cut(df.iloc[:,0], bins=bins, labels=False).fillna(0).astype(int).values
    y = pd.cut(df.iloc[:,1], bins=bins, labels=False).fillna(0).astype(int).values
    n = len(x)
    k = lag

    def p(*args):
        counts = {}
        for vals in zip(*[a[i:n-k+i] if i > 0 else a[:n-k] for i, a in zip(range(len(args)), args)]):
            counts[vals] = counts.get(vals, 0) + 1
        total = sum(counts.values())
        return {k: v/total for k, v in counts.items()}

    te = 0.0
    p_joint = p(y[k:], y[:n-k], x[:n-k])
    p_y_yk = p(y[k:], y[:n-k])
    p_yk = {}
    for (yk_next, yk, xk), prob in p_joint.items():
        p_yk[yk] = p_yk.get(yk, 0) + prob

    for (yk_next, yk, xk), pjoint in p_joint.items():
        p_cond_x = pjoint / (p_y_yk.get((yk_next, yk), 1e-9))
        p_cond_nox = p_y_yk.get((yk_next, yk), 1e-9) / (p_yk.get(yk, 1e-9))
        if p_cond_x > 0 and p_cond_nox > 0:
            te += pjoint * np.log2(p_cond_x / p_cond_nox)
    return max(0.0, te)

def mutual_information(s1, s2, bins=10):
    """Estimate mutual information between two series."""
    df = pd.concat([pd.Series(s1), pd.Series(s2)], axis=1).dropna()
    if len(df) < 30:
        return 0.0
    x = pd.cut(df.iloc[:,0], bins=bins, labels=False).fillna(0).astype(int)
    y = pd.cut(df.iloc[:,1], bins=bins, labels=False).fillna(0).astype(int)
    from sklearn.metrics import mutual_info_score
    return mutual_info_score(x, y)

def cointegration_test(s1, s2):
    """Engle-Granger cointegration test."""
    from statsmodels.tsa.stattools import coint
    df = pd.concat([s1, s2], axis=1).dropna()
    if len(df) < 30:
        return None
    try:
        score, p_value, _ = coint(df.iloc[:,0], df.iloc[:,1])
        return {'score': score, 'p_value': p_value, 'cointegrated': p_value < 0.05}
    except Exception:
        return None

def rolling_correlation(s1, s2, window=30):
    """Rolling Pearson correlation."""
    df = pd.concat([s1, s2], axis=1).dropna()
    if df.empty:
        return pd.Series()
    return df.iloc[:,0].rolling(window).corr(df.iloc[:,1]).dropna()

def var_model(df, max_lag=5):
    """VAR model for multiple time series."""
    from statsmodels.tsa.vector_ar.var_model import VAR
    clean = df.dropna()
    if len(clean) < max_lag * 3:
        return None
    try:
        model = VAR(clean)
        results = model.fit(maxlags=max_lag, ic='aic')
        return {
            'optimal_lag': results.k_ar,
            'aic': results.aic,
            'bic': results.bic,
            'params': results.params.to_dict(),
        }
    except Exception:
        return None

def dynamic_time_warping(s1, s2):
    """DTW distance between two series."""
    try:
        from dtaidistance import dtw
        a = s1.dropna().values
        b = s2.dropna().values
        # Normalize
        a = (a - a.mean()) / (a.std() + 1e-9)
        b = (b - b.mean()) / (b.std() + 1e-9)
        dist = dtw.distance(a, b)
        return float(dist)
    except Exception:
        return None

def compute_lead_lag_matrix(returns_df, max_lag=20):
    """
    Full pairwise lead-lag analysis.
    Returns DataFrame with columns: lead, lag, optimal_lag, correlation, granger_p, te, confidence
    """
    symbols = list(returns_df.columns)
    rows = []
    total = len(symbols) * (len(symbols) - 1)
    done = 0
    for i, s1 in enumerate(symbols):
        for j, s2 in enumerate(symbols):
            if i == j:
                continue
            r1 = returns_df[s1].dropna()
            r2 = returns_df[s2].dropna()
            if len(r1) < 30 or len(r2) < 30:
                continue
            lag_info = find_optimal_lag(r1, r2, max_lag)
            if lag_info is None:
                continue
            opt_lag = lag_info['optimal_lag']
            corr = lag_info['correlation']
            # Only consider positive lags (s1 leads s2)
            if opt_lag <= 0:
                done += 1
                continue
            gc = granger_causality(r1, r2, min(10, max_lag))
            gc_p = gc['p_value'] if gc else 1.0
            te_val = mutual_information(r1, r2)
            conf = _compute_confidence(corr, gc_p, te_val, len(r1))
            strength = abs(corr)
            rows.append({
                'lead': s1, 'lag_asset': s2,
                'optimal_lag': opt_lag,
                'correlation': round(corr, 4),
                'granger_p': round(gc_p, 4),
                'transfer_entropy': round(te_val, 4),
                'confidence': round(conf, 4),
                'p_value': round(gc_p, 4),
                'predictive_strength': round(strength, 4),
                'stability_score': round(_stability_score(r1, r2, opt_lag), 4),
                'influence_score': round(abs(corr) * (1 - gc_p), 4),
            })
            done += 1
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).sort_values('confidence', ascending=False)
    return df

def _compute_confidence(corr, gc_p, te, n):
    c = 0.0
    c += min(abs(corr), 1.0) * 0.4
    c += max(0, 1 - gc_p * 10) * 0.4
    c += min(te * 2, 1.0) * 0.2
    return min(c, 1.0)

def _stability_score(s1, s2, lag, n_splits=3):
    """Estimate stability of relationship across time windows."""
    df = pd.concat([s1, s2], axis=1).dropna()
    if len(df) < n_splits * 30:
        return 0.5
    chunk = len(df) // n_splits
    corrs = []
    for i in range(n_splits):
        sub = df.iloc[i*chunk:(i+1)*chunk]
        if len(sub) < 10:
            continue
        c = sub.iloc[:,0].corr(sub.iloc[:,1])
        corrs.append(c)
    if len(corrs) < 2:
        return 0.5
    std = np.std(corrs)
    return max(0.0, 1.0 - std * 2)

def pearson_corr(s1, s2):
    df = pd.concat([s1, s2], axis=1).dropna()
    if len(df) < 2:
        return 0, 1
    r, p = stats.pearsonr(df.iloc[:,0], df.iloc[:,1])
    return r, p

def spearman_corr(s1, s2):
    df = pd.concat([s1, s2], axis=1).dropna()
    if len(df) < 2:
        return 0, 1
    r, p = stats.spearmanr(df.iloc[:,0], df.iloc[:,1])
    return r, p

def kendall_corr(s1, s2):
    df = pd.concat([s1, s2], axis=1).dropna()
    if len(df) < 2:
        return 0, 1
    r, p = stats.kendalltau(df.iloc[:,0], df.iloc[:,1])
    return r, p

def regime_detection(prices, n_states=3):
    """HMM-based regime detection."""
    try:
        from hmmlearn import hmm
        returns = prices.pct_change().dropna().values.reshape(-1, 1)
        model = hmm.GaussianHMM(n_components=n_states, covariance_type='diag', n_iter=200)
        model.fit(returns)
        states = model.predict(returns)
        return states
    except Exception:
        return None

def change_point_detection(prices):
    """Detect structural breakpoints."""
    try:
        import ruptures as rpt
        signal = prices.pct_change().dropna().values
        model = rpt.Pelt(model='rbf').fit(signal)
        bkps = model.predict(pen=10)
        return bkps
    except Exception:
        return []
