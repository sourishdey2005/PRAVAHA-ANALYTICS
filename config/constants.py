APP_NAME = "PRAVAHA ANALYTICS"
APP_TAGLINE = "Tracing the Flow of Market Intelligence"
VERSION = "1.0.0"

NIFTY50 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS",
    "LT.NS","HCLTECH.NS","ASIANPAINT.NS","AXISBANK.NS","MARUTI.NS",
    "SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","BAJFINANCE.NS","WIPRO.NS",
    "NESTLEIND.NS","POWERGRID.NS","NTPC.NS","TECHM.NS","ONGC.NS",
    "TATAMOTORS.NS","BAJAJFINSV.NS","JSWSTEEL.NS","GRASIM.NS","TATASTEEL.NS",
    "INDUSINDBK.NS","ADANIENT.NS","COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS",
    "CIPLA.NS","EICHERMOT.NS","APOLLOHOSP.NS","HINDALCO.NS","TATACONSUM.NS",
    "BRITANNIA.NS","SBILIFE.NS","HDFCLIFE.NS","BPCL.NS","UPL.NS",
    "ADANIPORTS.NS","HEROMOTOCO.NS","M&M.NS","BAJAJ-AUTO.NS","SHREECEM.NS"
]

SP500_SAMPLE = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA","META","BRK-B","LLY","TSLA","V",
    "JPM","UNH","XOM","JNJ","WMT","MA","PG","HD","CVX","MRK",
    "ABBVIE","COST","PEP","ADBE","CRM","AMD","NFLX","INTC","CSCO","VZ",
    "TMO","ABT","ACN","MCD","NKE","DHR","TXN","LIN","PM","ORCL",
    "NEE","HON","AMGN","BMY","QCOM","RTX","UNP","IBM","SBUX","GS"
]

MACRO_INSTRUMENTS = {
    "Indices": ["^GSPC","^IXIC","^DJI","^RUT","^VIX","^NSEI","^BSESN","^N225","^FTSE","^GDAXI"],
    "Commodities": ["GC=F","SI=F","CL=F","NG=F","HG=F","ZW=F","ZC=F"],
    "Forex": ["EURUSD=X","GBPUSD=X","USDJPY=X","USDINR=X","DX-Y.NYB","AUDUSD=X","USDCNH=X"],
    "Bonds": ["^TNX","^TYX","^FVX","^IRX"],
    "Crypto": ["BTC-USD","ETH-USD","BNB-USD","SOL-USD","XRP-USD","DOGE-USD"],
    "ETFs": ["SPY","QQQ","IWM","EEM","GLD","SLV","USO","TLT","HYG","VEU"]
}

SECTORS = {
    "Technology": ["AAPL","MSFT","NVDA","AMD","INTC","CSCO","ORCL","IBM","TXN","QCOM"],
    "Finance": ["JPM","BAC","GS","MS","C","WFC","BLK","SCHW","AXP","USB"],
    "Healthcare": ["JNJ","UNH","LLY","ABT","TMO","DHR","BMY","AMGN","GILD","CVS"],
    "Energy": ["XOM","CVX","COP","SLB","EOG","PXD","MPC","VLO","PSX","OXY"],
    "Consumer": ["AMZN","TSLA","HD","MCD","NKE","SBUX","TGT","LOW","TJX","BKNG"],
}

PERIODS = ["1mo","3mo","6mo","1y","2y","3y","5y","10y"]
INTERVALS = ["1d","1wk","1mo"]

LAG_RANGE = 30  # max days
MIN_OBSERVATIONS = 60

THEME_COLORS = {
    "background": "#0a0e1a",
    "surface": "#0f1629",
    "surface2": "#151d35",
    "accent": "#00d4ff",
    "accent2": "#7c3aed",
    "accent3": "#f59e0b",
    "success": "#10b981",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "text": "#e2e8f0",
    "text_muted": "#64748b",
    "border": "#1e293b",
    "gradient1": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "gradient2": "linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)",
}
