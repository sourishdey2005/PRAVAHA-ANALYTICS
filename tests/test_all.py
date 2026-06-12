import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest
import pandas as pd
import numpy as np

class TestLeadLag(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        n = 300
        self.s1 = pd.Series(np.random.randn(n), name='A')
        lag = 5
        # Low noise for clear signal
        noise = np.random.randn(n) * 0.1
        self.s2 = pd.Series(
            np.concatenate([np.zeros(lag), self.s1.values[:-lag]]) + noise,
            name='B'
        )

    def test_cross_correlation(self):
        from analytics.lead_lag import cross_correlation
        xcorr = cross_correlation(self.s1, self.s2, max_lag=20)
        self.assertIsInstance(xcorr, dict)
        self.assertIn(5, xcorr)
        self.assertIn(5, xcorr)  # lag 5 exists in dict

    def test_find_optimal_lag(self):
        from analytics.lead_lag import find_optimal_lag
        result = find_optimal_lag(self.s1, self.s2, max_lag=20)
        self.assertIsNotNone(result)
        self.assertIn('optimal_lag', result)

    def test_granger_causality(self):
        from analytics.lead_lag import granger_causality
        result = granger_causality(self.s1, self.s2, max_lag=10)
        self.assertIsNotNone(result)
        self.assertIn('p_value', result)
        self.assertIn('significant', result)

    def test_mutual_information(self):
        from analytics.lead_lag import mutual_information
        mi = mutual_information(self.s1, self.s2)
        self.assertIsInstance(mi, float)
        self.assertGreaterEqual(mi, 0)

    def test_rolling_correlation(self):
        from analytics.lead_lag import rolling_correlation
        rc = rolling_correlation(self.s1, self.s2, window=20)
        self.assertFalse(rc.empty)

    def test_stability_score(self):
        from analytics.lead_lag import _stability_score
        score = _stability_score(self.s1, self.s2, lag=5)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)


class TestDatabase(unittest.TestCase):
    def setUp(self):
        import tempfile
        from database import db
        self.orig_path = db.DB_PATH
        db.DB_PATH = os.path.join(tempfile.mkdtemp(), 'test.db')
        db.init_db()

    def tearDown(self):
        from database import db
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
        db.DB_PATH = self.orig_path

    def test_create_and_get_user(self):
        from database.db import create_user, get_user
        ok, msg = create_user('testuser', 'test@test.com', 'pass123', 'Test User')
        self.assertTrue(ok)
        user = get_user('testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')

    def test_verify_password(self):
        from database.db import create_user, verify_password
        create_user('pwtest', 'pw@test.com', 'secure123')
        self.assertTrue(verify_password('pwtest', 'secure123'))
        self.assertFalse(verify_password('pwtest', 'wrong'))

    def test_duplicate_user(self):
        from database.db import create_user
        ok1, _ = create_user('dup', 'dup@test.com', 'pass')
        ok2, _ = create_user('dup', 'dup2@test.com', 'pass')
        self.assertTrue(ok1)
        self.assertFalse(ok2)

    def test_watchlists(self):
        from database.db import create_user, get_user, save_watchlist, get_watchlists
        create_user('wluser', 'wl@test.com', 'pass')
        user = get_user('wluser')
        save_watchlist(user['id'], 'Tech', ['AAPL','MSFT'], 'Test WL')
        wls = get_watchlists(user['id'])
        self.assertEqual(len(wls), 1)
        self.assertEqual(wls[0]['name'], 'Tech')


class TestForecasting(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        n = 300
        idx = pd.date_range('2022-01-01', periods=n, freq='B')
        prices = pd.Series(100 * np.exp(np.cumsum(np.random.randn(n) * 0.01)), index=idx)
        self.prices_df = pd.DataFrame({'SPY': prices})

    def test_build_features(self):
        from ml_models.forecasting import build_features
        feats = build_features(self.prices_df, 'SPY')
        self.assertFalse(feats.empty)
        self.assertIn('target', feats.columns)

    def test_run_forecast_elasticnet(self):
        from ml_models.forecasting import run_forecast
        result = run_forecast(self.prices_df, 'SPY', 'ElasticNet', forecast_days=5)
        self.assertIsNotNone(result)
        self.assertIn('direction_accuracy', result)
        self.assertIn('future_returns', result)
        self.assertEqual(len(result['future_returns']), 5)

    def test_monte_carlo(self):
        from ml_models.forecasting import monte_carlo_forecast
        result = monte_carlo_forecast(self.prices_df['SPY'], n_simulations=50, forecast_days=10)
        self.assertIn('mean', result)
        self.assertEqual(len(result['mean']), 10)


class TestNetwork(unittest.TestCase):
    def setUp(self):
        import pandas as pd
        self.ll_df = pd.DataFrame([
            {'lead':'SPY','lag_asset':'QQQ','optimal_lag':2,'correlation':0.7,'p_value':0.01,
             'confidence':0.8,'transfer_entropy':0.1,'predictive_strength':0.7,'stability_score':0.6,'influence_score':0.6},
            {'lead':'GLD','lag_asset':'SPY','optimal_lag':3,'correlation':-0.4,'p_value':0.04,
             'confidence':0.5,'transfer_entropy':0.08,'predictive_strength':0.4,'stability_score':0.5,'influence_score':0.4},
        ])

    def test_build_network(self):
        from network_engine.network import build_lead_lag_network
        G = build_lead_lag_network(self.ll_df, min_confidence=0.3)
        self.assertGreater(len(G.nodes), 0)
        self.assertGreater(len(G.edges), 0)

    def test_network_metrics(self):
        from network_engine.network import build_lead_lag_network, compute_network_metrics
        G = build_lead_lag_network(self.ll_df, min_confidence=0.3)
        metrics = compute_network_metrics(G)
        self.assertIsInstance(metrics, dict)
        for v in metrics.values():
            self.assertIn('pagerank', v)

    def test_community_detection(self):
        from network_engine.network import build_lead_lag_network, detect_communities
        G = build_lead_lag_network(self.ll_df, 0.3)
        comms = detect_communities(G)
        self.assertIsInstance(comms, dict)


class TestHelpers(unittest.TestCase):
    def test_format_number(self):
        from utils.helpers import format_number
        self.assertEqual(format_number(1_500_000), '1.50M')
        self.assertEqual(format_number(2_000_000_000), '2.00B')

    def test_max_drawdown(self):
        from utils.helpers import max_drawdown
        prices = pd.Series([100, 110, 90, 95, 80, 100])
        mdd = max_drawdown(prices)
        self.assertLess(mdd, 0)

    def test_sharpe_ratio(self):
        from utils.helpers import sharpe_ratio
        rets = pd.Series(np.random.randn(252) * 0.01 + 0.001)
        sr = sharpe_ratio(rets)
        self.assertIsInstance(sr, float)

    def test_validate_symbols(self):
        from utils.helpers import validate_symbols
        result = validate_symbols(['aapl', ' msft ', 'GOOGL'])
        self.assertEqual(result, ['AAPL', 'MSFT', 'GOOGL'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
