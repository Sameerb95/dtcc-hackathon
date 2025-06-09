# src/utils/graph_plotting.py
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

def plot_networkx_graph(graph: nx.DiGraph, title: str = "Difference Graph"):
    """Plots a NetworkX graph using Plotly."""
    if not graph.nodes():
        st.info("Graph is empty. Nothing to plot.")
        return

    pos = nx.spring_layout(graph, k=0.7, iterations=50, seed=42) # Use a seed for consistent layout

    edge_x = []
    edge_y = []
    
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_texts_hover = []
    node_texts_display = []
    node_colors = []
    node_sizes = []

    for node_id, data in graph.nodes(data=True):
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)

        status = data.get('change_status', 'unknown')
        label = data.get('label', str(node_id))
        node_texts_display.append(label)

        color = 'rgba(100, 100, 200, 0.8)' # default
        size = 15
        if status == 'added':
            color = 'rgba(0, 200, 0, 0.8)' # Green
            size = 18
        elif status == 'modified':
            color = 'rgba(255, 165, 0, 0.8)' # Orange
            size = 18
        elif status == 'implicit_from_edge':
            color = 'rgba(200, 200, 200, 0.8)' # Light Grey
            size = 12
        node_colors.append(color)
        node_sizes.append(size)

        hover_text = f"<b>{label}</b><br>ID: {node_id}<br>Status: {status}<br>Desc: {data.get('description', 'N/A')}"
        if status == 'modified':
            hover_text += f"<br>V1 Desc: {data.get('v1_description', 'N/A')}"
        node_texts_hover.append(hover_text)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_texts_display,
        textposition="top center",
        textfont=dict(size=9),
        hovertext=node_texts_hover,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line=dict(width=1, color='black')
        ))
    
    # Edge hover information
    edge_hover_x = []
    edge_hover_y = []
    edge_hover_texts = []

    for u, v, data in graph.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_hover_x.append((x0 + x1) / 2) # Midpoint for hover
        edge_hover_y.append((y0 + y1) / 2)
        status = data.get('change_status', 'unknown')
        details = f"<b>{data.get('label', 'RELATED_TO')}</b><br>Source: {u}<br>Target: {v}<br>Status: {status}"
        if status == 'modified':
            details += f"<br>V1 Label: {data.get('v1_relationship_label', 'N/A')}"
            details += f"<br>V1 Details: {data.get('v1_details', 'N/A')}"
            details += f"<br>V2 Details: {data.get('details', 'N/A')}" # 'details' is v2_details for modified edges
        else: # added or implicit
            details += f"<br>Details: {data.get('details', 'N/A')}"
        edge_hover_texts.append(details)

    edge_hover_trace = go.Scatter(
        x=edge_hover_x, y=edge_hover_y,
        mode='markers',
        hoverinfo='text',
        hovertext=edge_hover_texts,
        marker=dict(size=5, color='rgba(0,0,0,0)') # Invisible markers
    )

    fig = go.Figure(data=[edge_trace, node_trace, edge_hover_trace],
                    layout=go.Layout(
                        title=f'<br>{title}',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="Nodes: Green (Added), Orange (Modified), Blue (Unchanged/Referenced), Grey (Implicit). Hover for details.",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    st.plotly_chart(fig, use_container_width=True)
