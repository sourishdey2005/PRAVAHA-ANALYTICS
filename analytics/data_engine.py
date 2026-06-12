import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import json

INDEX_NAMES = {
    '^GSPC': 'S&P 500',
    '^IXIC': 'NASDAQ Composite',
    '^DJI': 'Dow Jones Industrial Average',
    '^VIX': 'CBOE Volatility Index',
    '^NSEI': 'NIFTY 50',
    '^BSESN': 'S&P BSE SENSEX',
    '^N225': 'Nikkei 225',
    '^FTSE': 'FTSE 100',
    '^GDAXI': 'DAX',
    '^HSI': 'HANG SENG INDEX',
}

FALLBACK_MARKET_OVERVIEW = [
    {'symbol': '^IXIC', 'name': 'Nasdaq', 'price': 25809.66, 'change': 640.16, 'change_pct': 2.54, 'volume': 8863106000},
    {'symbol': '^VIX', 'name': 'VIX', 'price': 19.44, 'change': -2.78, 'change_pct': -12.51, 'volume': 0},
    {'symbol': '^NSEI', 'name': 'Nifty 50', 'price': 23344.30, 'change': 183.75, 'change_pct': 0.79, 'volume': 0},
    {'symbol': '^GSPC', 'name': 'S&P 500', 'price': 6200.0, 'change': 68.75, 'change_pct': 1.12, 'volume': 4500000000},
    {'symbol': '^DJI', 'name': 'Dow Jones', 'price': 43000.0, 'change': 375.0, 'change_pct': 0.88, 'volume': 450000000},
]

FALLBACK_SECTORS = {
    'Technology': {'symbol': 'XLK', 'change_pct': 1.42, 'price': 100.0},
    'Healthcare': {'symbol': 'XLV', 'change_pct': 0.36, 'price': 100.0},
    'Finance': {'symbol': 'XLF', 'change_pct': -0.44, 'price': 100.0},
    'Energy': {'symbol': 'XLE', 'change_pct': 0.92, 'price': 100.0},
    'Consumer Disc': {'symbol': 'XLY', 'change_pct': 0.18, 'price': 100.0},
    'Consumer Staples': {'symbol': 'XLP', 'change_pct': -0.12, 'price': 100.0},
    'Industrials': {'symbol': 'XLI', 'change_pct': 0.64, 'price': 100.0},
    'Materials': {'symbol': 'XLB', 'change_pct': 0.22, 'price': 100.0},
    'Utilities': {'symbol': 'XLU', 'change_pct': -0.31, 'price': 100.0},
    'Real Estate': {'symbol': 'XLRE', 'change_pct': 0.47, 'price': 100.0},
    'Communication': {'symbol': 'XLC', 'change_pct': 0.73, 'price': 100.0},
}


def _retry(provider_call, attempts=2):
    last_error = None
    for _ in range(attempts):
        try:
            return provider_call()
        except Exception as exc:
            last_error = exc
    if last_error is not None:
        return None
    return None


def _first_existing_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _parse_yfinance_history(data, symbols):
    result = {}
    if data is None or data.empty:
        return result
    for sym in symbols:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                if 1 in data.columns.names or 'Ticker' in data.columns.names:
                    df = data.xs(sym, axis=1, level=1).copy()
                else:
                    continue
            else:
                if len(symbols) != 1:
                    continue
                df = data.copy()
            df.columns = [str(c).lower() for c in df.columns]
            if 'adjclose' in df.columns:
                df = df.drop(columns=['adjclose'])
            df.index = pd.to_datetime(df.index)
            result[sym] = df
        except Exception:
            pass
    return result


def fetch_price_data(symbols, period='1y', interval='1d'):
    """Fetch OHLCV data. Returns dict of DataFrames."""
    if isinstance(symbols, str):
        symbols = [symbols]
    result = {}

    missing = list(symbols)
    yf_result = _retry(lambda: _retry_yfinance_history(missing, period, interval)) or {}
    result.update(yf_result)

    missing = [s for s in symbols if s not in result]
    if missing:
        yq_result = _retry(lambda: _retry_yahooquery_history(missing, period, interval)) or {}
        result.update(yq_result)
    return result


def _retry_yahooquery_history(symbols, period, interval):
    from yahooquery import Ticker
    t = Ticker(symbols, asynchronous=True)
    hist = t.history(period=period, interval=interval)
    result = {}
    if isinstance(hist, pd.DataFrame) and not hist.empty:
        if 'symbol' in hist.index.names:
            for sym in symbols:
                try:
                    df = hist.xs(sym, level='symbol').copy()
                    df.index = pd.to_datetime(df.index)
                    result[sym] = df
                except Exception:
                    pass
        else:
            result[symbols[0]] = hist
    return result


def _retry_yfinance_history(symbols, period, interval):
    import yfinance as yf
    data = yf.download(symbols, period=period, interval=interval, auto_adjust=True, progress=False, group_by='column')
    return _parse_yfinance_history(data, symbols)

@st.cache_data(ttl=300)
def get_prices(symbols, period='1y', interval='1d'):
    return fetch_price_data(symbols, period, interval)

