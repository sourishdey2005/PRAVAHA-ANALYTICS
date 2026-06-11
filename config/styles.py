PRAVAHA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #0f1629;
    --bg-tertiary: #151d35;
    --bg-card: #1a2540;
    --border-primary: #1e293b;
    --border-secondary: #253452;
    --border-accent: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-muted: #64748b;
    --text-inverse: #0f172a;
    
    --accent-blue: #00d4ff;
    --accent-purple: #7c3aed;
    --accent-gold: #f59e0b;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    --accent-pink: #ec4899;
    
    --gradient-primary: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
    --gradient-success: linear-gradient(135deg, #10b981, #059669);
    --gradient-danger: linear-gradient(135deg, #ef4444, #dc2626);
    
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.15);
    
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 20px;
    --radius-full: 9999px;
    
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-primary) !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

[data-testid="stHeader"] { background: transparent !important; }

h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.25rem; }

a { color: var(--accent-blue) !important; text-decoration: none; }

/* ── Professional Card Components ────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin: 8px 0;
    transition: all var(--transition-normal);
    position: relative;
    overflow: hidden;
}

.card:hover {
    border-color: var(--accent-blue);
    box-shadow: var(--shadow-glow);
}

.card--elevated {
    box-shadow: var(--shadow-xl);
}

.card--gradient {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-tertiary));
    border: 1px solid var(--border-accent);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-primary);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
}

.card-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ── Glassmorphism Effect ────────────────────────── */
.glass {
    background: rgba(21, 30, 53, 0.6) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: var(--radius-lg) !important;
}

.glass--strong {
    background: rgba(15, 22, 41, 0.8) !important;
    backdrop-filter: blur(24px) !important;
}

/* ── Metric Cards ────────────────────────── */
.metric-card {
    background: linear-gradient(145deg, var(--bg-card), var(--bg-tertiary));
    border: 1px solid var(--border-secondary);
    border-radius: var(--radius-xl);
    padding: 24px;
    text-align: center;
    transition: all var(--transition-normal);
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent-blue);
    letter-spacing: -0.02em;
}

.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
}

.metric-delta {
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 6px;
}

/* ── Badges & Tags ────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all var(--transition-fast);
}

.badge:hover { transform: scale(1.05); }

.badge-blue {
    background: rgba(0, 212, 255, 0.15);
    color: var(--accent-blue);
    border: 1px solid rgba(0, 212, 255, 0.3);
}

.badge-purple {
    background: rgba(124, 58, 237, 0.15);
    color: var(--accent-purple);
    border: 1px solid rgba(124, 58, 237, 0.3);
}

.badge-green {
    background: rgba(16, 185, 129, 0.15);
    color: var(--accent-green);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-red {
    background: rgba(239, 68, 68, 0.15);
    color: var(--accent-red);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-gold {
    background: rgba(245, 158, 11, 0.15);
    color: var(--accent-gold);
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-pink {
    background: rgba(236, 72, 153, 0.15);
    color: var(--accent-pink);
    border: 1px solid rgba(236, 72, 153, 0.3);
}

/* ── Page Headers ────────────────────────── */
.page-header {
    padding: 24px 0 20px;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border-primary);
}

.page-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 12px;
}

.page-subtitle {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 6px;
}

/* ── Sidebar Logo ────────────────────────── */
.sidebar-logo {
    padding: 24px 20px;
    border-bottom: 1px solid var(--border-primary);
    margin-bottom: 16px;
    text-align: center;
}

