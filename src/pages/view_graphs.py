import json
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from pathlib import Path # Added for robust path handling

# Ensure this function is defined or imported if it's used elsewhere,
# for now, it's self-contained for plotting the merged graph.
def create_merged_graph_data(items_data):
    """
    Prepares node and edge data for a merged V1 and V2 view with enhanced styling.
    """
    nodes_dict = {}
    edges_list = []
    G = nx.DiGraph()

    source_node_modification_flags = {}
    for item in items_data:
        source_node_info = item['source_node']
        relationship_info = item['relationship']
        is_modified = relationship_info.get('change_status') == 'modified'
        s_id = source_node_info['id']
        if is_modified:
            source_node_modification_flags[s_id] = True

    for item in items_data:
        source_node_info = item['source_node']
        target_node_info = item['target_node']
        relationship_info = item['relationship']
        change_description = item.get('change_description', '')
        is_relationship_modified = relationship_info.get('change_status') == 'modified'

        s_id = source_node_info['id']
        s_label = source_node_info['label']
        s_desc_v2 = source_node_info['description_v2']
        s_color = 'orange' if source_node_modification_flags.get(s_id, False) else 'skyblue'
        s_size = 22

        if s_id not in G.nodes():
            G.add_node(s_id)
        nodes_dict[s_id] = {'label': s_label, 'description': s_desc_v2, 'color': s_color, 'size': s_size}

        # Old V1 value node
        old_value_node_id = f"{target_node_info['id']}_content_v1_merged"
        old_value_node_label = f"{target_node_info['label']} (Old Value)"
        old_value_node_desc = target_node_info['description_v1']
        old_value_node_color = 'lightgrey'
        old_value_node_size = 14

        if old_value_node_id not in G.nodes():
            G.add_node(old_value_node_id)
        nodes_dict[old_value_node_id] = {
            'label': old_value_node_label,
            'description': old_value_node_desc,
            'color': old_value_node_color,
            'size': old_value_node_size
        }
        
        G.add_edge(s_id, old_value_node_id)
        edges_list.append({
            'source': s_id,
            'target': old_value_node_id,
            'label': relationship_info['label_v1'],
            'hovertext': f"Old: {s_label} {relationship_info['label_v1'].lower()} '{target_node_info['label']}'",
            'color': 'dimgrey',
            'style': 'dash',
            'width': 1.2
        })

        # New V2 target node
        t_id = target_node_info['id']
        t_label = target_node_info['label']
        t_desc_v2 = target_node_info['description_v2']
        t_color = 'lightcoral' if is_relationship_modified else 'lightgreen'
        t_size = 18

        if t_id not in G.nodes():
            G.add_node(t_id)
        nodes_dict[t_id] = {'label': t_label, 'description': t_desc_v2, 'color': t_color, 'size': t_size}
        
        G.add_edge(s_id, t_id)
        edge_v2_color = 'red' if is_relationship_modified else 'darkgreen'
        edge_v2_width = 2.0 if is_relationship_modified else 1.5
        edges_list.append({
            'source': s_id,
            'target': t_id,
            'label': relationship_info['label_v2'],
            'hovertext': change_description if change_description else f"New: {s_label} {relationship_info['label_v2'].lower()} '{t_label}'",
            'color': edge_v2_color,
            'style': 'solid',
            'width': edge_v2_width
        })

    pos = {}
    if G.nodes():
        pos = nx.spring_layout(G, seed=42, k=1.5, iterations=100) # Adjusted layout params

    node_x, node_y, node_text, node_hovertext, node_colors, node_sizes_list = [], [], [], [], [], []
    for node_id, attr in nodes_dict.items():
        if node_id in pos:
            node_x.append(pos[node_id][0])
            node_y.append(pos[node_id][1])
            node_text.append(attr['label'])
            node_hovertext.append(f"<b>{attr['label']}</b><br>{attr['description']}")
            node_colors.append(attr['color'])
            node_sizes_list.append(attr['size'])

    annotations_list = []
    edge_traces = []

    # Separate traces for different edge styles for more control if needed, or combine
    # For simplicity, we'll create segments for solid and dashed lines with varying properties
    
    # This part can be complex if we want truly separate traces for Plotly legend.
    # For now, edge styling is handled by properties in edges_list and drawn as segments.
    # The custom legend will explain these.

    for edge in edges_list:
        if edge['source'] in pos and edge['target'] in pos:
            x0, y0 = pos[edge['source']]
            x1, y1 = pos[edge['target']]
            
            edge_trace = go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None], mode='lines',
                line=dict(width=edge['width'], color=edge['color'], dash=edge.get('style', 'solid')),
                hoverinfo='none' # Edge hover handled by annotations for now
            )
            edge_traces.append(edge_trace)
            
            annotations_list.append(
                dict(
                    x=(x0+x1)/2, y=(y0+y1)/2,
                    text=edge['label'], showarrow=False,
                    font=dict(size=9, color=edge['color']),
                    hovertext=edge['hovertext'],
                    bgcolor="rgba(255,255,255,0.75)"
                )
            )
    
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', text=node_text,
        hovertext=node_hovertext, hoverinfo='text',
        marker=dict(size=node_sizes_list, color=node_colors, line=dict(width=1, color='black')),
        textposition="top center", textfont=dict(size=10)
    )
    
    return node_trace, edge_traces, annotations_list


