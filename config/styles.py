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
/* Base Reset and Background Injection */
[data-testid="stAppViewContainer"] {
    background-image: 
        radial-gradient(circle at 30% 30%, rgba(124, 58, 237, 0.25), transparent 50%),
        radial-gradient(circle at 70% 70%, rgba(0, 212, 255, 0.2), transparent 50%),
        linear-gradient(135deg, rgba(3, 7, 18, 0.85) 0%, rgba(15, 23, 42, 0.75) 50%, rgba(3, 7, 18, 0.9) 100%),
        url('https://wallpapercave.com/wp/wp8379331.jpg') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

/* Ensure no default overlays cover the content */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* Centering the entire auth container in the viewport */
.block-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 20px !important;
    min-height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 32px !important;
}

.auth-left-panel {
    padding: 40px;
    border-radius: 24px;
    background: rgba(15, 23, 42, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(24px) !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3) !important;
}

.auth-logo-section {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
}

.auth-logo-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: conic-gradient(from 180deg, #7c3aed, #00d4ff, #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white !important;
}

.auth-logo-text {
    font-size: 2.2rem;
    font-weight: 950;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #ffffff, #93c5fd, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.auth-logo-subtitle {
    font-size: 0.8rem;
    color: #94a3b8;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
    margin-top: 2px;
}

.auth-left-panel .auth-intro {
    font-size: 1.15rem;
    line-height: 1.6;
    color: #cbd5e1;
    margin-bottom: 32px;
}

.auth-shell {
    min-height: 100vh;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 15% 20%, rgba(0, 212, 255, 0.14), transparent 28%),
        radial-gradient(circle at 85% 10%, rgba(124, 58, 237, 0.16), transparent 24%),
        radial-gradient(circle at 80% 80%, rgba(245, 158, 11, 0.10), transparent 25%),
        linear-gradient(180deg, #08101f 0%, #0a1223 45%, #060b15 100%);
}

.auth-shell::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 52px 52px;
    mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.8), transparent 95%);
    pointer-events: none;
}

.auth-shell > div {
    position: relative;
    z-index: 1;
}

.auth-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    margin-bottom: 18px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(15, 23, 42, 0.45);
    color: #cbd5e1;
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.auth-page {
    min-height: 100vh;
    padding: 2px 0 12px;
}

.auth-hero-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: linear-gradient(135deg, #10b981, #00d4ff);
    box-shadow: 0 0 18px rgba(16, 185, 129, 0.8);
}

.auth-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 18px;
}

.auth-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 14px;
}

.auth-card-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -0.03em;
}

.auth-card-subtitle {
    margin-top: 6px;
    color: #94a3b8;
    font-size: 0.92rem;
    line-height: 1.5;
}

.auth-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid rgba(16, 185, 129, 0.18);
    background: rgba(16, 185, 129, 0.08);
    color: #bbf7d0;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.auth-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #10b981;
    box-shadow: 0 0 14px rgba(16, 185, 129, 0.85);
}

.auth-landing-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(360px, 0.9fr);
    gap: 14px;
    align-items: start;
}

.auth-hero-wrap {
    margin-top: 0;
    margin-bottom: 6px;
}

.auth-left-panel, .auth-card {
    transform: translateY(0);
}