.sidebar-logo .logo-mark {
    width: 50px;
    height: 50px;
    margin: 0 auto 12px;
    border-radius: var(--radius-lg);
    background: conic-gradient(from 160deg, #00d4ff, #7c3aed, #f59e0b, #00d4ff);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: var(--shadow-glow);
}

.sidebar-logo .logo-mark::before {
    content: '';
    position: absolute;
    inset: 9px;
    border-radius: var(--radius-md);
    background: var(--bg-secondary);
    clip-path: polygon(52% 0, 62% 31%, 96% 31%, 68% 51%, 79% 84%, 52% 64%, 25% 84%, 36% 51%, 8% 31%, 42% 31%);
}

.sidebar-logo .logo-text {
    font-size: 1.3rem;
    font-weight: 800;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sidebar-logo .logo-tagline {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Buttons ────────────────────────── */
.stButton > button {
    background: var(--gradient-primary) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    transition: all var(--transition-normal) !important;
    box-shadow: var(--shadow-md) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Primary button variant */
button[kind="primary"] {
    background: var(--gradient-primary) !important;
}

/* Secondary button variant */
.stButton > button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* ── Inputs ────────────────────────── */
.stTextInput input,
.stSelectbox > div > div,
.stMultiselect > div > div,
.stNumberInput input,
.stTextArea textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-secondary) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-md) !important;
    font-size: 0.9rem !important;
    transition: border-color var(--transition-fast) !important;
}

.stTextInput input:focus,
.stSelectbox > div > div:focus-within,
.stMultiselect > div > div:focus-within {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1) !important;
}

/* ── Forms ────────────────────────── */
.stForm {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 20px;
}

/* ── Tabs ────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-tertiary) !important;
    border-radius: var(--radius-full) !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid var(--border-primary) !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    border-radius: var(--radius-full) !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: all var(--transition-fast) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--gradient-primary) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
}

/* ── DataFrame & Tables ────────────────────────── */
.stDataFrame {
    background: var(--bg-card) !important;
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.stDataFrame thead {
    background: var(--bg-tertiary) !important;
}

/* ── Progress & Alerts ────────────────────────── */
.stProgress > div > div {
    background: var(--gradient-primary) !important;
    border-radius: var(--radius-full) !important;
    height: 8px !important;
}

.stProgress > div {
    background: var(--bg-tertiary) !important;
    border-radius: var(--radius-full) !important;
}

.stAlert {
    border-radius: var(--radius-lg) !important;
    border: none !important;
    padding: 16px !important;
}

.stAlert[data-baseweb="notification"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-secondary) !important;
}

/* Success alert */
.stAlert[data-baseweb="notification"][aria-label*="success"] {
    background: rgba(16, 185, 129, 0.15) !important;
    border-color: var(--accent-green) !important;
}

/* Error alert */
.stAlert[data-baseweb="notification"][aria-label*="error"] {
    background: rgba(239, 68, 68, 0.15) !important;
    border-color: var(--accent-red) !important;
}

/* ── Expander ────────────────────────── */
div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-secondary) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden;
}

/* ── Metrics ────────────────────────── */
.stMetric {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-secondary) !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px !important;
    transition: all var(--transition-normal) !important;
}

.stMetric:hover {
    border-color: var(--accent-blue) !important;
    box-shadow: var(--shadow-md) !important;
}

.stMetric label {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
}

.stMetric [data-testid="metric-container"] {
    color: var(--accent-blue) !important;
    font-weight: 700 !important;
}

/* ── Utils ────────────────────────── */
.mono {
    font-family: 'JetBrains Mono', monospace !important;
}

.positive { color: var(--accent-green) !important; }
.negative { color: var(--accent-red) !important; }
.neutral { color: var(--accent-gold) !important; }

/* ── Lead-Lag Results Card ────────────────────────── */
.lead-lag-result {
    background: linear-gradient(145deg, rgba(124, 58, 237, 0.12), rgba(0, 212, 255, 0.08));
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: var(--radius-xl);
    padding: 20px;
    margin: 12px 0;
    position: relative;
    overflow: hidden;
}

.lead-lag-result::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--gradient-primary);
}

.confidence-bar {
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-full);
    overflow: hidden;
    margin: 12px 0 8px;
}

.confidence-fill {
    height: 100%;
    border-radius: var(--radius-full);
    background: var(--gradient-primary);
}

