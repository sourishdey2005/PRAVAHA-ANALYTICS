import pandas as pd
import numpy as np
from datetime import datetime

def format_number(n, prefix='', suffix='', decimals=2):
    if n is None:
        return 'N/A'
    if abs(n) >= 1e12:
        return f"{prefix}{n/1e12:.{decimals}f}T{suffix}"
    if abs(n) >= 1e9:
        return f"{prefix}{n/1e9:.{decimals}f}B{suffix}"
    if abs(n) >= 1e6:
        return f"{prefix}{n/1e6:.{decimals}f}M{suffix}"
    return f"{prefix}{n:.{decimals}f}{suffix}"

def pct_format(v, decimals=2):
    if v is None:
        return 'N/A'
    sign = '+' if v >= 0 else ''
    return f"{sign}{v:.{decimals}f}%"

def color_pct(v):
    if v >= 0:
        return f'<span style="color:#10b981">▲ {v:.2f}%</span>'
    return f'<span style="color:#ef4444">▼ {abs(v):.2f}%</span>'

def safe_divide(a, b, default=0.0):
    return a / b if b != 0 else default

def annualize_return(r, n_periods, periods_per_year=252):
    return (1 + r) ** (periods_per_year / n_periods) - 1 if n_periods > 0 else 0

def max_drawdown(prices):
    roll_max = prices.cummax()
    drawdown = prices / roll_max - 1
    return drawdown.min()

def sharpe_ratio(returns, risk_free=0.0, periods=252):
    excess = returns - risk_free / periods
    if excess.std() == 0:
        return 0.0
    return excess.mean() / excess.std() * np.sqrt(periods)

def sortino_ratio(returns, risk_free=0.0, periods=252):
    excess = returns - risk_free / periods
    downside = excess[excess < 0].std()
    if downside == 0:
        return 0.0
    return excess.mean() / downside * np.sqrt(periods)

def calmar_ratio(prices, periods=252):
    returns = prices.pct_change().dropna()
    ann_ret = annualize_return(returns.sum(), len(returns), periods)
    mdd = max_drawdown(prices)
    return safe_divide(ann_ret, abs(mdd))

def validate_symbols(symbols):
    return [s.strip().upper() for s in symbols if s.strip()]

def parse_symbols(input_str):
    return validate_symbols(input_str.split(','))

def trading_days_between(d1, d2):
    bdays = pd.bdate_range(d1, d2)
    return len(bdays)

def describe_relationship(lag, corr):
    direction = "leads" if lag > 0 else "lags behind"
    strength = "strong" if abs(corr) > 0.6 else "moderate" if abs(corr) > 0.3 else "weak"
    sign = "positive" if corr > 0 else "negative"
    return f"{strength} {sign} {direction} by {abs(lag)} day(s)"
