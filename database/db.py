import sqlite3
import os
import bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'pravaha.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            theme TEXT DEFAULT 'dark',
            default_exchange TEXT DEFAULT 'NSE',
            default_period TEXT DEFAULT '1y',
            notifications INTEGER DEFAULT 1,
            preferences TEXT DEFAULT '{}',
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            symbols TEXT DEFAULT '[]',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS saved_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            analysis_type TEXT,
            config TEXT DEFAULT '{}',
            result_summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            layout TEXT DEFAULT '{}',
            widgets TEXT DEFAULT '[]',
            is_default INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            report_type TEXT,
            config TEXT DEFAULT '{}',
            file_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()

    # Seed demo user
    try:
        pw = bcrypt.hashpw(b'demo123', bcrypt.gensalt()).decode()
        c.execute("INSERT OR IGNORE INTO users (username, email, password_hash, full_name, role) VALUES (?,?,?,?,?)",
                  ('demo', 'demo@pravaha.ai', pw, 'Demo User', 'admin'))
        conn.commit()
        uid = c.execute("SELECT id FROM users WHERE username='demo'").fetchone()['id']
        c.execute("INSERT OR IGNORE INTO settings (user_id) VALUES (?)", (uid,))

        # Sample watchlists
        wl = [
            ('Indian Banking', 'Top Indian banking stocks', '["HDFCBANK.NS","ICICIBANK.NS","KOTAKBANK.NS","SBIN.NS","AXISBANK.NS"]'),
            ('US Technology', 'Top US tech stocks', '["AAPL","MSFT","GOOGL","NVDA","META","AMZN"]'),
            ('Global Macro', 'Macro instruments', '["GC=F","CL=F","DX-Y.NYB","^TNX","^VIX","GLD"]'),
            ('Crypto Leaders', 'Top crypto assets', '["BTC-USD","ETH-USD","BNB-USD","SOL-USD"]'),
            ('Energy', 'Energy sector', '["XOM","CVX","CL=F","NG=F","SLB","HAL"]'),
        ]
        for name, desc, syms in wl:
            c.execute("INSERT OR IGNORE INTO watchlists (user_id, name, description, symbols) VALUES (?,?,?,?)",
                      (uid, name, desc, syms))
        conn.commit()
    except Exception:
        pass
    conn.close()

def get_user(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=? OR email=?", (username, username)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username, email, password, full_name=''):
    conn = get_conn()
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        conn.execute("INSERT INTO users (username, email, password_hash, full_name) VALUES (?,?,?,?)",
                     (username, email, pw_hash, full_name))
        conn.commit()
        uid = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()['id']
        conn.execute("INSERT INTO settings (user_id) VALUES (?)", (uid,))
        conn.commit()
        return True, "User created"
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def verify_password(username, password):
    user = get_user(username)
    if not user:
        return False
    return bcrypt.checkpw(password.encode(), user['password_hash'].encode())

def update_last_login(user_id):
    conn = get_conn()
    conn.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

def get_watchlists(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM watchlists WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_watchlist(user_id, name, symbols, description=''):
    conn = get_conn()
    import json
    syms = json.dumps(symbols) if isinstance(symbols, list) else symbols
    conn.execute("INSERT INTO watchlists (user_id, name, description, symbols) VALUES (?,?,?,?)",
                 (user_id, name, description, syms))
    conn.commit()
    conn.close()

def update_watchlist(wl_id, symbols):
    conn = get_conn()
    import json
    syms = json.dumps(symbols) if isinstance(symbols, list) else symbols
    conn.execute("UPDATE watchlists SET symbols=?, updated_at=? WHERE id=?",
                 (syms, datetime.now().isoformat(), wl_id))
    conn.commit()
    conn.close()

def delete_watchlist(wl_id):
    conn = get_conn()
    conn.execute("DELETE FROM watchlists WHERE id=?", (wl_id,))
    conn.commit()
    conn.close()

def save_analysis(user_id, name, analysis_type, config, result_summary=''):
    conn = get_conn()
    import json
    cfg = json.dumps(config) if isinstance(config, dict) else config
    conn.execute("INSERT INTO saved_analyses (user_id, name, analysis_type, config, result_summary) VALUES (?,?,?,?,?)",
                 (user_id, name, analysis_type, cfg, result_summary))
    conn.commit()
    conn.close()

def get_saved_analyses(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM saved_analyses WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_settings(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM settings WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}

def update_settings(user_id, **kwargs):
    conn = get_conn()
    for k, v in kwargs.items():
        conn.execute(f"UPDATE settings SET {k}=? WHERE user_id=?", (v, user_id))
    conn.commit()
    conn.close()

def log_audit(user_id, action, details=''):
    conn = get_conn()
    conn.execute("INSERT INTO audit_logs (user_id, action, details) VALUES (?,?,?)",
                 (user_id, action, details))
    conn.commit()
    conn.close()
