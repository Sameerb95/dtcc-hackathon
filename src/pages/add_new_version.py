import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
from pathlib import Path
from typing import Optional
import networkx as nx

try:
    from upload_interface import UploadProcessor
    from create_diff_json import generate_all_diffs
    from create_diff_graph import process_all_diff_jsons, filter_isolated_nodes, merge_individual_graphs, create_graph_from_diff
    from graph_plotting import plot_networkx_graph 
except ImportError:
    try:
        from ..upload_interface import UploadProcessor
        from ..create_diff_json import generate_all_diffs
        from ..create_diff_graph import process_all_diff_jsons, filter_isolated_nodes, merge_individual_graphs, create_graph_from_diff
        from graph_plotting import plot_networkx_graph 
    except ImportError:
        st.error(
            "Critical Import Error: Could not import necessary components. "
            "Ensure 'upload_interface.py', 'create_diff_json.py', 'create_diff_graph.py', and 'utils/graph_plotting.py' are accessible."
        )
        UploadProcessor, generate_all_diffs, process_all_diff_jsons, filter_isolated_nodes, \
        merge_individual_graphs, create_graph_from_diff, plot_networkx_graph = [None] * 7


try:
    from .new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
except ImportError:
    try:
        from pages.new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
    except ImportError:
        st.error("Could not import DB functions from new_regulation.py. Regulation selection will be unavailable.")
        get_all_regulation_names_from_db = None
        init_db = None
        RESOURCE_PATH = "resources" 


def find_summaries_dir_in_version_folder(version_folder_path: Path) -> Optional[str]:
    if not version_folder_path.is_dir():
        st.warning(f"Version folder path not found or not a directory: {version_folder_path}")
        return None
    for pdf_stem_folder in version_folder_path.iterdir():
        if pdf_stem_folder.is_dir():
            potential_summary_dirs = [d for d in pdf_stem_folder.iterdir() if d.is_dir() and d.name.endswith("_summaries")]
            if potential_summary_dirs:
                summary_dir = potential_summary_dirs[0] 
                st.info(f"Using summary directory for V1 comparison: {summary_dir}")
                return str(summary_dir)
    st.warning(f"No summary directories (ending with '_summaries') found within subfolders of {version_folder_path}.")
    return None


