import networkx as nx
import pandas as pd
import numpy as np

def build_lead_lag_network(lead_lag_df, min_confidence=0.3):
    """Build directed network from lead-lag results."""
    G = nx.DiGraph()
    if lead_lag_df is None or lead_lag_df.empty:
        return G
    for _, row in lead_lag_df.iterrows():
        if row['confidence'] >= min_confidence:
            G.add_edge(
                row['lead'], row['lag_asset'],
                weight=row['confidence'],
                lag=row['optimal_lag'],
                correlation=row['correlation'],
                p_value=row['p_value'],
            )
    return G

def compute_network_metrics(G):
    """Compute centrality and influence metrics."""
    if len(G.nodes) == 0:
        return {}
    metrics = {}
    try:
        pr = nx.pagerank(G, weight='weight')
        dc = dict(G.degree(weight='weight'))
        in_dc = dict(G.in_degree(weight='weight'))
        out_dc = dict(G.out_degree(weight='weight'))
        try:
            bc = nx.betweenness_centrality(G, weight='weight')
        except Exception:
            bc = {n: 0 for n in G.nodes}
        try:
            ec = nx.eigenvector_centrality(G, weight='weight', max_iter=300)
        except Exception:
            ec = {n: 0 for n in G.nodes}
        try:
            cc = nx.closeness_centrality(G)
        except Exception:
            cc = {n: 0 for n in G.nodes}
        for node in G.nodes:
            metrics[node] = {
                'pagerank': round(pr.get(node, 0), 6),
                'degree': dc.get(node, 0),
                'in_degree': in_dc.get(node, 0),
                'out_degree': out_dc.get(node, 0),
                'betweenness': round(bc.get(node, 0), 6),
                'eigenvector': round(ec.get(node, 0), 6),
                'closeness': round(cc.get(node, 0), 6),
                'influence_rank': round(pr.get(node, 0) * out_dc.get(node, 0), 6),
            }
    except Exception:
        pass
    return metrics

def detect_communities(G):
    """Community detection using greedy modularity."""
    if len(G.nodes) < 3:
        return {}
    try:
        UG = G.to_undirected()
        communities = nx.community.greedy_modularity_communities(UG, weight='weight')
        node_community = {}
        for i, comm in enumerate(communities):
            for node in comm:
                node_community[node] = i
        return node_community
    except Exception:
        return {}

def get_network_layout(G, layout='spring'):
    """Get node positions for visualization."""
    if len(G.nodes) == 0:
        return {}
    try:
        if layout == 'spring':
            return nx.spring_layout(G, k=2/np.sqrt(len(G.nodes)+1), seed=42)
        elif layout == 'circular':
            return nx.circular_layout(G)
        elif layout == 'kamada':
            return nx.kamada_kawai_layout(G)
        elif layout == 'shell':
            return nx.shell_layout(G)
        else:
            return nx.spring_layout(G, seed=42)
    except Exception:
        return nx.spring_layout(G, seed=42)

def network_to_plotly(G, layout='spring', metrics=None, communities=None, title='Lead-Lag Network'):
    """Convert NetworkX graph to Plotly figure."""
    import plotly.graph_objects as go
    if len(G.nodes) == 0:
        return go.Figure()
    pos = get_network_layout(G, layout)
    if not metrics:
        metrics = compute_network_metrics(G)
    if not communities:
        communities = detect_communities(G)

    colors = ['#00d4ff','#7c3aed','#f59e0b','#10b981','#ef4444',
              '#8b5cf6','#ec4899','#14b8a6','#f97316','#06b6d4']

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines',
        line=dict(width=0.8, color='rgba(100,116,139,0.5)'),
        hoverinfo='none', showlegend=False)

    node_x, node_y, node_text, node_hover, node_size, node_color = [], [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y)
        node_text.append(node)
        m = metrics.get(node, {})
        node_hover.append(
            f"<b>{node}</b><br>PageRank: {m.get('pagerank',0):.4f}<br>"
            f"Out-Degree: {m.get('out_degree',0)}<br>In-Degree: {m.get('in_degree',0)}<br>"
            f"Betweenness: {m.get('betweenness',0):.4f}"
        )
        size = 10 + m.get('pagerank', 0) * 2000
        node_size.append(min(size, 40))
        comm_id = communities.get(node, 0)
        node_color.append(colors[comm_id % len(colors)])

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        text=node_text, textposition='top center',
        marker=dict(size=node_size, color=node_color,
                    line=dict(width=1, color='rgba(255,255,255,0.3)'),
                    opacity=0.9),
        hovertext=node_hover, hoverinfo='text', showlegend=False
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=dict(text=title, font=dict(color='#e2e8f0', size=16)),
        paper_bgcolor='#0a0e1a', plot_bgcolor='#0f1629',
        font=dict(color='#e2e8f0'),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hovermode='closest', margin=dict(l=20, r=20, t=40, b=20),
        height=550,
    )
    return fig

def network_3d(G, metrics=None):
    """3D network visualization."""
    import plotly.graph_objects as go
    if len(G.nodes) == 0:
        return go.Figure()
    if not metrics:
        metrics = compute_network_metrics(G)
    pos2d = get_network_layout(G, 'spring')
    # Add z coordinate based on pagerank
    pos3d = {}
    for node, (x, y) in pos2d.items():
        z = metrics.get(node, {}).get('pagerank', 0) * 100
        pos3d[node] = (x, y, z)

    ex, ey, ez = [], [], []
    for u, v in G.edges():
        x0, y0, z0 = pos3d[u]
        x1, y1, z1 = pos3d[v]
        ex += [x0, x1, None]; ey += [y0, y1, None]; ez += [z0, z1, None]

    edge_trace = go.Scatter3d(x=ex, y=ey, z=ez, mode='lines',
        line=dict(color='rgba(100,116,139,0.4)', width=2),
        hoverinfo='none', showlegend=False)

    nx_, ny_, nz_, texts, sizes = [], [], [], [], []
    for node in G.nodes():
        x, y, z = pos3d[node]
        nx_.append(x); ny_.append(y); nz_.append(z)
        texts.append(node)
        sizes.append(8 + metrics.get(node, {}).get('pagerank', 0) * 1500)

    node_trace = go.Scatter3d(x=nx_, y=ny_, z=nz_, mode='markers+text',
        text=texts, textposition='top center',
        marker=dict(size=[min(s, 20) for s in sizes], color=nz_,
                    colorscale='Viridis', opacity=0.85,
                    line=dict(width=1, color='white')),
        hoverinfo='text', showlegend=False)

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        paper_bgcolor='#0a0e1a', plot_bgcolor='#0a0e1a',
        font=dict(color='#e2e8f0'),
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, backgroundcolor='#0a0e1a'),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, backgroundcolor='#0a0e1a'),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, backgroundcolor='#0a0e1a'),
            bgcolor='#0a0e1a',
        ),
        margin=dict(l=0, r=0, t=30, b=0), height=550,
    )
    return fig

def metrics_to_df(metrics):
    if not metrics:
        return pd.DataFrame()
    rows = [{'asset': k, **v} for k, v in metrics.items()]
    df = pd.DataFrame(rows)
    if 'pagerank' in df.columns:
        df = df.sort_values('pagerank', ascending=False)
    return df