/* ── Animations ────────────────────────── */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
}

.pulse { animation: pulse 2s infinite; }
.skeleton {
    background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-tertiary) 50%, var(--bg-card) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--radius-md);
}

/* ── Scrollbar ────────────────────────── */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--border-secondary);
    border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-purple);
}

/* ── Hide Streamlit Branding ────────────────────────── */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header { visibility: hidden !important; }

/* ── Divider ────────────────────────── */
.stMarkdown hr {
    border: none;
    height: 1px;
    background: var(--border-primary);
    margin: 24px 0;
}

/* ── Chart Container ────────────────────────── */
.plotly-chart-container {
    border-radius: var(--radius-lg);
    overflow: hidden;
}

/* ── Responsive ────────────────────────── */
@media (max-width: 768px) {
    .page-title { font-size: 1.5rem; }
    .metric-value { font-size: 1.5rem; }
    .card { padding: 16px; }
}

@media (max-width: 480px) {
    .page-title { font-size: 1.25rem; }
    .metric-value { font-size: 1.25rem; }
}
</style>
"""

AUTH_CSS = """
<style>
.auth-shell {
    min-height: 100vh;
    margin: 0;
    padding: 2rem 1rem;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background:
        linear-gradient(135deg, rgba(10, 16, 36, 0.95), rgba(15, 24, 56, 0.9)),
        radial-gradient(circle at 20% 30%, rgba(0, 212, 255, 0.15), transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(124, 58, 237, 0.15), transparent 40%);
}

.auth-shell::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 50px 50px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent 90%);
    pointer-events: none;
}

.auth-brand-lockup {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    margin-bottom: 2rem;
    position: relative;
    z-index: 1;
}

.auth-logo {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-xl);
    background: conic-gradient(from 160deg, #00d4ff, #7c3aed, #f59e0b, #00d4ff);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 50px rgba(0, 212, 255, 0.4);
    animation: float 6s ease-in-out infinite;
}

.auth-logo::before {
    content: '';
    position: absolute;
    inset: 14px;
    border-radius: var(--radius-lg);
    background: var(--bg-primary);
    clip-path: polygon(52% 0, 62% 31%, 96% 31%, 68% 51%, 79% 84%, 52% 64%, 25% 84%, 36% 51%, 8% 31%, 42% 31%);
}

.auth-title {
    font-size: clamp(2.5rem, 6vw, 3.5rem);
    font-weight: 800;
    letter-spacing: -0.05em;
    background: linear-gradient(135deg, #ffffff, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    line-height: 1.1;
}

.auth-subtitle {
    font-size: clamp(0.9rem, 2vw, 1.1rem);
    color: var(--text-secondary);
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    text-align: center;
}

.auth-content-grid {
    width: 100%;
    max-width: 1100px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 24px;
    position: relative;
    z-index: 1;
}

.auth-card {
    background: rgba(21, 30, 53, 0.7);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-xl);
    padding: 32px;
    box-shadow: var(--shadow-xl);
    position: relative;
    overflow: hidden;
}

.auth-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, transparent 0 30%, rgba(0, 212, 255, 0.1) 45%, transparent 60%);
    transform: translateX(-120%);
    animation: auth-sweep 8s ease-in-out infinite;
    pointer-events: none;
}

.auth-card > * { position: relative; z-index: 1; }

.auth-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.auth-card-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
}

.auth-card-subtitle {
    color: var(--text-muted);
    font-size: 0.85rem;
}

.auth-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: var(--radius-full);
    border: 1px solid rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.1);
    color: #86efac;
    font-size: 0.75rem;
    font-weight: 600;
}

.auth-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent-green);
    box-shadow: 0 0 10px var(--accent-green);
    animation: pulse 2s infinite;
}

.auth-feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-top: 20px;
}

.auth-feature {
    padding: 16px;
    border-radius: var(--radius-lg);
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(0, 212, 255, 0.15);
    backdrop-filter: blur(12px);
    transition: all var(--transition-normal);
}

