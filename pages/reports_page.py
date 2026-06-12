import streamlit as st
import pandas as pd
import json
from config.styles import inject_css, page_header
from analytics.data_engine import get_close_prices
from analytics.lead_lag import compute_lead_lag_matrix
from reports.report_engine import (generate_pdf_report, generate_html_report,
                                    export_csv, export_excel, export_json, get_download_bytes)
from auth.auth_manager import current_user
from database.db import save_analysis, get_saved_analyses

def show():
    inject_css()
    page_header("Reports Center", "Generate & export professional financial reports", "📋")

    tab1, tab2, tab3 = st.tabs(["📄 Generate Report", "📥 Export Data", "🗂️ Saved Reports"])

    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("#### Report Configuration")
            report_name = st.text_input("Report Name", "Lead-Lag Analysis Report")
            report_type = st.selectbox("Report Type", [
                "Lead-Lag Summary", "Market Overview", "Portfolio Analysis", "Custom"
            ])
            assets_input = st.text_input("Assets", "SPY,QQQ,GLD,TLT,^VIX")
            symbols = [s.strip() for s in assets_input.split(',') if s.strip()]
            period = st.selectbox("Period", ["6mo","1y","2y"], index=1)
            fmt = st.selectbox("Format", ["HTML", "PDF"])
            gen = st.button("📄 Generate Report", type="primary", use_container_width=True)

        with col2:
            if gen:
                with st.spinner("Generating report…"):
                    filepath = _generate_report(report_name, report_type, symbols, period, fmt)
                if filepath:
                    st.success(f"Report generated!")
                    data = get_download_bytes(filepath)
                    if data:
                        ext = 'pdf' if fmt == 'PDF' else 'html'
                        mime = 'application/pdf' if fmt == 'PDF' else 'text/html'
                        st.download_button(f"📥 Download {fmt}", data,
                                           f"{report_name.replace(' ','_')}.{ext}", mime,
                                           use_container_width=True)
                    user = current_user()
                    save_analysis(user['id'], report_name, report_type, {'symbols': symbols, 'period': period})
                else:
                    st.error("Report generation failed. Check dependencies.")

    with tab2:
        st.markdown("#### Export Data")
        exp_assets = st.text_input("Assets to Export", "AAPL,MSFT,GOOGL,TSLA")
        exp_syms = [s.strip() for s in exp_assets.split(',') if s.strip()]
        exp_period = st.selectbox("Period", ["6mo","1y","2y"], key='exp_period')
        exp_fmt = st.selectbox("Format", ["CSV", "Excel", "JSON"])

        if st.button("📥 Export", type="primary"):
            with st.spinner("Fetching & exporting…"):
                prices = get_close_prices(exp_syms, exp_period)
            if prices.empty:
                st.error("No data.")
            else:
                rets = prices.pct_change().dropna()
                if exp_fmt == "CSV":
                    fp = export_csv(prices, "pravaha_prices.csv")
                    data = get_download_bytes(fp)
                    st.download_button("📥 Download CSV", data, "pravaha_prices.csv", "text/csv")
                elif exp_fmt == "Excel":
                    fp = export_excel({'Prices': prices, 'Returns': rets}, "pravaha_data.xlsx")
                    data = get_download_bytes(fp)
                    st.download_button("📥 Download Excel", data, "pravaha_data.xlsx",
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                elif exp_fmt == "JSON":
                    payload = {
                        'symbols': exp_syms, 'period': exp_period,
                        'prices': prices.tail(30).to_dict(),
                        'returns': rets.tail(30).to_dict()
                    }
                    fp = export_json(payload, "pravaha_data.json")
                    data = get_download_bytes(fp)
                    st.download_button("📥 Download JSON", data, "pravaha_data.json", "application/json")

    with tab3:
        user = current_user()
        saved = get_saved_analyses(user['id'])
        if saved:
            for s in saved:
                cfg = json.loads(s['config']) if isinstance(s['config'], str) else s['config']
                st.markdown(f"""
                <div class="card" style="padding:14px 18px;margin:6px 0">
                    <div style="display:flex;justify-content:space-between">
                        <div>
                            <span style="font-weight:700;color:#e2e8f0">{s['name']}</span>
                            <span class="badge badge-blue" style="margin-left:8px">{s['analysis_type']}</span>
                        </div>
                        <div style="color:#64748b;font-size:0.8rem">{s['created_at'][:10]}</div>
                    </div>
                    <div style="color:#64748b;font-size:0.8rem;margin-top:4px">
                        Assets: {', '.join(cfg.get('symbols', [])[:5])} · Period: {cfg.get('period','N/A')}
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No saved reports yet. Generate a report to save it here.")

def _generate_report(name, report_type, symbols, period, fmt):
    prices = get_close_prices(symbols, period)
    if prices.empty:
        return None

    rets = prices.pct_change().dropna()
    sections = [
        {'type': 'heading', 'content': 'Executive Summary'},
        {'type': 'text', 'content': f'This report covers {len(symbols)} assets over a {period} period.'},
        {'type': 'metrics_row', 'metrics': [
            {'label': 'Assets Analyzed', 'value': str(len(symbols))},
            {'label': 'Period', 'value': period},
            {'label': 'Data Points', 'value': str(len(prices))},
            {'label': 'Report Type', 'value': report_type},
        ]},
        {'type': 'heading', 'content': 'Price Summary'},
    ]

    # Stats table
    stats_rows = []
    for sym in symbols:
        if sym not in prices.columns:
            continue
        s = prices[sym].dropna()
        r = rets[sym].dropna() if sym in rets.columns else pd.Series()
        stats_rows.append({
            'Symbol': sym,
            'Start Price': round(s.iloc[0], 4),
            'End Price': round(s.iloc[-1], 4),
            'Return (%)': round((s.iloc[-1]/s.iloc[0]-1)*100, 2),
            'Volatility (%)': round(r.std()*252**0.5*100, 2) if len(r) > 0 else 0,
            'Sharpe': round(r.mean()/r.std()*252**0.5, 2) if len(r) > 0 and r.std() > 0 else 0,
        })
    sections.append({'type': 'table', 'content': pd.DataFrame(stats_rows)})

    if report_type == "Lead-Lag Summary":
        sections.append({'type': 'heading', 'content': 'Lead-Lag Analysis'})
        with st.spinner("Computing lead-lag matrix for report…"):
            ll_df = compute_lead_lag_matrix(rets, max_lag=15)
        if not ll_df.empty:
            sections.append({'type': 'table', 'content': ll_df.head(20)})

    sections.append({'type': 'heading', 'content': 'Correlation Analysis'})
    corr = rets[symbols[:8]].corr().round(4) if len(symbols) >= 2 else pd.DataFrame()
    if not corr.empty:
        sections.append({'type': 'table', 'content': corr.reset_index()})

    if fmt == "PDF":
        return generate_pdf_report(name, sections)
    else:
        return generate_html_report(name, sections)