.auth-feature {
    padding: 12px 14px;
    border-radius: 16px;
    background: rgba(3, 7, 18, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.auth-feature:hover {
    border-color: rgba(0, 212, 255, 0.3);
    background: rgba(3, 7, 18, 0.6);
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.auth-feature strong {
    display: block;
    color: #f1f5f9;
    font-size: 0.95rem;
    margin-bottom: 4px;
    font-weight: 600;
}

.auth-feature span {
    color: #64748b;
    font-size: 0.8rem;
    line-height: 1.5;
}

.auth-side-panel {
    padding: 16px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    background: rgba(3, 7, 18, 0.3);
}

.auth-side-panel-title {
    color: #94a3b8;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.auth-metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 8px;
}

.auth-metric {
    padding: 10px 8px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    text-align: center;
    transition: all 0.3s ease;
}

.auth-metric:hover {
    border-color: rgba(124, 58, 237, 0.3);
    background: rgba(255, 255, 255, 0.04);
}

.auth-metric b {
    display: block;
    color: #ffffff;
    font-size: 1.3rem;
    margin-bottom: 4px;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.auth-metric span {
    color: #64748b;
    font-size: 0.75rem;
}

.auth-mini-list {
    display: grid;
    gap: 10px;
    margin-bottom: 12px;
}

.auth-mini-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 10px 12px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.auth-mini-icon {
    width: 34px;
    height: 34px;
    flex: 0 0 34px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(0, 212, 255, 0.20));
    color: #e0f2fe;
    font-weight: 800;
}

.auth-mini-item strong {
    display: block;
    color: #f8fafc;
    font-size: 0.92rem;
    margin-bottom: 4px;
}

.auth-mini-item span {
    color: #94a3b8;
    font-size: 0.82rem;
    line-height: 1.45;
}

.auth-form-shell {
    display: grid;
    gap: 8px;
}

.auth-form-note {
    color: #94a3b8;
    font-size: 0.78rem;
    line-height: 1.25;
    margin-top: -8px;
}

.auth-form-shell label {
    color: #cbd5e1 !important;
    font-weight: 600 !important;
}

.auth-form-shell input {
    border-radius: 14px !important;
}

@media (max-width: 900px) {
    .auth-landing-grid {
        grid-template-columns: 1fr;
    }

    .auth-page {
        padding-top: 10px;
    }

    .auth-header-center {
        margin-top: 20px !important;
        margin-bottom: 22px !important;
    }

    .auth-feature-grid {
        grid-template-columns: 1fr;
    }

    .auth-card-header {
        flex-direction: column;
    }

    .auth-card {
        padding: 28px !important;
    }
}

.auth-card {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(30px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 24px !important;
    padding: 28px 30px !important;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4) !important;
    position: relative;
    overflow: hidden;
}

.auth-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #7c3aed, #00d4ff, #7c3aed);
}

.auth-header-center {
    text-align: center;
    width: 100%;
    max-width: 920px;
    margin: 22px auto 4px;
    display: grid;
    justify-items: center;
    gap: 2px;
}

.auth-hero-title {
    font-size: clamp(2.2rem, 4vw, 4rem) !important;
    font-weight: 950 !important;
    letter-spacing: -0.05em !important;
    line-height: 1 !important;
    margin-bottom: 0 !important;
    background: linear-gradient(135deg, #ffffff 0%, #e0f7ff 50%, #8be9ff 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-shadow: 0 4px 20px rgba(0, 212, 255, 0.15) !important;
}

.auth-hero-subtitle {
    font-size: clamp(0.9rem, 1.5vw, 1.15rem) !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #00d4ff !important;
    text-shadow: 0 0 15px rgba(0, 212, 255, 0.4) !important;
}

.auth-brand-line {
    margin-top: 0;
    color: #f8fafc;
    font-weight: 950;
    letter-spacing: -0.06em;
    font-size: clamp(1.8rem, 3vw, 2.8rem);
    line-height: 0.95;
}

.auth-brand-line span {
    display: block;
    margin-top: 2px;
    font-size: 0.34em;
    font-weight: 700;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #94a3b8;
}

.auth-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 18px;
    margin-bottom: 28px;
}

.auth-card-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
}

.auth-card-subtitle {
    color: #94a3b8;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-top: 6px;
}

.auth-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 100px;
    border: 1px solid rgba(16, 185, 129, 0.2);
    background: rgba(16, 185, 129, 0.08);
    color: #34d399;
    font-size: 0.75rem;
    font-weight: 600;
}

.auth-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
}

.auth-card .stTabs {
    margin-top: 0;
}

.auth-card .stTabs [data-baseweb="tab-list"] {
    background: rgba(3, 7, 18, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    gap: 4px !important;
}

.auth-card .stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    flex: 1;
    text-align: center;
}

.auth-card .stTabs [aria-selected="true"] {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.auth-card .stForm {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-top: 8px;
}

.auth-card .stTextInput {
    margin-bottom: 8px !important;
}

.auth-card .stTextInput label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
}

.auth-card .stTextInput input {
    background: rgba(3, 7, 18, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    height: 48px !important;
    color: #ffffff !important;
    font-size: 0.95rem !important;
    padding: 0 16px !important;
    transition: all 0.2s ease !important;
}

.auth-card .stTextInput input:focus {
    border-color: rgba(0, 212, 255, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15) !important;
    background: rgba(3, 7, 18, 0.6) !important;
}

.auth-card .stCheckbox {
    margin: 6px 0 10px 0 !important;
}

.auth-card .stCheckbox label {
    color: #64748b !important;
    font-size: 0.85rem !important;
}

.auth-card .stButton button {
    border-radius: 10px !important;
    height: 40px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #7c3aed, #00d4ff) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2) !important;
    transition: all 0.2s ease !important;
}

.auth-card .stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
}