.auth-feature:hover {
    border-color: var(--accent-blue);
    transform: translateX(4px);
}

.auth-feature strong {
    display: block;
    color: var(--text-primary);
    font-size: 0.85rem;
    margin-bottom: 6px;
}

.auth-feature span {
    color: var(--text-muted);
    font-size: 0.75rem;
    line-height: 1.4;
}

.auth-side-panel {
    margin-top: 20px;
    padding: 16px;
    border-radius: var(--radius-lg);
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(16px);
}

.auth-side-panel-title {
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.75rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.auth-metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}

.auth-metric {
    padding: 12px 8px;
    border-radius: var(--radius-md);
    background: rgba(124, 58, 237, 0.1);
    border: 1px solid rgba(124, 58, 237, 0.2);
    text-align: center;
}

.auth-metric b {
    display: block;
    color: var(--accent-blue);
    font-size: 1rem;
    margin-bottom: 4px;
}

.auth-metric span {
    color: var(--text-muted);
    font-size: 0.7rem;
}

.auth-demo {
    margin-top: 16px;
    padding: 12px;
    border-radius: var(--radius-md);
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    font-size: 0.8rem;
}

.auth-note {
    margin-top: 12px;
    color: var(--text-muted);
    font-size: 0.75rem;
    text-align: center;
}

.auth-card .stTabs {
    margin-top: 12px;
}

.auth-card .stTabs [data-baseweb="tab-list"] {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid var(--border-secondary) !important;
    border-radius: var(--radius-full) !important;
    padding: 3px !important;
}

.auth-card .stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    border-radius: var(--radius-full) !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}

.auth-card .stTabs [aria-selected="true"] {
    background: var(--gradient-primary) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
}

.auth-card .stTextInput,
.auth-card .stCheckbox {
    margin: 12px 0 !important;
}

.auth-card .stTextInput label,
.auth-card .stCheckbox label {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}

.auth-card .stTextInput input {
    background: rgba(12, 18, 36, 0.8) !important;
    border: 1px solid var(--border-secondary) !important;
    border-radius: var(--radius-md) !important;
    height: 42px !important;
    color: var(--text-primary) !important;
}

.auth-card .stCheckbox > div:first-child {
    border-radius: var(--radius-sm) !important;
    border-color: var(--accent-blue) !important;
}

.auth-card .stButton button {
    border-radius: var(--radius-md) !important;
    padding: 12px 20px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
}

@keyframes auth-sweep {
    0%, 60% { transform: translateX(-120%); }
    80%, 100% { transform: translateX(120%); }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

@media (max-width: 768px) {
    .auth-content-grid { grid-template-columns: 1fr; }
    .auth-card { padding: 24px; }
    .auth-metric-row { grid-template-columns: 1fr; }
}
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(PRAVAHA_CSS, unsafe_allow_html=True)

def auth_css():
    import streamlit as st
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

def page_header(title, subtitle='', icon=''):
    import streamlit as st
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{icon} {title}</div>
        <div class="page-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, delta=None, prefix='', suffix=''):
    delta_html = ''
    if delta is not None:
        cls = 'positive' if delta >= 0 else 'negative'
        sign = '+' if delta >= 0 else ''
        delta_html = f'<div class="{cls}" style="font-size:0.85rem">{sign}{delta:.2f}%</div>'
    import streamlit as st
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{prefix}{value}{suffix}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def badge(text, color='blue'):
    import streamlit as st
    st.markdown(f'<span class="badge badge-{color}">{text}</span>', unsafe_allow_html=True)

def sidebar_logo():
    import streamlit as st
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <div class="logo-mark">
            <div style="position:relative;z-index:2;color:white;font-weight:800;font-size:1.2rem;">⚡</div>
        </div>
        <div>
            <div class="logo-text">PRAVAHA</div>
            <div class="logo-tagline">Market Intelligence Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)