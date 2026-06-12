import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

def build_features(prices_df, target_col, lag_features=10):
    """Build feature matrix from price data."""
    df = prices_df.copy()
    rets = df.pct_change()
    feats = pd.DataFrame(index=df.index)

    # Lagged returns of target
    for i in range(1, lag_features + 1):
        feats[f'ret_lag_{i}'] = rets[target_col].shift(i)

    # Technical features
    close = df[target_col]
    feats['ma5'] = close.rolling(5).mean() / close - 1
    feats['ma10'] = close.rolling(10).mean() / close - 1
    feats['ma20'] = close.rolling(20).mean() / close - 1
    feats['vol5'] = rets[target_col].rolling(5).std()
    feats['vol20'] = rets[target_col].rolling(20).std()
    feats['rsi14'] = _rsi(close, 14)
    feats['momentum'] = close / close.shift(10) - 1
    feats['high_low_ratio'] = (df.get('high', close) / df.get('low', close) - 1) if 'high' in df.columns else 0

    # Other assets as features
    for col in df.columns:
        if col != target_col:
            feats[f'{col}_ret'] = rets[col].shift(1)

    feats['target'] = rets[target_col]
    feats.dropna(inplace=True)
    return feats

def _rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - 100 / (1 + rs)

def train_xgboost(X_train, y_train):
    from xgboost import XGBRegressor
    model = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.05,
                         subsample=0.8, colsample_bytree=0.8, random_state=42,
                         n_jobs=-1, verbosity=0)
    model.fit(X_train, y_train, eval_set=[(X_train, y_train)], verbose=False)
    return model

def train_lightgbm(X_train, y_train):
    from lightgbm import LGBMRegressor
    model = LGBMRegressor(n_estimators=200, max_depth=5, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8, random_state=42,
                          n_jobs=-1, verbose=-1)
    model.fit(X_train, y_train)
    return model

def train_catboost(X_train, y_train):
    from catboost import CatBoostRegressor
    model = CatBoostRegressor(iterations=200, depth=5, learning_rate=0.05,
                               random_seed=42, verbose=0)
    model.fit(X_train, y_train)
    return model

def train_random_forest(X_train, y_train):
    from sklearn.ensemble import RandomForestRegressor
    model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    return model

def train_elasticnet(X_train, y_train):
    from sklearn.linear_model import ElasticNet
    model = ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=1000)
    model.fit(X_train, y_train)
    return model

MODEL_MAP = {
    'XGBoost': train_xgboost,
    'LightGBM': train_lightgbm,
    'CatBoost': train_catboost,
    'Random Forest': train_random_forest,
    'ElasticNet': train_elasticnet,
}

def run_forecast(prices_df, target_col, model_name='XGBoost', forecast_days=10, n_splits=3):
    """Full pipeline: features -> train -> predict -> backtest."""
    feats = build_features(prices_df, target_col)
    if len(feats) < 60:
        return None

    X = feats.drop('target', axis=1)
    y = feats['target']
    feature_names = list(X.columns)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_names, index=X.index)

    # Time-series cross validation
    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_scores = []
    for train_idx, val_idx in tscv.split(X_scaled):
        X_tr, X_val = X_scaled.iloc[train_idx], X_scaled.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
        try:
            m = MODEL_MAP[model_name](X_tr, y_tr)
            preds = m.predict(X_val)
            mse = mean_squared_error(y_val, preds)
            cv_scores.append(mse)
        except Exception:
            pass

    # Final model on all data
    train_fn = MODEL_MAP.get(model_name, train_xgboost)
    model = train_fn(X_scaled, y)
    in_sample_preds = model.predict(X_scaled)

    # Feature importance
    fi = get_feature_importance(model, feature_names, model_name)

    # SHAP values
    shap_vals = get_shap_values(model, X_scaled, model_name)

    # Forecast future returns
    last_features = X_scaled.iloc[-1:].values
    future_preds = []
    cur = last_features.copy()
    for _ in range(forecast_days):
        pred = model.predict(cur)[0]
        future_preds.append(pred)
        # Shift lag features
        cur = np.roll(cur, 1)
        cur[0, 0] = pred

    # Direction accuracy
    direction_acc = np.mean(np.sign(in_sample_preds) == np.sign(y.values))

    backtest = pd.Series(in_sample_preds, index=y.index, name='predicted')
    backtest_actual = y.copy()
    backtest_actual.name = 'actual'

    return {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'cv_mse': float(np.mean(cv_scores)) if cv_scores else None,
        'cv_rmse': float(np.sqrt(np.mean(cv_scores))) if cv_scores else None,
        'direction_accuracy': float(direction_acc),
        'future_returns': future_preds,
        'feature_importance': fi,
        'shap_values': shap_vals,
        'backtest_predicted': backtest,
        'backtest_actual': backtest_actual,
        'in_sample_mae': float(mean_absolute_error(y, in_sample_preds)),
    }

def get_feature_importance(model, feature_names, model_name):
    try:
        if hasattr(model, 'feature_importances_'):
            fi = pd.Series(model.feature_importances_, index=feature_names)
            return fi.sort_values(ascending=False).head(20)
        elif hasattr(model, 'coef_'):
            fi = pd.Series(np.abs(model.coef_), index=feature_names)
            return fi.sort_values(ascending=False).head(20)
    except Exception:
        pass
    return pd.Series()

def get_shap_values(model, X, model_name):
    try:
        import shap
        if model_name in ['XGBoost', 'LightGBM', 'CatBoost']:
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.LinearExplainer(model, X)
        shap_vals = explainer.shap_values(X)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[0]
        mean_shap = pd.Series(np.abs(shap_vals).mean(axis=0), index=X.columns)
        return mean_shap.sort_values(ascending=False).head(20)
    except Exception:
        return pd.Series()

def monte_carlo_forecast(prices, n_simulations=500, forecast_days=30):
    """Monte Carlo price simulation."""
    returns = prices.pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    last_price = prices.iloc[-1]
    sims = []
    for _ in range(n_simulations):
        rand_returns = np.random.normal(mu, sigma, forecast_days)
        path = [last_price]
        for r in rand_returns:
            path.append(path[-1] * (1 + r))
        sims.append(path[1:])
    sims = np.array(sims)
    return {
        'simulations': sims,
        'mean': sims.mean(axis=0),
        'p5': np.percentile(sims, 5, axis=0),
        'p25': np.percentile(sims, 25, axis=0),
        'p75': np.percentile(sims, 75, axis=0),
        'p95': np.percentile(sims, 95, axis=0),
        'last_price': last_price,
    }

def volatility_forecast(prices, window=20, forecast_days=10):
    """GARCH-like volatility forecast."""
    returns = prices.pct_change().dropna()
    hist_vol = returns.rolling(window).std() * np.sqrt(252)
    last_vol = hist_vol.iloc[-1]
    # Simple EWMA forecast
    ewm_vol = returns.ewm(span=window).std() * np.sqrt(252)
    forecast = ewm_vol.iloc[-1]
    return {
        'historical_vol': hist_vol,
        'ewm_vol': ewm_vol,
        'current_vol': last_vol,
        'forecast_vol': forecast,
    }