def render_add_new_version_page():
    st.set_page_config(layout="wide")
    if init_db: init_db()

    st.sidebar.page_link(page="pages/home.py", label="Home")
    st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (V1)")
    st.sidebar.page_link(page="pages/add_new_version.py", label="Add New Version (V2) & Diff")
    st.sidebar.page_link(page="pages/view_graphs.py", label="View Difference Graphs")

    add_vertical_space(1)
    st.title("Add New Version (V2) and Generate Differences")

    # Check if all necessary functions are loaded
    required_funcs = [UploadProcessor, generate_all_diffs, process_all_diff_jsons, 
                      filter_isolated_nodes, merge_individual_graphs, 
                      create_graph_from_diff, plot_networkx_graph, get_all_regulation_names_from_db]
    if not all(required_funcs):
        st.error("One or more core components failed to load. Page functionality will be limited.")
        # Optionally, return early if critical components like DB access are missing
        if not get_all_regulation_names_from_db:
            return

    selected_regulation = None
    if get_all_regulation_names_from_db:
        regulation_names = get_all_regulation_names_from_db()
        if regulation_names:
            selected_regulation = st.selectbox(
                "Select Regulation for V2 Comparison", options=[""] + regulation_names, index=0,
                key="main_page_reg_select_v2_compare"
            )
        else:
            st.info("No regulations found. Please add an initial regulation (V1) first.")
            return
    else: # This case should be caught by the check above, but as a fallback:
        st.warning("Regulation selection unavailable (DB function missing).")
        return

    if not selected_regulation:
        st.info("Please select a regulation above to proceed.")
        return

    session_key_uploaded_file = f"v2_uploaded_file_{selected_regulation}"
    if session_key_uploaded_file not in st.session_state:
        st.session_state[session_key_uploaded_file] = None

    st.subheader(f"Upload V2 PDF for '{selected_regulation}'")
    uploaded_file_v2 = st.file_uploader(
        "Upload PDF for Version 2 Document", type=["pdf"], 
        key=f"v2_pdf_uploader_new_version_page_{selected_regulation}"
    )

    if uploaded_file_v2:
        st.session_state[session_key_uploaded_file] = uploaded_file_v2
        st.caption(f"Uploaded V2: {uploaded_file_v2.name}")

    if st.session_state.get(session_key_uploaded_file) and selected_regulation:
        if st.button(f"Process V2 & Generate Diffs for '{selected_regulation}'", 
                     key=f"process_v2_diff_new_version_page_{selected_regulation}"):
            
            # Re-check critical components before processing
            if not all([UploadProcessor, generate_all_diffs, process_all_diff_jsons, 
                        filter_isolated_nodes, merge_individual_graphs, plot_networkx_graph]):
                st.error("Core processing or plotting components are not available. Cannot proceed.")
                return

            v2_file_obj = st.session_state[session_key_uploaded_file]
            v2_file_stem = Path(v2_file_obj.name).stem
            v2_processor_base_path = Path(RESOURCE_PATH) / selected_regulation / "new"
            v2_processor_instance_name = v2_file_stem

            with st.spinner(f"Processing V2 document '{v2_file_obj.name}'..."):
                processor_v2 = UploadProcessor(
                    st_object=st, uploaded_file_obj=v2_file_obj,
                    regulation_name=v2_processor_instance_name,
                    resource_path=str(v2_processor_base_path)
                )
                v2_processed_ok = processor_v2.process()

            if v2_processed_ok:
                st.success(f"V2 document '{v2_file_obj.name}' processed successfully.")
                v1_version_folder_path = Path(RESOURCE_PATH) / selected_regulation / "old"
                path_for_v1_summaries = find_summaries_dir_in_version_folder(v1_version_folder_path)
                path_for_v2_summaries = v2_processor_base_path / v2_processor_instance_name / f"{v2_file_stem}_summaries"

                if path_for_v1_summaries and path_for_v2_summaries.is_dir():
                    st.info("Proceeding to generate differences...")
                    with st.expander("Difference Generation Log", expanded=True):
                        diffs_generated_successfully = generate_all_diffs(
                            selected_regulation=selected_regulation,
                            base_summary_path_v1_arg=str(path_for_v1_summaries),
                            base_summary_path_v2_arg=str(path_for_v2_summaries),
                            use_streamlit_feedback=True
                        )
                    
                    if diffs_generated_successfully:
                        st.info("Difference generation step completed.")
                        v2_summary_folder_name_for_diff_json = path_for_v2_summaries.name 
                        actual_diff_json_folder = Path(RESOURCE_PATH) / selected_regulation / "graph_diff_json" / v2_summary_folder_name_for_diff_json

                        if actual_diff_json_folder.is_dir() and list(actual_diff_json_folder.glob('*.json')):
                            with st.spinner("Processing diff JSONs and building graphs..."):
                                # process_all_diff_jsons returns List[Tuple[str, nx.DiGraph]]
                                list_of_graphs_with_names = process_all_diff_jsons(str(actual_diff_json_folder))
                                
                                if list_of_graphs_with_names:
                                    st.subheader("Individual Chunk Difference Graphs")
                                    graphs_for_merging = []
                                    for filename, chunk_graph in list_of_graphs_with_names:
                                        if chunk_graph and chunk_graph.number_of_nodes() > 0:
                                            graphs_for_merging.append(chunk_graph)
                                            with st.expander(f"Graph for {filename.replace('_diff.json', '')}", expanded=False):
                                                plot_networkx_graph(chunk_graph, title=f"Chunk Diff: {filename.replace('_diff.json', '')}")
                                        else:
                                            st.caption(f"Chunk {filename.replace('_diff.json', '')} resulted in an empty or non-significant graph.")
                                    
                                    st.subheader("Merged Difference Graph")
                                    if graphs_for_merging:
                                        merged_graph_obj = merge_individual_graphs(graphs_for_merging)
                                        st.caption(f"Merged graph from {len(graphs_for_merging)} chunks: {merged_graph_obj.number_of_nodes()} nodes, {merged_graph_obj.number_of_edges()} edges (before filtering).")
                                        filtered_merged_graph = filter_isolated_nodes(merged_graph_obj)
                                        st.caption(f"Final merged graph: {filtered_merged_graph.number_of_nodes()} nodes, {filtered_merged_graph.number_of_edges()} edges (after filtering).")
                                        
                                        if filtered_merged_graph.number_of_nodes() > 0:
                                            plot_networkx_graph(filtered_merged_graph, title=f"Overall Difference Graph for '{selected_regulation}' (V2: {v2_file_obj.name})")
                                        else:
                                            st.info("The final merged graph is empty after filtering.")
                                    else:
                                        st.warning("No individual chunk graphs were suitable for merging.")
                                else:
                                    st.warning("No graphs (even empty ones) were created from the diff JSON files. Cannot plot.")
                        else:
                            st.error(f"Diff JSON folder not found or empty at '{actual_diff_json_folder}'. Cannot generate graph.")
                    else:
                        st.warning("Difference generation reported issues or did not complete. Graph plotting skipped.")
                else: # Issues with V1 or V2 summary paths
                    if not path_for_v1_summaries: st.error(f"Could not find V1 summary path in '{v1_version_folder_path}'.")
                    if not path_for_v2_summaries.is_dir(): st.error(f"V2 summary path not found: {path_for_v2_summaries}.")
            else: # V2 processing failed
                st.error(f"Failed to process V2 document '{v2_file_obj.name}'.")

            st.session_state[session_key_uploaded_file] = None # Clear uploaded file from session
            st.rerun() # Rerun to reset UI state

if __name__ == "__main__":
    render_add_new_version_page()