@st.cache_data(ttl=300)
def get_close_prices(symbols, period='1y'):
    """Returns DataFrame of close prices, columns=symbols."""
    if isinstance(symbols, str):
        symbols = [symbols]
    data = fetch_price_data(symbols, period)
    closes = {}
    for sym, df in data.items():
        if df is not None and not df.empty:
            col = 'close' if 'close' in df.columns else ('Close' if 'Close' in df.columns else df.columns[0])
            closes[sym] = df[col]
    if not closes:
        return pd.DataFrame()
    return pd.DataFrame(closes).dropna(how='all')

@st.cache_data(ttl=300)
def get_returns(symbols, period='1y'):
    prices = get_close_prices(symbols, period)
    if prices.empty:
        return pd.DataFrame()
    return prices.pct_change().dropna()

def _market_overview_from_yfinance(indices, existing=None):
    import yfinance as yf
    existing = existing or {}
    data = yf.download(indices, period='2d', interval='1d', auto_adjust=False, progress=False, group_by='column')
    if data is None or data.empty:
        return []
    result = []
    for sym in indices:
        if sym in existing:
            result.append(existing[sym])
            continue
        try:
            if isinstance(data.columns, pd.MultiIndex):
                df = data.xs(sym, axis=1, level=1).copy()
            else:
                df = data.copy()
            close_col = _first_existing_column(df, ['Close', 'close'])
            vol_col = _first_existing_column(df, ['Volume', 'volume'])
            if close_col is None:
                continue
            close = pd.to_numeric(df[close_col], errors='coerce').dropna()
            if close.empty:
                continue
            price = float(close.iloc[-1])
            if len(close) >= 2:
                prev = float(close.iloc[-2])
                change = price - prev
                change_pct = (change / prev * 100) if prev else 0
            else:
                change = 0
                change_pct = 0
            result.append({
                'symbol': sym,
                'name': INDEX_NAMES.get(sym, sym),
                'price': price,
                'change': change,
                'change_pct': change_pct,
                'volume': float(pd.to_numeric(df[vol_col], errors='coerce').dropna().iloc[-1]) if vol_col else 0,
            })
        except Exception:
            pass
    return result


@st.cache_data(ttl=300)
def get_market_overview():
    indices = ["^GSPC","^IXIC","^DJI","^VIX","^NSEI","^BSESN","^N225","^FTSE","^GDAXI","^HSI"]
    result = _retry(lambda: _market_overview_from_yfinance(indices)) or []
    if not result:
        return FALLBACK_MARKET_OVERVIEW.copy()
    return result


@st.cache_data(ttl=300)
def get_sector_performance():
    sector_etfs = {
        'Technology': 'XLK', 'Healthcare': 'XLV', 'Finance': 'XLF',
        'Energy': 'XLE', 'Consumer Disc': 'XLY', 'Consumer Staples': 'XLP',
        'Industrials': 'XLI', 'Materials': 'XLB', 'Utilities': 'XLU',
        'Real Estate': 'XLRE', 'Communication': 'XLC'
    }
    result = _retry(lambda: _sector_performance_from_yfinance(sector_etfs)) or {}
    if not result:
        return FALLBACK_SECTORS.copy()
    return result


def _sector_performance_from_yfinance(sector_etfs, existing=None):
    import yfinance as yf
    existing = existing or {}
    data = yf.download(list(sector_etfs.values()), period='2d', interval='1d', auto_adjust=False, progress=False, group_by='column')
    if data is None or data.empty:
        return {}
    result = {}
    for sector, sym in sector_etfs.items():
        if sector in existing:
            result[sector] = existing[sector]
            continue
        try:
            if isinstance(data.columns, pd.MultiIndex):
                df = data.xs(sym, axis=1, level=1).copy()
            else:
                df = data.copy()
            close_col = _first_existing_column(df, ['Close', 'close'])
            if close_col is None:
                continue
            close = pd.to_numeric(df[close_col], errors='coerce').dropna()
            if len(close) < 2:
                continue
            price = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            change_pct = ((price - prev) / prev * 100) if prev else 0
            result[sector] = {'symbol': sym, 'change_pct': change_pct, 'price': price}
        except Exception:
            pass
    return result


@st.cache_data(ttl=600)
def search_assets(query, max_results=20):
    results = []
    try:
        from yahooquery import search
        data = search(query)
        quotes = data.get('quotes', [])[:max_results]
        for q in quotes:
            results.append({
                'symbol': q.get('symbol',''),
                'name': q.get('longname', q.get('shortname','')),
                'exchange': q.get('exchange',''),
                'type': q.get('quoteType',''),
            })
    except Exception:
        pass
    return results

def returns_to_series(prices_df, col):
    return prices_df[col].pct_change().dropna() if col in prices_df.columns else pd.Series()

def align_series(s1, s2):
    df = pd.concat([s1, s2], axis=1).dropna()
    if df.empty:
        return pd.Series(), pd.Series()
    return df.iloc[:,0], df.iloc[:,1]