def display_graph_on_streamlit(json_string_data):
    """
    Parses JSON string, creates graph data, and plots the Merged graph in Streamlit.
    """
    try:
        diff_data = json.loads(json_string_data)
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        st.text_area("Problematic JSON data", json_string_data[:1000] + "...", height=200)
        return

    if not isinstance(diff_data, list):
        st.error("Error: JSON data should be a list of objects.")
        st.json(diff_data)
        return
    
    if not diff_data:
        st.info("No difference data found in the JSON. Nothing to plot.")
        return

    node_trace_merged, edge_traces_merged, annotations_merged = create_merged_graph_data(diff_data)

    fig = make_subplots(rows=1, cols=1)

    if node_trace_merged.x:
        for trace in edge_traces_merged: # Add all individual edge traces
            fig.add_trace(trace, row=1, col=1)
        fig.add_trace(node_trace_merged, row=1, col=1)
    else:
        st.info("Graph data prepared, but no nodes to display for the merged view.")
            
    fig_annotations = []
    for ann in annotations_merged:
        ann['xref'] = 'x1'
        ann['yref'] = 'y1'
        fig_annotations.append(ann)
            
    fig.update_layout(
        height=800, # Increased height for legend
        showlegend=False, # Using custom legend via annotations
        annotations=fig_annotations,
        hovermode='closest',
        margin=dict(l=50, r=50, t=120, b=50) # Adjusted top margin for legend
    )
    
    fig.update_xaxes(showticklabels=False, zeroline=False, showgrid=False, mirror=True, linecolor='lightgrey', linewidth=1, row=1, col=1)
    fig.update_yaxes(showticklabels=False, zeroline=False, showgrid=False, mirror=True, linecolor='lightgrey', linewidth=1, row=1, col=1)

    # --- Custom Legend ---
    legend_items_data = [
        {"color": "skyblue", "label": "Source Node (Unchanged Relationships)", "type": "node"},
        {"color": "orange", "label": "Source Node (Modified Relationships)", "type": "node"},
        {"color": "lightgreen", "label": "Target Node (New V2 Content - Added)", "type": "node"},
        {"color": "lightcoral", "label": "Target Node (New V2 Content - Modified)", "type": "node"},
        {"color": "lightgrey", "label": "Old V1 Content Node", "type": "node"},
        {"color": "darkgreen", "label": "Edge: New V2 Relationship", "type": "edge", "style": "solid", "width": 1.5},
        {"color": "red", "label": "Edge: Modified V2 Relationship", "type": "edge", "style": "solid", "width": 2.0},
        {"color": "dimgrey", "label": "Edge: Old V1 Relationship", "type": "edge", "style": "dash", "width": 1.2},
    ]

    legend_annotations_custom = []
    legend_shapes_custom = []
    
    # Position legend at the top, outside the plot area
    y_start_legend = 1.15  # Y position in 'paper' coordinates (above the plot)
    x_item_start = 0.01
    y_step_legend = 0.035
    current_x_offset = x_item_start

    for i, item in enumerate(legend_items_data):
        y_pos_legend = y_start_legend - ( (i // 2) * y_step_legend) # Two items per row for legend
        
        if i % 2 == 0: # First item in a row
            current_x_offset = x_item_start
        else: # Second item in a row
            current_x_offset = x_item_start + 0.4 # Adjust this for spacing between items in a row

        shape_x0 = current_x_offset
        text_x_offset = current_x_offset + 0.03

        if item["type"] == "node":
            legend_shapes_custom.append(
                dict(type="circle", xref="paper", yref="paper",
                     x0=shape_x0, y0=y_pos_legend - 0.008,
                     x1=shape_x0 + 0.02, y1=y_pos_legend + 0.008,
                     fillcolor=item["color"], line_color=item["color"], opacity=0.8)
            )
        elif item["type"] == "edge":
            legend_shapes_custom.append(
                dict(type="line", xref="paper", yref="paper",
                     x0=shape_x0, y0=y_pos_legend,
                     x1=shape_x0 + 0.02, y1=y_pos_legend,
                     line=dict(color=item["color"], width=item["width"], dash=item.get("style", "solid")))
            )

        legend_annotations_custom.append(
            dict(xref="paper", yref="paper", x=text_x_offset, y=y_pos_legend,
                 text=item["label"], showarrow=False, font=dict(size=10),
                 align="left", xanchor="left", yanchor="middle")
        )

    fig.update_layout(
        annotations=fig.layout.annotations + tuple(legend_annotations_custom),
        shapes=(fig.layout.shapes if fig.layout.shapes else ()) + tuple(legend_shapes_custom)
    )
    # --- End Custom Legend ---

    st.plotly_chart(fig, use_container_width=True)

def view_graphs_page():
    st.set_page_config(layout="wide", page_title="View Difference Graphs")
    st.title("📊 View Document Difference Graphs")

    st.sidebar.page_link("pages/home.py", label="Home")
    st.sidebar.page_link("pages/new_regulation.py", label="Add New Regulation (V1)")
    st.sidebar.page_link("pages/add_new_version.py", label="Add New Version (V2) & Diff")
    st.sidebar.page_link("pages/view_graphs.py", label="View Difference Graphs")
    st.sidebar.page_link("pages/changes_review.py", label="Review Changes & KOP")


    query_params = st.query_params
    initial_graph_path_str = query_params.get("initial_graph_path")
    if isinstance(initial_graph_path_str, list): # query_params can return list
        initial_graph_path_str = initial_graph_path_str[0]


    uploaded_file = st.file_uploader("Upload a graph JSON file (optional, overrides URL param)", type=["json"])
    graph_data_to_plot = None

    if uploaded_file is not None:
        st.info(f"Using uploaded file: {uploaded_file.name}")
        graph_data_to_plot = uploaded_file.read().decode()
    elif initial_graph_path_str:
        initial_graph_path = Path(initial_graph_path_str)
        if initial_graph_path.is_file():
            st.info(f"Using graph data from URL parameter: {initial_graph_path.name}")
            try:
                with open(initial_graph_path, 'r', encoding='utf-8') as f:
                    graph_data_to_plot = f.read()
            except Exception as e:
                st.error(f"Error reading graph file '{initial_graph_path}': {e}")
        else:
            st.warning(f"Graph file specified in URL not found: {initial_graph_path}")
    
    if graph_data_to_plot:
        display_graph_on_streamlit(graph_data_to_plot)
    else:
        st.info("No graph data loaded. Upload a file or provide a valid path via URL parameter (e.g., `?initial_graph_path=path/to/your/graph.json`).")

    st.markdown("---")

# In view_graphs.py, inside view_graphs_page()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Proceed to Report Creation", key="proceed_report_creation"):
            if graph_data_to_plot:
                st.session_state['graph_data_for_review'] = graph_data_to_plot
                # Ensure 'selected_regulation' is in session state.
                # This might need to be derived from initial_graph_path_str if not already set
                if 'selected_regulation' not in st.session_state and initial_graph_path_str:
                    # Attempt to derive regulation name from path, e.g., resources/REG_NAME/document_diff_json/...
                    try:
                        path_parts = Path(initial_graph_path_str).parts
                        if "resources" in path_parts:
                            reg_index = path_parts.index("resources") + 1
                            if reg_index < len(path_parts):
                                st.session_state['selected_regulation'] = path_parts[reg_index]
                                st.info(f"Derived selected regulation: {st.session_state['selected_regulation']}")
                    except ValueError:
                        st.warning("Could not derive selected regulation from path for report creation.")

                st.session_state['graph_file_path_for_review'] = str(initial_graph_path_str) if initial_graph_path_str else "uploaded_data"
            else:
                st.warning("No graph data loaded to proceed with.")
                return # Don't switch page if no data

            if 'selected_regulation' in st.session_state:
                st.switch_page("pages/changes_review.py")
            else:
                st.error("Selected regulation context is missing. Cannot proceed to report creation.")

    with col2:
        if st.button("Regenerate Graphs", key="regenerate_graphs"):
            st.info("Regenerating graphs...")
            st.rerun()
    
    with col3:
        if st.button("Home", key="go_home_graphs"):
            st.switch_page("pages/home.py")

if __name__ == '__main__':
    # For local testing, ensure a default path can be loaded if no query param
    if "initial_graph_path" not in st.session_state: # Check if it's already set by rerun or navigation
        query_params = st.query_params
        initial_graph_path_str = query_params.get("initial_graph_path")
        if isinstance(initial_graph_path_str, list):
            initial_graph_path_str = initial_graph_path_str[0]

        if not initial_graph_path_str:
            # Provide a default path for local testing if needed
            # IMPORTANT: Replace this with an actual path to a valid diff JSON on your system for testing
            default_json_path_str = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/src/resources/AWPR2/document_diff_json/AWPR Version 2_vs_AWPR Version 1_diff.json"
            default_json_path = Path(default_json_path_str)
            if default_json_path.exists():
                # Simulate setting it as a query param for the first run
                st.query_params["initial_graph_path"] = str(default_json_path)
                print(f"INFO (local test): Using default graph path: {default_json_path}")
            else:
                print(f"WARNING (local test): Default test JSON not found at {default_json_path}. Graph will not load unless uploaded or passed via URL.")
    
    view_graphs_page()
