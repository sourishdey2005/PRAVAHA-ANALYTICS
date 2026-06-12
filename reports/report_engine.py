import os
import io
import json
import pandas as pd
import numpy as np
from datetime import datetime

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports_output')
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_pdf_report(title, sections, filename=None):
    """Generate a PDF report with sections."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        if filename is None:
            filename = f"pravaha_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                     fontSize=24, textColor=colors.HexColor('#00d4ff'),
                                     alignment=TA_CENTER, spaceAfter=6)
        story.append(Paragraph('⚡ PRAVAHA ANALYTICS', title_style))
        story.append(Paragraph(title, styles['Heading2']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#1e293b')))
        story.append(Spacer(1, 0.3*inch))

        for section in sections:
            stype = section.get('type', 'text')
            if stype == 'heading':
                story.append(Paragraph(section['content'], styles['Heading2']))
            elif stype == 'text':
                story.append(Paragraph(section['content'], styles['Normal']))
            elif stype == 'table':
                df = section['content']
                if isinstance(df, pd.DataFrame) and not df.empty:
                    data = [list(df.columns)]
                    for _, row in df.iterrows():
                        data.append([str(v) for v in row.values])
                    t = Table(data[:50], repeatRows=1)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f1629')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#00d4ff')),
                        ('FONTSIZE', (0,0), (-1,-1), 8),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#151d35'), colors.HexColor('#1a2540')]),
                        ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#1e293b')),
                        ('TOPPADDING', (0,0), (-1,-1), 3),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                    ]))
                    story.append(t)
            elif stype == 'metric':
                label = section.get('label', '')
                value = section.get('value', '')
                story.append(Paragraph(f"<b>{label}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.15*inch))

        doc.build(story)
        return filepath
    except Exception as e:
        return None

def generate_html_report(title, sections, filename=None):
    """Generate a styled HTML report."""
    if filename is None:
        filename = f"pravaha_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(REPORTS_DIR, filename)

    html_sections = ''
    for section in sections:
        stype = section.get('type', 'text')
        if stype == 'heading':
            html_sections += f'<h2 class="section-title">{section["content"]}</h2>'
        elif stype == 'text':
            html_sections += f'<p class="text">{section["content"]}</p>'
        elif stype == 'table':
            df = section.get('content')
            if isinstance(df, pd.DataFrame) and not df.empty:
                html_sections += df.head(100).to_html(classes='data-table', index=False, border=0)
        elif stype == 'metric':
            html_sections += f'''
            <div class="metric-box">
                <div class="metric-label">{section.get("label","")}</div>
                <div class="metric-value">{section.get("value","")}</div>
            </div>'''
        elif stype == 'metrics_row':
            html_sections += '<div class="metrics-row">'
            for m in section.get('metrics', []):
                html_sections += f'''
                <div class="metric-box">
                    <div class="metric-label">{m.get("label","")}</div>
                    <div class="metric-value">{m.get("value","")}</div>
                </div>'''
            html_sections += '</div>'

    html = f'''<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>PRAVAHA - {title}</title>
<style>
body{{background:#0a0e1a;color:#e2e8f0;font-family:'Segoe UI',sans-serif;margin:0;padding:0}}
.header{{background:linear-gradient(135deg,#0f1629,#151d35);padding:40px;border-bottom:1px solid #1e293b}}
.logo{{font-size:2rem;font-weight:800;background:linear-gradient(135deg,#00d4ff,#7c3aed);
-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.report-title{{font-size:1.4rem;color:#e2e8f0;margin-top:8px}}
.meta{{color:#64748b;font-size:0.85rem;margin-top:4px}}
.content{{padding:40px;max-width:1200px;margin:0 auto}}
.section-title{{color:#00d4ff;font-size:1.3rem;border-bottom:1px solid #1e293b;padding-bottom:8px;margin:32px 0 16px}}
.text{{color:#94a3b8;line-height:1.7;margin:8px 0}}
.metrics-row{{display:flex;gap:16px;flex-wrap:wrap;margin:16px 0}}
.metric-box{{background:#151d35;border:1px solid #1e293b;border-radius:12px;padding:16px;min-width:150px;flex:1}}
.metric-label{{color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px}}
.metric-value{{color:#00d4ff;font-size:1.5rem;font-weight:700;margin-top:4px}}
.data-table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:0.85rem}}
.data-table th{{background:#0f1629;color:#00d4ff;padding:10px 12px;text-align:left;border-bottom:1px solid #1e293b}}
.data-table td{{padding:8px 12px;border-bottom:1px solid #1a2540;color:#94a3b8}}
.data-table tr:hover td{{background:#151d35}}
.footer{{background:#0f1629;padding:24px 40px;border-top:1px solid #1e293b;color:#64748b;font-size:0.8rem;text-align:center}}
</style></head>
<body>
<div class="header">
    <div class="logo">⚡ PRAVAHA ANALYTICS</div>
    <div class="report-title">{title}</div>
    <div class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
<div class="content">{html_sections}</div>
<div class="footer">PRAVAHA ANALYTICS — Tracing the Flow of Market Intelligence</div>
</body></html>'''

    with open(filepath, 'w') as f:
        f.write(html)
    return filepath

def export_csv(df, filename=None):
    if filename is None:
        filename = f"pravaha_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)
    df.to_csv(filepath)
    return filepath

def export_excel(dfs_dict, filename=None):
    """Export multiple DataFrames to Excel sheets."""
    if filename is None:
        filename = f"pravaha_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(REPORTS_DIR, filename)
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, df in dfs_dict.items():
            if isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=sheet_name[:31])
    return filepath

def export_json(data, filename=None):
    if filename is None:
        filename = f"pravaha_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    return filepath

def get_download_bytes(filepath):
    """Read file as bytes for Streamlit download."""
    if filepath and os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return f.read()
    return None
