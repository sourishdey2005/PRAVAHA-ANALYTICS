import streamlit as st
import pandas as pd
from config.styles import inject_css, page_header, badge
from analytics.data_engine import get_close_prices
from analytics.lead_lag import compute_lead_lag_matrix
from network_engine.network import (build_lead_lag_network, compute_network_metrics,
                                     detect_communities, network_to_plotly, network_3d, metrics_to_df)
from config.constants import NIFTY50, SP500_SAMPLE, MACRO_INSTRUMENTS

def show():
    inject_css()
    page_header("Dependency Network", "Asset influence graph with PageRank & community detection", "🕸️")

    col_ctrl, col_main = st.columns([1, 3], gap="large")

    with col_ctrl:
        st.markdown("#### ⚙️ Configuration")
        universe_choice = st.selectbox("Asset Universe", ["Macro Mix", "Nifty 50", "S&P 500"], key="universe_choice")
        period = st.selectbox("Time Period", ["6mo","1y","2y"], index=1)
        max_lag = st.slider("Max Lag (days)", 5, 30, 15, help="Maximum lag for lead-lag computation")
        min_conf = st.slider("Min Confidence", 0.1, 0.8, 0.25, help="Minimum confidence for network edge")
        layout = st.selectbox("Network Layout", ["spring","circular","kamada","shell"])
        run = st.button("🕸️ Build Network", type="primary", use_container_width=True)

    if universe_choice == "Nifty 50":
        universe = NIFTY50[:15]
    elif universe_choice == "S&P 500":
        universe = SP500_SAMPLE[:15]
    else:
        universe = (MACRO_INSTRUMENTS['Indices'][:5] + MACRO_INSTRUMENTS['ETFs'][:5] +
                    MACRO_INSTRUMENTS['Commodities'][:4] + MACRO_INSTRUMENTS['Forex'][:4])

    with col_main:
        if not run:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px">
                <div style="font-size:2.5rem">🕸️</div>
                <div style="font-size:1.3rem;font-weight:700;color:#00d4ff;margin-top:16px">Network Analytics Engine</div>
                <div style="color:#64748b;margin-top:8px">Build the lead-lag network to discover asset influence hierarchies</div>
                <div style="margin-top:24px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
                    <span class="badge badge-blue">PageRank</span>
                    <span class="badge badge-green">Betweenness</span>
                    <span class="badge badge-gold">Community Detection</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        with st.spinner("Computing lead-lag matrix and building network…"):
            prices = get_close_prices(universe, period)
            if prices.empty:
                st.markdown("""
                <div class="card" style="text-align:center;padding:40px;border-color:#ef4444">
                    <div style="font-size:2rem;color:#ef4444">❌</div>
                    <div style="color:#ef4444;margin-top:8px">No data available for network construction</div>
                </div>
                """, unsafe_allow_html=True)
                return
            rets = prices.pct_change().dropna()
            ll_df = compute_lead_lag_matrix(rets, max_lag)
            G = build_lead_lag_network(ll_df, min_conf)
            metrics = compute_network_metrics(G)
            communities = detect_communities(G)

        st.success(f"Network built: {len(G.nodes)} nodes, {len(G.edges)} edges")

        tab1, tab2, tab3, tab4 = st.tabs(["🌐 2D Network", "🌐 3D Network", "📊 Metrics", "📋 Edges"])

        with tab1:
            fig = network_to_plotly(G, layout, metrics, communities)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig3d = network_3d(G, metrics)
            st.plotly_chart(fig3d, use_container_width=True)

        with tab3:
            metrics_df = metrics_to_df(metrics)
            if not metrics_df.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 🏆 Top Influencers (PageRank)")
                    top_pr = metrics_df.nlargest(5, 'pagerank')[['asset','pagerank','out_degree','in_degree']]
                    for _, row in top_pr.iterrows():
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;padding:10px 14px;
                        background:#151d35;border-radius:10px;margin:4px 0;border:1px solid #253452">
                            <span style="color:#00d4ff;font-weight:600">{row['asset']}</span>
                            <span class="badge badge-blue">PR={row['pagerank']:.5f}</span>
                        </div>""", unsafe_allow_html=True)
                
                with c2:
                    st.markdown("#### 🔗 Most Connected (Degree)")
                    top_deg = metrics_df.nlargest(5, 'degree')[['asset','degree','betweenness']]
                    for _, row in top_deg.iterrows():
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;padding:10px 14px;
                        background:#151d35;border-radius:10px;margin:4px 0;border:1px solid #253452">
                            <span style="color:#7c3aed;font-weight:600">{row['asset']}</span>
                            <span class="badge badge-gold">Deg={row['degree']:.0f}</span>
                        </div>""", unsafe_allow_html=True)
                
                st.markdown("#### Full Metrics Table")
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        with tab4:
            if ll_df is not None and not ll_df.empty:
                filtered = ll_df[ll_df['confidence'] >= min_conf]
                st.dataframe(filtered, use_container_width=True, hide_index=True)
                csv = filtered.to_csv(index=False).encode()
                st.download_button("📥 Download Edges CSV", csv, "network_edges.csv", "text/csv")