.auth-demo {
    margin-top: 24px;
    padding: 16px;
    border-radius: 12px;
    background: rgba(16, 185, 129, 0.05);
    border: 1px solid rgba(16, 185, 129, 0.1);
    color: #a7f3d0;
    font-size: 0.85rem;
    line-height: 1.5;
}

.auth-demo code {
    color: #34d399;
    background: rgba(16, 185, 129, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 1024px) {
    .auth-content-grid {
        grid-template-columns: 1fr;
    }

    .auth-left-panel {
        margin-right: 0;
        margin-bottom: 24px;
    }
}

@media (max-width: 768px) {
    .auth-left-panel {
        padding: 16px;
    }

    .auth-feature-grid {
        grid-template-columns: 1fr;
    }

    .auth-card {
        padding: 16px;
    }
}
 </style>
"""

AUTH_CSS = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #07101d !important;
}

.auth-shell {
    min-height: auto;
    position: relative;
    overflow: hidden;
    background: #07101d;
}

.auth-shell::before {
    content: none;
}

.auth-shell::after {
    content: none;
}

.auth-page {
    min-height: auto;
    position: relative;
    z-index: 1;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

section.main {
    margin-left: 0 !important;
}

.block-container {
    max-width: 1240px !important;
    margin: 0 auto !important;
    padding: 8px 18px 10px !important;
    min-height: 100vh !important;
}

.auth-header-center {
    display: grid;
    justify-items: center;
    gap: 0px;
    text-align: center;
    max-width: 880px;
    margin: 0 auto 4px;
}

.auth-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    background: rgba(15, 23, 42, 0.54);
    color: #dbeafe;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.auth-hero-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: linear-gradient(135deg, #34d399, #38bdf8);
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.7);
}

.auth-brand-line {
    color: #f8fafc;
    font-weight: 950;
    letter-spacing: -0.07em;
    font-size: clamp(2.3rem, 4vw, 4.4rem);
    line-height: 0.95;
}

.auth-brand-line span {
    display: block;
    margin-top: 0;
    color: #8ea0b8;
    font-size: 0.28em;
    font-weight: 700;
    letter-spacing: 0.32em;
    text-transform: uppercase;
}

.auth-hero-copy {
    max-width: 760px;
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.2;
}

.auth-landing-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.08fr) minmax(360px, 0.92fr);
    gap: 8px;
    align-items: start;
}

.auth-left-panel,
.auth-card {
    position: relative;
    overflow: hidden;
    border-radius: 28px;
    border: 1px solid rgba(148, 163, 184, 0.08);
    background: rgba(9, 16, 30, 0.70);
    backdrop-filter: blur(24px);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
}

.auth-left-panel {
    padding: 18px;
}

.auth-left-panel::before,
.auth-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), transparent 34%);
    pointer-events: none;
}

.auth-logo-section {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 12px;
}

.auth-logo-icon {
    width: 54px;
    height: 54px;
    border-radius: 18px;
    display: grid;
    place-items: center;
    background: linear-gradient(145deg, #0ea5e9, #7c3aed 65%, #f59e0b);
    color: white !important;
    font-size: 1.35rem;
    font-weight: 900;
    box-shadow: 0 18px 32px rgba(14, 165, 233, 0.24);
}

.auth-logo-text {
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    color: #ffffff;
}

.auth-logo-subtitle {
    margin-top: 3px;
    color: #90a4bf;
    font-size: 0.78rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}

.auth-left-panel .auth-intro {
    color: #d7e2f2;
    font-size: 0.98rem;
    line-height: 1.45;
    margin-bottom: 12px;
}

.auth-mini-list {
    display: grid;
    gap: 8px;
    margin-bottom: 10px;
}

.auth-mini-item {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 10px 12px;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.10);
    background: rgba(15, 23, 42, 0.42);
}

.auth-mini-icon {
    width: 32px;
    height: 32px;
    flex: 0 0 32px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.24), rgba(124, 58, 237, 0.22));
    color: #e0f2fe;
    font-weight: 900;
}

.auth-mini-item strong,
.auth-feature strong {
    display: block;
    color: #f8fafc;
    font-size: 0.9rem;
    margin-bottom: 4px;
}

.auth-mini-item span,
.auth-feature span {
    color: #94a3b8;
    font-size: 0.78rem;
    line-height: 1.35;
}

.auth-feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-bottom: 10px;
}

.auth-feature {
    padding: 10px 12px;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.10);
    background: rgba(15, 23, 42, 0.38);
    transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
}

.auth-feature:hover,
.auth-mini-item:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.26);
    background: rgba(15, 23, 42, 0.52);
}

.auth-side-panel {
    padding: 12px;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.10);
    background: rgba(15, 23, 42, 0.34);
}

.auth-side-panel-title {
    color: #9fb1c7;
    font-weight: 800;
    font-size: 0.74rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.auth-metric-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
}

.auth-metric {
    text-align: center;
    padding: 10px 8px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(148, 163, 184, 0.10);
}

.auth-metric b {
    display: block;
    font-size: 1.1rem;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 4px;
    background: linear-gradient(135deg, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.auth-metric span {
    color: #94a3b8;
    font-size: 0.7rem;
}

.auth-card {
    padding: 18px;
}

.auth-card::before {
    height: 4px;
    background: linear-gradient(90deg, #0ea5e9, #22c55e, #f59e0b);
}

.auth-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 18px;
    margin-bottom: 10px;
}

.auth-card-title {
    font-size: 1.3rem;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.04em;
}

.auth-card-subtitle {
    margin-top: 6px;
    color: #93a4ba;
    font-size: 0.84rem;
    line-height: 1.35;
}

.auth-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    border: 1px solid rgba(34, 197, 94, 0.20);
    background: rgba(34, 197, 94, 0.09);
    color: #bbf7d0;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.auth-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #22c55e;
    box-shadow: 0 0 14px rgba(34, 197, 94, 0.7);
}

.auth-form-note {
    color: #93a4ba;
    font-size: 0.78rem;
    line-height: 1.35;
    margin: 0 0 8px;
}

.auth-form-shell {
    display: grid;
    gap: 6px;
}

.auth-card .stTabs {
    margin-top: 8px;
}

.auth-card .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(15, 23, 42, 0.32);
    padding: 4px;
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.10);
}

.auth-card .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
}

.auth-card .stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.20), rgba(124, 58, 237, 0.18)) !important;
}

.auth-card .stTextInput,
.auth-card .stCheckbox,
.auth-card .stButton {
    margin-top: 0;
}

.auth-card .stTextInput label,
.auth-card .stCheckbox label {
    color: #dbe7f4 !important;
    font-weight: 600 !important;
}

.auth-card .stTextInput input {
    border-radius: 12px !important;
    background: rgba(15, 23, 42, 0.75) !important;
    border: 1px solid rgba(148, 163, 184, 0.16) !important;
    color: #f8fafc !important;
}

.auth-card .stTextInput input:focus {
    border-color: rgba(56, 189, 248, 0.55) !important;
    box-shadow: 0 0 0 0.18rem rgba(56, 189, 248, 0.12) !important;
}

.auth-card .stButton button {
    border-radius: 12px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    border: 0 !important;
    box-shadow: 0 18px 30px rgba(37, 99, 235, 0.28) !important;
}

.auth-card .stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 22px 36px rgba(37, 99, 235, 0.34) !important;
}

.auth-demo {
    margin-top: 10px;
    padding: 10px 12px;
    border-radius: 14px;
    border: 1px solid rgba(34, 197, 94, 0.16);
    background: rgba(34, 197, 94, 0.06);
    color: #d1fae5;
    font-size: 0.86rem;
    line-height: 1.6;
}

.auth-demo code {
    color: #6ee7b7;
    background: rgba(34, 197, 94, 0.12);
    padding: 2px 6px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 980px) {
    .auth-landing-grid {
        grid-template-columns: 1fr;
    }

    .auth-feature-grid,
    .auth-metric-row {
        grid-template-columns: 1fr;
    }

    .auth-card-header {
        flex-direction: column;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding: 8px 12px 10px !important;
    }

    .auth-left-panel,
    .auth-card {
        padding: 14px;
        border-radius: 18px;
    }

    .auth-logo-text {
        font-size: 1.7rem;
    }

    .auth-brand-line {
        font-size: clamp(2rem, 11vw, 3rem);
    }
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
