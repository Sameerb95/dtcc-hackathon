import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
from pathlib import Path
import networkx as nx
from typing import List, Optional, Dict # Added Dict

try:
    # Import create_graph_from_diff if needed for single file, merge_individual_graphs for merging
    from create_diff_graph import process_all_diff_jsons, filter_isolated_nodes, create_graph_from_diff, merge_individual_graphs
    from pages.new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
    from graph_plotting import plot_networkx_graph
except ImportError:
    try:
        from ..create_diff_graph import process_all_diff_jsons, filter_isolated_nodes, create_graph_from_diff, merge_individual_graphs
        from ..pages.new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
        from graph_plotting import plot_networkx_graph
    except ImportError:
        st.error(
            "Critical Import Error: Could not import necessary components for graph viewing. "
            "Ensure 'create_diff_graph.py', 'new_regulation.py', and 'utils/graph_plotting.py' are accessible."
        )
        # Initialize all to None
        process_all_diff_jsons, filter_isolated_nodes, create_graph_from_diff, merge_individual_graphs, \
        get_all_regulation_names_from_db, init_db, plot_networkx_graph = [None] * 7
        RESOURCE_PATH = "resources"


def get_available_diff_sets(selected_regulation: str) -> List[str]:
    if not selected_regulation: return []
    base_diff_path = Path(RESOURCE_PATH) / selected_regulation / "graph_diff_json"
    if not base_diff_path.is_dir(): return []
    return sorted([d.name for d in base_diff_path.iterdir() if d.is_dir() and list(d.glob('*.json'))])


def render_view_graphs_page():
    if init_db: init_db()

    st.sidebar.page_link(page="pages/home.py", label="Home")
    st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (V1)")

    add_vertical_space(1)
    st.title("View Difference Graphs")

    required_funcs = [process_all_diff_jsons, filter_isolated_nodes, merge_individual_graphs,
                      get_all_regulation_names_from_db, plot_networkx_graph, create_graph_from_diff]
    if not all(required_funcs):
        st.error("Graph viewing functionality is impaired due to missing components.")
        if not get_all_regulation_names_from_db: return # Critical for selection

    # 1. Select Regulation
    regulation_names = get_all_regulation_names_from_db() if get_all_regulation_names_from_db else []
    if not regulation_names:
        st.info("No regulations found. Please add regulations and generate differences first.")
        return

    selected_regulation = st.selectbox(
        "Select Regulation", options=[""] + regulation_names, index=0, key="view_graphs_reg_select"
    )
    if not selected_regulation:
        st.info("Please select a regulation.")
        return

    # 2. Select Diff Set
    available_diffs = get_available_diff_sets(selected_regulation)
    if not available_diffs:
        st.info(f"No difference graph sets found for '{selected_regulation}'.")
        return

    selected_diff_set_name = st.selectbox(
        f"Select Difference Set for '{selected_regulation}'", options=[""] + available_diffs, index=0,
        key=f"view_graphs_diff_set_select_{selected_regulation}",
        help="Corresponds to the V2 document version."
    )
    if not selected_diff_set_name:
        st.info("Please select a difference set.")
        return

    # 3. Load graphs for the selected diff set and offer chunk/merged view
    actual_diff_json_folder = Path(RESOURCE_PATH) / selected_regulation / "graph_diff_json" / selected_diff_set_name
    
    # Use session state to cache loaded graphs for a selected diff_set_name
    session_key_graphs = f"graphs_cache_{selected_regulation}_{selected_diff_set_name}"

    if actual_diff_json_folder.is_dir() and list(actual_diff_json_folder.glob('*.json')):
        if session_key_graphs not in st.session_state or st.session_state[session_key_graphs]['folder'] != str(actual_diff_json_folder) :
            with st.spinner(f"Loading graphs for '{selected_diff_set_name}'..."):
                # process_all_diff_jsons returns List[Tuple[str, nx.DiGraph]]
                list_of_graphs_with_names = process_all_diff_jsons(str(actual_diff_json_folder))
                st.session_state[session_key_graphs] = {
                    'folder': str(actual_diff_json_folder),
                    'data': list_of_graphs_with_names
                }
        
        cached_graphs_with_names = st.session_state[session_key_graphs]['data']

        if not cached_graphs_with_names:
            st.warning(f"No graph data could be loaded from '{actual_diff_json_folder}'.")
            return

        chunk_graph_options: Dict[str, Optional[nx.DiGraph]] = {"Merged Graph": None} # Placeholder for merged
        valid_chunk_graphs_for_merging: List[nx.DiGraph] = []

        for filename, graph_obj in cached_graphs_with_names:
            display_name = filename.replace("_diff.json", "").replace("chunk_", "Chunk ")
            chunk_graph_options[display_name] = graph_obj
            if graph_obj and graph_obj.number_of_nodes() > 0:
                 valid_chunk_graphs_for_merging.append(graph_obj)
        
        selected_graph_display_name = st.selectbox(
            "Select Graph to View",
            options=list(chunk_graph_options.keys()),
            index=0, # Default to "Merged Graph"
            key=f"view_graphs_select_chunk_{selected_regulation}_{selected_diff_set_name}"
        )

        graph_to_plot = None
        graph_title = ""

        if selected_graph_display_name == "Merged Graph":
            if valid_chunk_graphs_for_merging:
                with st.spinner("Generating merged graph..."):
                    merged_graph_obj = merge_individual_graphs(valid_chunk_graphs_for_merging)
                    st.caption(f"Merged from {len(valid_chunk_graphs_for_merging)} chunks: {merged_graph_obj.number_of_nodes()}N, {merged_graph_obj.number_of_edges()}E (pre-filter).")
                    graph_to_plot = filter_isolated_nodes(merged_graph_obj)
                    graph_title = f"Overall Difference: {selected_regulation} ({selected_diff_set_name.replace('_summaries', '')})"
                    st.caption(f"Final merged: {graph_to_plot.number_of_nodes()}N, {graph_to_plot.number_of_edges()}E (post-filter).")
            else:
                st.info("No valid chunk graphs available to merge for this set.")
        
        elif selected_graph_display_name in chunk_graph_options:
            graph_to_plot = chunk_graph_options[selected_graph_display_name]
            # No need to filter isolated nodes for a single chunk's raw graph unless desired
            # graph_to_plot = filter_isolated_nodes(graph_to_plot) # Optional
            graph_title = f"Chunk Difference: {selected_graph_display_name} ({selected_regulation} - {selected_diff_set_name.replace('_summaries', '')})"
        
        if graph_to_plot is not None:
            if graph_to_plot.number_of_nodes() > 0:
                plot_networkx_graph(graph_to_plot, title=graph_title)
            else:
                st.info(f"The selected graph ('{selected_graph_display_name}') is empty or has no nodes after processing.")
        elif selected_graph_display_name == "Merged Graph" and not valid_chunk_graphs_for_merging:
            pass # Message already shown
        else:
            st.info(f"No graph data found for '{selected_graph_display_name}'.")
            
    else:
        st.error(f"Diff JSON folder not found or empty at '{actual_diff_json_folder}'.")
        if session_key_graphs in st.session_state: # Clear cache if folder disappears
            del st.session_state[session_key_graphs]


if __name__ == "__main__":
    render_view_graphs_page()
