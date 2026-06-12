# ⚡ PRAVAHA ANALYTICS
### *Tracing the Flow of Market Intelligence*

An institutional-grade financial intelligence platform for lead-lag discovery, causal inference, ML forecasting, and network analytics.

---

## 🚀 Quick Start

```bash
# 1. Create virtual environment (recommended)
python -m venv venv
#source venv/bin/activate        # Linux/Mac
venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
streamlit run app.py
```

Open your browser at `http://localhost:8501`

**Demo credentials:** `demo` / `demo123`

---

## 🏗️ Architecture

```
pravaha_analytics/
├── app.py                    # Main entry point
├── database/
│   └── db.py                 # SQLite ORM + migrations
├── auth/
│   └── auth_manager.py       # JWT authentication
├── config/
│   ├── constants.py          # Asset universes, settings
│   └── styles.py             # CSS + UI helpers
├── analytics/
│   ├── data_engine.py        # Market data (yahooquery/yfinance)
│   └── lead_lag.py           # Correlation, Granger, TE, DTW
├── ml_models/
│   └── forecasting.py        # XGBoost, LightGBM, CatBoost, SHAP
├── network_engine/
│   └── network.py            # NetworkX graph analytics
├── visualizations/
│   └── charts.py             # 50+ Plotly chart functions
├── reports/
│   └── report_engine.py      # PDF/HTML/CSV/Excel export
└── pages/
    ├── dashboard.py
    ├── market_overview.py
    ├── asset_explorer.py
    ├── lead_lag_page.py
    ├── causal_page.py
    ├── forecast_page.py
    ├── network_page.py
    ├── visuals_page.py
    ├── analytics_3d.py
    ├── portfolio_page.py
    ├── reports_page.py
    ├── watchlists_page.py
    └── settings_page.py
```

---

## 📊 Features

### Lead-Lag Discovery
- Cross-correlation analysis
- Granger causality testing
- Transfer entropy
- Dynamic Time Warping
- PCMCI causal discovery

### Machine Learning
- XGBoost, LightGBM, CatBoost
- Random Forest, ElasticNet
- SHAP explainability
- Monte Carlo simulation
- Volatility forecasting

### Network Analytics
- PageRank influence scoring
- Betweenness centrality
- Community detection
- 2D & 3D network graphs

### Visualizations (50+)
- Candlestick, OHLC, Volume
- Correlation heatmaps
- 3D surfaces (correlation, lead-lag, PCA)
- Feature importance, SHAP
- Monte Carlo fan charts

### Asset Universe
- Nifty 50, S&P 500, Nasdaq 100
- ETFs, Forex, Commodities
- Crypto, Bonds, Indices

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Charts | Plotly, Altair |
| Data | yahooquery, yfinance |
| ML | XGBoost, LightGBM, CatBoost, SHAP |
| Stats | statsmodels, scipy, pingouin |
| Networks | NetworkX |
| Database | SQLite |
| Auth | JWT + bcrypt |

---

## 📈 Sample Relationships

| Lead Asset | Lag Asset | Typical Lag |
|-----------|-----------|-------------|
| US10Y Treasury | QQQ | 3 days |
| DXY (Dollar) | Gold | 5 days |
| Crude Oil | Airlines | 4 days |
| VIX | SPY | 1-2 days |
| USDINR | Indian IT | 2-3 days |
| Bitcoin | Crypto Equities | 1-2 days |

---

## 📝 License
MIT License — For educational and research use.
