# import streamlit as st
# from streamlit_extras.add_vertical_space import add_vertical_space
# import os
# from pathlib import Path
# from typing import Optional
# import networkx as nx

# from upload_interface import UploadProcessor
# from get_difference_prompt import get_difference_prompt
# from create_diff_graph import process_all_diff_jsons, filter_isolated_nodes, merge_individual_graphs, create_graph_from_diff
# from graph_plotting import plot_networkx_graph 
# from llm_call import VertexAILangchainLLM


# try:
#     from .new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
# except ImportError:
#     try:
#         from pages.new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
#     except ImportError:
#         st.error("Could not import DB functions from new_regulation.py. Regulation selection will be unavailable.")
#         get_all_regulation_names_from_db = None
#         init_db = None
#         RESOURCE_PATH = "resources" 


# def find_summaries_dir_in_version_folder(version_folder_path: Path) -> Optional[str]:
#     if not version_folder_path.is_dir():
#         st.warning(f"Version folder path not found or not a directory: {version_folder_path}")
#         return None
#     for pdf_stem_folder in version_folder_path.iterdir():
#         if pdf_stem_folder.is_dir():
#             potential_summary_dirs = [d for d in pdf_stem_folder.iterdir() if d.is_dir() and d.name.endswith("_summaries")]
#             if potential_summary_dirs:
#                 summary_dir = potential_summary_dirs[0] 
#                 st.info(f"Using summary directory for V1 comparison: {summary_dir}")
#                 return str(summary_dir)
#     st.warning(f"No summary directories (ending with '_summaries') found within subfolders of {version_folder_path}.")
#     return None


# def render_add_new_version_page():
#     st.set_page_config(layout="wide")
#     if init_db: init_db()

#     st.sidebar.page_link(page="pages/home.py", label="Home")
#     st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (V1)")
#     st.sidebar.page_link(page="pages/add_new_version.py", label="Add New Version (V2) & Diff")
#     st.sidebar.page_link(page="pages/view_graphs.py", label="View Difference Graphs")

#     add_vertical_space(1)
#     st.title("Add New Version (V2) and Generate Differences")

#     # Check if all necessary functions are loaded
#     required_funcs = [UploadProcessor, generate_all_diffs, process_all_diff_jsons, 
#                       filter_isolated_nodes, merge_individual_graphs, 
#                       create_graph_from_diff, plot_networkx_graph, get_all_regulation_names_from_db]
#     if not all(required_funcs):
#         st.error("One or more core components failed to load. Page functionality will be limited.")
#         # Optionally, return early if critical components like DB access are missing
#         if not get_all_regulation_names_from_db:
#             return

#     selected_regulation = None
#     if get_all_regulation_names_from_db:
#         regulation_names = get_all_regulation_names_from_db()
#         if regulation_names:
#             selected_regulation = st.selectbox(
#                 "Select Regulation for V2 Comparison", options=[""] + regulation_names, index=0,
#                 key="main_page_reg_select_v2_compare"
#             )
#         else:
#             st.info("No regulations found. Please add an initial regulation (V1) first.")
#             return
#     else: # This case should be caught by the check above, but as a fallback:
#         st.warning("Regulation selection unavailable (DB function missing).")
#         return

#     if not selected_regulation:
#         st.info("Please select a regulation above to proceed.")
#         return

#     session_key_uploaded_file = f"v2_uploaded_file_{selected_regulation}"
#     if session_key_uploaded_file not in st.session_state:
#         st.session_state[session_key_uploaded_file] = None

#     st.subheader(f"Upload V2 PDF for '{selected_regulation}'")
#     uploaded_file_v2 = st.file_uploader(
#         "Upload PDF for Version 2 Document", type=["pdf"], 
#         key=f"v2_pdf_uploader_new_version_page_{selected_regulation}"
#     )

#     if uploaded_file_v2:
#         st.session_state[session_key_uploaded_file] = uploaded_file_v2
#         st.caption(f"Uploaded V2: {uploaded_file_v2.name}")

#     if st.session_state.get(session_key_uploaded_file) and selected_regulation:
#         if st.button(f"Process V2 & Generate Diffs for '{selected_regulation}'", 
#                      key=f"process_v2_diff_new_version_page_{selected_regulation}"):
            
#             # # Re-check critical components before processing
#             # if not all([UploadProcessor, generate_all_diffs, process_all_diff_jsons, 
#             #             filter_isolated_nodes, merge_individual_graphs, plot_networkx_graph]):
#             #     st.error("Core processing or plotting components are not available. Cannot proceed.")
#             #     return

#             v2_file_obj = st.session_state[session_key_uploaded_file]
#             v2_file_stem = Path(v2_file_obj.name).stem
#             v2_processor_base_path = Path(RESOURCE_PATH) / selected_regulation / "new"
#             v2_processor_instance_name = v2_file_stem

#             with st.spinner(f"Processing V2 document '{v2_file_obj.name}'..."):
#                 processor_v2 = UploadProcessor(
#                     st_object=st, uploaded_file_obj=v2_file_obj,
#                     regulation_name=v2_processor_instance_name,
#                     resource_path=str(v2_processor_base_path)
#                 )
#                 v2_processed_ok = processor_v2.process()

#             if v2_processed_ok:
#                 st.success(f"V2 document '{v2_file_obj.name}' processed successfully.")
#                 v1_version_folder_path = Path(RESOURCE_PATH) / selected_regulation / "old"
#                 path_for_v1_summaries = find_summaries_dir_in_version_folder(v1_version_folder_path)
#                 path_for_v2_summaries = v2_processor_base_path / v2_processor_instance_name / f"{v2_file_stem}_summaries"

#                 if path_for_v1_summaries and path_for_v2_summaries.is_dir():
#                     st.info("Proceeding to generate differences...")
#                     with st.expander("Difference Generation Log", expanded=True):
#                         diffs_generated_successfully = generate_all_diffs(
#                             selected_regulation=selected_regulation,
#                             base_summary_path_v1_arg=str(path_for_v1_summaries),
#                             base_summary_path_v2_arg=str(path_for_v2_summaries),
#                             use_streamlit_feedback=True
#                         )
                    
#                     if diffs_generated_successfully:
#                         st.info("Difference generation step completed.")
#                         v2_summary_folder_name_for_diff_json = path_for_v2_summaries.name 
#                         actual_diff_json_folder = Path(RESOURCE_PATH) / selected_regulation / "graph_diff_json" / v2_summary_folder_name_for_diff_json

#                         if actual_diff_json_folder.is_dir() and list(actual_diff_json_folder.glob('*.json')):
#                             with st.spinner("Processing diff JSONs and building graphs..."):
#                                 # process_all_diff_jsons returns List[Tuple[str, nx.DiGraph]]
#                                 list_of_graphs_with_names = process_all_diff_jsons(str(actual_diff_json_folder))
                                
#                                 if list_of_graphs_with_names:
#                                     st.subheader("Individual Chunk Difference Graphs")
#                                     graphs_for_merging = []
#                                     for filename, chunk_graph in list_of_graphs_with_names:
#                                         if chunk_graph and chunk_graph.number_of_nodes() > 0:
#                                             graphs_for_merging.append(chunk_graph)
#                                             with st.expander(f"Graph for {filename.replace('_diff.json', '')}", expanded=False):
#                                                 plot_networkx_graph(chunk_graph, title=f"Chunk Diff: {filename.replace('_diff.json', '')}")
#                                         else:
#                                             st.caption(f"Chunk {filename.replace('_diff.json', '')} resulted in an empty or non-significant graph.")
                                    
#                                     st.subheader("Merged Difference Graph")
#                                     if graphs_for_merging:
#                                         merged_graph_obj = merge_individual_graphs(graphs_for_merging)
#                                         st.caption(f"Merged graph from {len(graphs_for_merging)} chunks: {merged_graph_obj.number_of_nodes()} nodes, {merged_graph_obj.number_of_edges()} edges (before filtering).")
#                                         filtered_merged_graph = filter_isolated_nodes(merged_graph_obj)
#                                         st.caption(f"Final merged graph: {filtered_merged_graph.number_of_nodes()} nodes, {filtered_merged_graph.number_of_edges()} edges (after filtering).")
                                        
#                                         if filtered_merged_graph.number_of_nodes() > 0:
#                                             plot_networkx_graph(filtered_merged_graph, title=f"Overall Difference Graph for '{selected_regulation}' (V2: {v2_file_obj.name})")
#                                         else:
#                                             st.info("The final merged graph is empty after filtering.")
#                                     else:
#                                         st.warning("No individual chunk graphs were suitable for merging.")
#                                 else:
#                                     st.warning("No graphs (even empty ones) were created from the diff JSON files. Cannot plot.")
#                         else:
#                             st.error(f"Diff JSON folder not found or empty at '{actual_diff_json_folder}'. Cannot generate graph.")
#                     else:
#                         st.warning("Difference generation reported issues or did not complete. Graph plotting skipped.")
#                 else: # Issues with V1 or V2 summary paths
#                     if not path_for_v1_summaries: st.error(f"Could not find V1 summary path in '{v1_version_folder_path}'.")
#                     if not path_for_v2_summaries.is_dir(): st.error(f"V2 summary path not found: {path_for_v2_summaries}.")
#             else: # V2 processing failed
#                 st.error(f"Failed to process V2 document '{v2_file_obj.name}'.")

#             st.session_state[session_key_uploaded_file] = None # Clear uploaded file from session
#             st.rerun() # Rerun to reset UI state

# if __name__ == "__main__":
#     render_add_new_version_page()

##------------------------------------------------------------


# import streamlit as st
# from streamlit_extras.add_vertical_space import add_vertical_space
# import os
# from pathlib import Path
# from typing import Optional, List as TypingList

# import fitz  # PyMuPDF
# from difflib import SequenceMatcher, Differ
# from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
# import networkx as nx # Keep for type hints if any remain, though direct use is commented out

# from upload_interface import UploadProcessor
# from get_difference_prompt import get_difference_prompt
# # Graph processing imports - will be largely unused with the new diff JSON format for now
# from create_diff_graph import process_all_diff_jsons, filter_isolated_nodes, merge_individual_graphs, create_graph_from_diff
# from graph_plotting import plot_networkx_graph 
# from llm_call import VertexAILangchainLLM
# import json # For saving the new diff JSON

# try:
#     from .new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
# except ImportError:
#     try:
#         from pages.new_regulation import get_all_regulation_names_from_db, init_db, RESOURCE_PATH
#     except ImportError:
#         st.error("Could not import DB functions from new_regulation.py. Regulation selection will be unavailable.")
#         get_all_regulation_names_from_db = None
#         init_db = None
#         RESOURCE_PATH = "resources" 

# # --- Helper functions for new PDF diffing mechanism ---
# def extract_text_from_pdf_pages_for_diff(pdf_path: str, use_streamlit_feedback: bool = False) -> TypingList[str]:
#     pages_text = []
#     if not os.path.exists(pdf_path):
#         msg = f"Error: PDF file not found at '{pdf_path}'"
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#         return pages_text
#     try:
#         doc = fitz.open(pdf_path)
#         if use_streamlit_feedback: st.caption(f"Extracting text from {len(doc)} pages in '{Path(pdf_path).name}'...")
#         for i, page in enumerate(doc):
#             text = page.get_text("text")
#             pages_text.append(text.strip() if text else "")
#         doc.close()
#     except Exception as e:
#         msg = f"Error reading PDF {pdf_path}: {e}"
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#     return pages_text

# def calculate_sequence_similarity_ratio_for_diff(text1: str, text2: str) -> float:
#     if not text1 and not text2:
#         return 1.0
#     if not text1 or not text2:
#         return 0.0
#     return SequenceMatcher(None, text1, text2).ratio()

# def get_detailed_contextual_diff_enhanced_for_diff(text_v1: str, text_v2: str, num_context_lines: int = 4) -> str:
#     lines_v1 = text_v1.splitlines()
#     lines_v2 = text_v2.splitlines()
#     d = Differ()
#     diff_result = list(d.compare(lines_v1, lines_v2))
    
#     output_lines = []
#     has_changes = False
    
#     for i, line in enumerate(diff_result):
#         if line.startswith('+ ') or line.startswith('- '):
#             has_changes = True
#             if not output_lines or output_lines[-1] == "---":
#                  if output_lines and output_lines[-1] == "---": output_lines.pop()
#                  for j in range(max(0, i - num_context_lines), i):
#                     if j < len(diff_result) and diff_result[j].startswith('  '):
#                         output_lines.append(diff_result[j])
#             output_lines.append(line)
#         elif line.startswith('  ') and has_changes and (not output_lines or not output_lines[-1].startswith('  ')):
#             trailing_context_count = 0
#             temp_trailing_context = []
#             for k in range(i, min(len(diff_result), i + num_context_lines)):
#                 if diff_result[k].startswith('  '):
#                     temp_trailing_context.append(diff_result[k])
#                     trailing_context_count +=1
#                 else:
#                     break
#             output_lines.extend(temp_trailing_context)
#             if temp_trailing_context and i + trailing_context_count < len(diff_result) :
#                  output_lines.append("---")
#             has_changes = False
#         elif line.startswith('? '):
#             pass

#     if not output_lines:
#         return "No significant textual differences found by difflib."

#     final_output = []
#     if output_lines:
#         final_output.append(output_lines[0])
#         for i in range(1, len(output_lines)):
#             if output_lines[i] == "---" and final_output[-1] == "---":
#                 continue
#             final_output.append(output_lines[i])
#         if final_output and final_output[-1] == "---":
#             final_output.pop()
#     return "\n".join(final_output) if final_output else "No significant textual differences found by difflib."

# def generate_document_diff_json(pdf_path_v1: str, pdf_path_v2: str, context_lines: int = 2, use_streamlit_feedback: bool = False) -> Optional[str]:
#     if use_streamlit_feedback:
#         st.info(f"Starting document-level difference analysis between '{Path(pdf_path_v1).name}' and '{Path(pdf_path_v2).name}'...")

#     text_v1_pages = extract_text_from_pdf_pages_for_diff(pdf_path_v1, use_streamlit_feedback)
#     text_v2_pages = extract_text_from_pdf_pages_for_diff(pdf_path_v2, use_streamlit_feedback)

#     if not text_v1_pages or not text_v2_pages:
#         msg = "Could not extract text from one or both documents. Aborting analysis."
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#         return None

#     min_pages = min(len(text_v1_pages), len(text_v2_pages))
#     page_analysis_for_llm = []

#     if use_streamlit_feedback: st.write("--- Page-by-Page Similarity & Contextual Diff ---")
    
#     for i in range(min_pages):
#         page_text_v1 = text_v1_pages[i]
#         page_text_v2 = text_v2_pages[i]
#         similarity_ratio = calculate_sequence_similarity_ratio_for_diff(page_text_v1, page_text_v2)
        
#         context_diff_str = ""
#         if similarity_ratio < 0.999: 
#             context_diff_str = get_detailed_contextual_diff_enhanced_for_diff(page_text_v1, page_text_v2, num_context_lines=context_lines)
        
#         page_analysis_for_llm.append(
#             f"Page {i+1}:\n"
#             f"- Similarity Ratio: {similarity_ratio:.4f}\n"
#             f"- V1 Char Count: {len(page_text_v1)}\n"
#             f"- V2 Char Count: {len(page_text_v2)}\n"
#             + (f"- Contextual Diff Snippet:\n```diff\n{context_diff_str}\n```\n" if context_diff_str and context_diff_str != "No significant textual differences found by difflib." else "- Context: Pages are highly similar or differences are minor.\n")
#         )

#     if len(text_v1_pages) > min_pages:
#         extra_pages_info_v1 = f"Version 1 has {len(text_v1_pages) - min_pages} additional page(s) not present in Version 2 (starting from V1 Page {min_pages + 1})."
#         page_analysis_for_llm.append(extra_pages_info_v1)
#         for i in range(min_pages, len(text_v1_pages)):
#              page_analysis_for_llm.append(f"V1 Additional Page {i+1} Content Snippet:\n```\n{text_v1_pages[i][:200]}...\n```\n")
    
#     if len(text_v2_pages) > min_pages:
#         extra_pages_info_v2 = f"Version 2 has {len(text_v2_pages) - min_pages} additional page(s) not present in Version 1 (starting from V2 Page {min_pages + 1})."
#         page_analysis_for_llm.append(extra_pages_info_v2)
#         for i in range(min_pages, len(text_v2_pages)):
#              page_analysis_for_llm.append(f"V2 Additional Page {i+1} Content Snippet:\n```\n{text_v2_pages[i][:200]}...\n```\n")

#     llm_input_summary = "\n".join(page_analysis_for_llm)
    
#     if not VertexAILangchainLLM:
#         msg = "LLM analysis skipped as VertexAILangchainLLM is not available."
#         if use_streamlit_feedback: st.warning(msg)
#         else: print(msg)
#         return None

#     if use_streamlit_feedback: st.info("Sending document similarity analysis to LLM for JSON diff generation...")
#     llm = VertexAILangchainLLM({}) 
    
#     prompt_template_str = get_difference_prompt() 
#     human_template = HumanMessagePromptTemplate.from_template(prompt_template_str)
#     chat_prompt = ChatPromptTemplate.from_messages([human_template])

#     try:
#         prompt_messages = chat_prompt.format_prompt(page_analysis_summary=llm_input_summary.strip()).to_messages()
#         request_content_str = "".join([msg.content for msg in prompt_messages])
        
#         llm_response_json_str = llm._call(prompt=request_content_str)

#         if use_streamlit_feedback:
#             st.success("LLM analysis response received.")
#         return llm_response_json_str
#     except Exception as e:
#         msg = f"Error during LLM interaction for document diff: {e}"
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#         return None

# def find_pdf_in_version_subfolder(version_path: Path) -> Optional[Path]:
#     if not version_path.is_dir():
#         st.warning(f"Version path not found or not a directory: {version_path}")
#         return None
#     for pdf_stem_folder in version_path.iterdir():
#         if pdf_stem_folder.is_dir():
#             for item in pdf_stem_folder.iterdir():
#                 if item.is_file() and item.name.lower().endswith(".pdf"):
#                     st.info(f"Found PDF for V1 comparison: {item}")
#                     return item
#     st.warning(f"No PDF file found in subfolders of {version_path}.")
#     return None
# # --- End of new helper functions ---


# def find_summaries_dir_in_version_folder(version_folder_path: Path) -> Optional[str]:
#     # This function was for the old summary-based diff. It might not be needed
#     # if we are only doing PDF-to-PDF diff, but keeping it for now in case.
#     if not version_folder_path.is_dir():
#         st.warning(f"Version folder path not found or not a directory: {version_folder_path}")
#         return None
#     for pdf_stem_folder in version_folder_path.iterdir():
#         if pdf_stem_folder.is_dir():
#             potential_summary_dirs = [d for d in pdf_stem_folder.iterdir() if d.is_dir() and d.name.endswith("_summaries")]
#             if potential_summary_dirs:
#                 summary_dir = potential_summary_dirs[0] 
#                 st.info(f"Using summary directory for V1 comparison: {summary_dir}") # This message might be misleading now
#                 return str(summary_dir)
#     st.warning(f"No summary directories (ending with '_summaries') found within subfolders of {version_folder_path}.")
#     return None


# def render_add_new_version_page():
#     st.set_page_config(layout="wide")
#     if init_db: init_db()

#     st.sidebar.page_link(page="pages/home.py", label="Home")
#     st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (V1)")
#     st.sidebar.page_link(page="pages/add_new_version.py", label="Add New Version (V2) & Diff")
#     st.sidebar.page_link(page="pages/view_graphs.py", label="View Difference Graphs")

#     add_vertical_space(1)
#     st.title("Add New Version (V2) and Generate Document Differences")

#     # required_funcs = [UploadProcessor, 
#     #                   # generate_all_diffs, # Removed
#     #                   process_all_diff_jsons, 
#     #                   filter_isolated_nodes, merge_individual_graphs, 
#     #                   create_graph_from_diff, plot_networkx_graph, get_all_regulation_names_from_db,
#     #                   generate_document_diff_json # Added
#     #                   ]
#     # if not all(required_funcs):
#     #     st.error("One or more core components failed to load. Page functionality will be limited.")
#     #     if not get_all_regulation_names_from_db:
#     #         return

#     selected_regulation = None
#     if get_all_regulation_names_from_db:
#         regulation_names = get_all_regulation_names_from_db()
#         if regulation_names:
#             selected_regulation = st.selectbox(
#                 "Select Regulation for V2 Comparison", options=[""] + regulation_names, index=0,
#                 key="main_page_reg_select_v2_compare"
#             )
#         else:
#             st.info("No regulations found. Please add an initial regulation (V1) first.")
#             return
#     else:
#         st.warning("Regulation selection unavailable (DB function missing).")
#         return

#     if not selected_regulation:
#         st.info("Please select a regulation above to proceed.")
#         return

#     session_key_uploaded_file = f"v2_uploaded_file_{selected_regulation}"
#     if session_key_uploaded_file not in st.session_state:
#         st.session_state[session_key_uploaded_file] = None

#     st.subheader(f"Upload V2 PDF for '{selected_regulation}'")
#     uploaded_file_v2 = st.file_uploader(
#         "Upload PDF for Version 2 Document", type=["pdf"], 
#         key=f"v2_pdf_uploader_new_version_page_{selected_regulation}"
#     )

#     if uploaded_file_v2:
#         st.session_state[session_key_uploaded_file] = uploaded_file_v2
#         st.caption(f"Uploaded V2: {uploaded_file_v2.name}")

#     if st.session_state.get(session_key_uploaded_file) and selected_regulation:
#         if st.button(f"Process V2 & Generate Document Diffs for '{selected_regulation}'", 
#                      key=f"process_v2_diff_new_version_page_{selected_regulation}"):
            
#             v2_file_obj = st.session_state[session_key_uploaded_file]
#             v2_file_stem = Path(v2_file_obj.name).stem
#             v2_processor_base_path = Path(RESOURCE_PATH) / selected_regulation / "new"
#             v2_processor_instance_name = v2_file_stem # This is the subfolder under "new" named after the V2 PDF stem

#             with st.spinner(f"Processing V2 document '{v2_file_obj.name}'..."):
#                 processor_v2 = UploadProcessor(
#                     st_object=st, uploaded_file_obj=v2_file_obj,
#                     regulation_name=v2_processor_instance_name, # This creates "new/<v2_pdf_stem>"
#                     resource_path=str(v2_processor_base_path)   # Base for processor is "new"
#                 )
#                 v2_processed_pdf = processor_v2._save_pdf()
#                 if v2_processed_pdf:
#                     v2_processed_ok = processor_v2._extract_and_save_text()
                    
#             if v2_processed_ok:
#                 st.success(f"V2 document '{v2_file_obj.name}' processed successfully.")
                
#                 # Locate V1 PDF
#                 v1_version_folder_path = Path(RESOURCE_PATH) / selected_regulation / "old"
#                 v1_pdf_path = find_pdf_in_version_subfolder(v1_version_folder_path)
                
#                 # V2 PDF path is available from the processor
#                 v2_pdf_path = processor_v2.saved_pdf_path # This is "new/<v2_pdf_stem>/<v2_pdf_name.pdf>"

#                 if v1_pdf_path and v2_pdf_path.exists():
#                     st.info("Proceeding to generate document-level differences...")
#                     with st.expander("Document Difference Generation Log", expanded=True):
#                         diff_json_str = generate_document_diff_json(
#                             pdf_path_v1=str(v1_pdf_path),
#                             pdf_path_v2=str(v2_pdf_path),
#                             use_streamlit_feedback=True
#                         )
                    
#                     if diff_json_str:
#                         st.success("Document difference JSON generated successfully by LLM.")
                        
#                         # Save the new diff JSON
#                         diff_output_dir = Path(RESOURCE_PATH) / selected_regulation / "document_diff_json"
#                         diff_output_dir.mkdir(parents=True, exist_ok=True)
                        
#                         # Use V2 PDF stem for the output filename to associate it with the V2 version
#                         output_json_filename = f"{v2_file_stem}_vs_V1_diff.json"
#                         output_json_filepath = diff_output_dir / output_json_filename

#                         try:
#                             # Attempt to parse and re-serialize for pretty printing, or save as is
#                             parsed_json = json.loads(diff_json_str)
#                             with open(output_json_filepath, 'w', encoding='utf-8') as f:
#                                 json.dump(parsed_json, f, indent=2, ensure_ascii=False)
#                             st.info(f"Document difference JSON saved to: {output_json_filepath}")
#                             st.json(parsed_json) # Display the generated JSON in the UI
#                         except json.JSONDecodeError:
#                             st.warning("LLM output was not valid JSON. Saving raw output.")
#                             with open(output_json_filepath, 'w', encoding='utf-8') as f:
#                                 f.write(diff_json_str)
#                             st.info(f"Raw document difference output saved to: {output_json_filepath}")
#                             st.text_area("Raw LLM Output", diff_json_str, height=300)
#                         except Exception as e:
#                             st.error(f"Error saving diff JSON: {e}")

#                         # --- Graph plotting section (currently incompatible with new JSON format) ---
#                         # The following code for graph generation expects a different JSON structure
#                         # and multiple files. It will likely fail or produce incorrect results with
#                         # the new single document_diff_json (which is an array).
#                         # This section needs to be adapted or replaced to work with the new JSON format.
#                         st.warning("Graph plotting based on the new document-level diff JSON is not yet implemented. "
#                                    "The old graph logic below is commented out as it's incompatible.")
                        
#                         # actual_diff_json_folder = Path(RESOURCE_PATH) / selected_regulation / "graph_diff_json" / v2_summary_folder_name_for_diff_json
#                         # if actual_diff_json_folder.is_dir() and list(actual_diff_json_folder.glob('*.json')):
#                         #     with st.spinner("Processing diff JSONs and building graphs..."):
#                         #         list_of_graphs_with_names = process_all_diff_jsons(str(actual_diff_json_folder))
#                         #         if list_of_graphs_with_names:
#                         #             st.subheader("Individual Chunk Difference Graphs")
#                         #             graphs_for_merging = []
#                         #             # ... (rest of the old graph plotting logic) ...
#                         # else:
#                         #     st.error(f"Diff JSON folder not found or empty at '{actual_diff_json_folder}'. Cannot generate graph.")
#                         # --- End of commented out graph plotting section ---

#                     else:
#                         st.warning("Document difference JSON generation reported issues or did not complete.")
#                 else: 
#                     if not v1_pdf_path: st.error(f"Could not find V1 PDF in '{v1_version_folder_path}'. Cannot generate diff.")
#                     if not v2_pdf_path.exists(): st.error(f"V2 PDF path not found: {v2_pdf_path}. This should not happen if V2 processing was OK.")
#             else: 
#                 st.error(f"Failed to process V2 document '{v2_file_obj.name}'.")

#             st.session_state[session_key_uploaded_file] = None 
#             st.rerun()

# if __name__ == "__main__":
#     render_add_new_version_page()

#####======================================

# import streamlit as st
# from streamlit_extras.add_vertical_space import add_vertical_space
# import os
# from pathlib import Path
# from typing import Optional, List as TypingList

# import fitz
# from difflib import SequenceMatcher, Differ
# from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
# import json

# from upload_interface import UploadProcessor
# from get_difference_prompt import get_difference_prompt
# from llm_call import VertexAILangchainLLM

# # Import new DB functions from new_regulation.py
# try:
#     from .new_regulation import (
#         get_all_regulation_names_from_db, init_db, RESOURCE_PATH,
#         add_summary_to_db, add_graph_to_db # Import new functions
#     )
# except ImportError:
#     try:
#         from pages.new_regulation import (
#             get_all_regulation_names_from_db, init_db, RESOURCE_PATH,
#             add_summary_to_db, add_graph_to_db
#         )
#     except ImportError:
#         st.error("Could not import DB functions from new_regulation.py. Functionality will be limited.")
#         get_all_regulation_names_from_db = None
#         init_db = None
#         add_summary_to_db = None
#         add_graph_to_db = None
#         RESOURCE_PATH = "resources"

# # --- Helper functions for PDF diffing ---
# def extract_text_from_pdf_pages_for_diff(pdf_path: str, use_streamlit_feedback: bool = False) -> TypingList[str]:
#     pages_text = []
#     if not os.path.exists(pdf_path):
#         msg = f"Error: PDF file not found at '{pdf_path}'"
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#         return pages_text
#     try:
#         doc = fitz.open(pdf_path)
#         if use_streamlit_feedback: st.caption(f"Extracting text from {len(doc)} pages in '{Path(pdf_path).name}'...")
#         for i, page in enumerate(doc):
#             text = page.get_text("text")
#             pages_text.append(text.strip() if text else "")
#         doc.close()
#     except Exception as e:
#         msg = f"Error reading PDF {pdf_path}: {e}"
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#     return pages_text

# def calculate_sequence_similarity_ratio_for_diff(text1: str, text2: str) -> float:
#     if not text1 and not text2:
#         return 1.0
#     if not text1 or not text2:
#         return 0.0
#     return SequenceMatcher(None, text1, text2).ratio()

# def get_detailed_contextual_diff_enhanced_for_diff(text_v1: str, text_v2: str, num_context_lines: int = 4) -> str:
#     lines_v1 = text_v1.splitlines()
#     lines_v2 = text_v2.splitlines()
#     d = Differ()
#     diff_result = list(d.compare(lines_v1, lines_v2))
#     output_lines = []
#     has_changes = False
#     for i, line in enumerate(diff_result):
#         if line.startswith('+ ') or line.startswith('- '):
#             has_changes = True
#             if not output_lines or output_lines[-1] == "---":
#                  if output_lines and output_lines[-1] == "---": output_lines.pop()
#                  for j in range(max(0, i - num_context_lines), i):
#                     if j < len(diff_result) and diff_result[j].startswith('  '):
#                         output_lines.append(diff_result[j])
#             output_lines.append(line)
#         elif line.startswith('  ') and has_changes and (not output_lines or not output_lines[-1].startswith('  ')):
#             trailing_context_count = 0
#             temp_trailing_context = []
#             for k in range(i, min(len(diff_result), i + num_context_lines)):
#                 if diff_result[k].startswith('  '):
#                     temp_trailing_context.append(diff_result[k])
#                     trailing_context_count +=1
#                 else:
#                     break
#             output_lines.extend(temp_trailing_context)
#             if temp_trailing_context and i + trailing_context_count < len(diff_result) :
#                  output_lines.append("---")
#             has_changes = False
#         elif line.startswith('? '):
#             pass # Ignore hint lines from Differ
#     if not output_lines: return "No significant textual differences found by difflib."
#     final_output = []
#     if output_lines:
#         final_output.append(output_lines[0])
#         for i in range(1, len(output_lines)):
#             if output_lines[i] == "---" and final_output[-1] == "---": continue
#             final_output.append(output_lines[i])
#         if final_output and final_output[-1] == "---": final_output.pop()
#     return "\n".join(final_output) if final_output else "No significant textual differences found by difflib."

# def generate_document_diff_json(pdf_path_v1: str, pdf_path_v2: str, context_lines: int = 2, use_streamlit_feedback: bool = False) -> Optional[str]:
#     if use_streamlit_feedback:
#         st.info(f"Starting document-level difference analysis between '{Path(pdf_path_v1).name}' and '{Path(pdf_path_v2).name}'...")
#     text_v1_pages = extract_text_from_pdf_pages_for_diff(pdf_path_v1, use_streamlit_feedback)
#     text_v2_pages = extract_text_from_pdf_pages_for_diff(pdf_path_v2, use_streamlit_feedback)
#     if not text_v1_pages or not text_v2_pages:
#         msg = "Could not extract text from one or both documents. Aborting analysis."
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#         return None
#     min_pages = min(len(text_v1_pages), len(text_v2_pages))
#     page_analysis_for_llm = []
#     if use_streamlit_feedback: st.write("--- Page-by-Page Similarity & Contextual Diff ---")
#     for i in range(min_pages):
#         page_text_v1 = text_v1_pages[i]
#         page_text_v2 = text_v2_pages[i]
#         similarity_ratio = calculate_sequence_similarity_ratio_for_diff(page_text_v1, page_text_v2)
#         context_diff_str = ""
#         if similarity_ratio < 0.999:
#             context_diff_str = get_detailed_contextual_diff_enhanced_for_diff(page_text_v1, page_text_v2, num_context_lines=context_lines)
#         page_analysis_for_llm.append(
#             f"Page {i+1}:\n"
#             f"- Similarity Ratio: {similarity_ratio:.4f}\n"
#             f"- V1 Char Count: {len(page_text_v1)}\n"
#             f"- V2 Char Count: {len(page_text_v2)}\n"
#             + (f"- Contextual Diff Snippet:\n```diff\n{context_diff_str}\n```\n" if context_diff_str and context_diff_str != "No significant textual differences found by difflib." else "- Context: Pages are highly similar or differences are minor.\n")
#         )
#     if len(text_v1_pages) > min_pages:
#         extra_pages_info_v1 = f"Version 1 has {len(text_v1_pages) - min_pages} additional page(s) not present in Version 2 (starting from V1 Page {min_pages + 1})."
#         page_analysis_for_llm.append(extra_pages_info_v1)
#         for i in range(min_pages, len(text_v1_pages)):
#              page_analysis_for_llm.append(f"V1 Additional Page {i+1} Content Snippet:\n```\n{text_v1_pages[i][:200]}...\n```\n")
#     if len(text_v2_pages) > min_pages:
#         extra_pages_info_v2 = f"Version 2 has {len(text_v2_pages) - min_pages} additional page(s) not present in Version 1 (starting from V2 Page {min_pages + 1})."
#         page_analysis_for_llm.append(extra_pages_info_v2)
#         for i in range(min_pages, len(text_v2_pages)):
#              page_analysis_for_llm.append(f"V2 Additional Page {i+1} Content Snippet:\n```\n{text_v2_pages[i][:200]}...\n```\n")
#     llm_input_summary = "\n".join(page_analysis_for_llm)
#     if not VertexAILangchainLLM:
#         msg = "LLM analysis skipped as VertexAILangchainLLM is not available."
#         if use_streamlit_feedback: st.warning(msg)
#         else: print(msg)
#         return None
#     if use_streamlit_feedback: st.info("Sending document similarity analysis to LLM for JSON diff generation...")
#     llm = VertexAILangchainLLM({})
#     prompt_template_str = get_difference_prompt()
#     human_template = HumanMessagePromptTemplate.from_template(prompt_template_str)
#     chat_prompt = ChatPromptTemplate.from_messages([human_template])
#     try:
#         prompt_messages = chat_prompt.format_prompt(page_analysis_summary=llm_input_summary.strip()).to_messages()
#         request_content_str = "".join([msg.content for msg in prompt_messages])
#         llm_response_json_str = llm._call(prompt=request_content_str)
#         if use_streamlit_feedback: st.success("LLM analysis response received.")
#         return llm_response_json_str
#     except Exception as e:
#         msg = f"Error during LLM interaction for document diff: {e}"
#         if use_streamlit_feedback: st.error(msg)
#         else: print(msg)
#         return None

# def find_pdf_in_version_subfolder(version_path: Path) -> Optional[Path]:
#     """Finds the first PDF file within any subfolder of the given version_path."""
#     if not version_path.is_dir():
#         st.warning(f"Version path not found or not a directory: {version_path}")
#         return None
#     for pdf_stem_folder in version_path.iterdir(): # e.g., "old/MyDocumentV1_Stem"
#         if pdf_stem_folder.is_dir():
#             for item in pdf_stem_folder.iterdir(): # e.g., "old/MyDocumentV1_Stem/MyDocumentV1.pdf"
#                 if item.is_file() and item.name.lower().endswith(".pdf"):
#                     st.info(f"Found PDF for comparison: {item}")
#                     return item
#     st.warning(f"No PDF file found in subfolders of {version_path}.")
#     return None
# # --- End of new helper functions ---

# def render_add_new_version_page():
#     st.set_page_config(layout="wide")
#     if init_db: init_db() # Initialize DB using SQLAlchemy

#     # Sidebar Navigation
#     st.sidebar.page_link(page="pages/home.py", label="Home")
#     st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (V1)")
#     st.sidebar.page_link(page="pages/add_new_version.py", label="Add New Version (V2) & Diff")
#     st.sidebar.page_link(page="pages/view_graphs.py", label="View Difference Graphs")

#     add_vertical_space(1)
#     st.title("Add New Version (V2) and Generate Document Differences")

#     selected_regulation = None
#     if get_all_regulation_names_from_db:
#         regulation_names = get_all_regulation_names_from_db()
#         if regulation_names:
#             selected_regulation = st.selectbox(
#                 "Select Regulation for V2 Comparison", options=[""] + regulation_names, index=0,
#                 key="main_page_reg_select_v2_compare"
#             )
#         else:
#             st.info("No regulations found. Please add an initial regulation (V1) first.")
#             return
#     else:
#         st.warning("Regulation selection unavailable (DB function missing).")
#         return

#     if not selected_regulation:
#         st.info("Please select a regulation above to proceed.")
#         return

#     session_key_uploaded_file = f"v2_uploaded_file_{selected_regulation}"
#     if session_key_uploaded_file not in st.session_state:
#         st.session_state[session_key_uploaded_file] = None

#     st.subheader(f"Upload V2 PDF for '{selected_regulation}'")
#     uploaded_file_v2 = st.file_uploader(
#         "Upload PDF for Version 2 Document", type=["pdf"],
#         key=f"v2_pdf_uploader_new_version_page_{selected_regulation}"
#     )

#     if uploaded_file_v2:
#         st.session_state[session_key_uploaded_file] = uploaded_file_v2
#         st.caption(f"Uploaded V2: {uploaded_file_v2.name}")

#     if st.session_state.get(session_key_uploaded_file) and selected_regulation:
#         if st.button(f"Process V2 & Generate Document Diffs for '{selected_regulation}'",
#                      key=f"process_v2_diff_new_version_page_{selected_regulation}"):

#             v2_file_obj = st.session_state[session_key_uploaded_file]
#             v2_file_stem = Path(v2_file_obj.name).stem

#             v2_processor_base_path = Path(RESOURCE_PATH) / selected_regulation / "new"
#             v2_processor_instance_name = v2_file_stem # This is the subfolder under "new"

#             v2_processed_ok = False
#             processor_v2 = None

#             with st.spinner(f"Processing V2 document '{v2_file_obj.name}'..."):
#                 if UploadProcessor:
#                     processor_v2 = UploadProcessor(
#                         st_object=st, uploaded_file_obj=v2_file_obj,
#                         regulation_name=v2_processor_instance_name,
#                         resource_path=str(v2_processor_base_path)
#                     )
#                     v2_processed_ok = processor_v2.process() # Handles PDF save, text extraction, summarization
#                 else:
#                     st.error("UploadProcessor is not available. Cannot process V2 document.")


#             if v2_processed_ok and processor_v2:
#                 st.success(f"V2 document '{v2_file_obj.name}' processed successfully.")

#                 if add_summary_to_db:
#                     v2_summary_dir_path = v2_processor_base_path / v2_processor_instance_name / f"{v2_file_stem}_summaries"
#                     if v2_summary_dir_path.is_dir() and any(v2_summary_dir_path.iterdir()):
#                         summary_name_for_db = f"{v2_file_stem}_summaries"
#                         version_tag_for_db = f"NEW_{v2_file_stem}"
#                         add_summary_to_db(
#                             regulation_name=selected_regulation,
#                             summary_name=summary_name_for_db,
#                             summary_path=str(v2_summary_dir_path),
#                             version_tag=version_tag_for_db
#                         )
#                     else:
#                         st.caption(f"No summaries generated for V2 '{v2_file_obj.name}' or directory empty. DB record for summary skipped.")

#                 v1_version_folder_path = Path(RESOURCE_PATH) / selected_regulation / "old"
#                 v1_pdf_path = find_pdf_in_version_subfolder(v1_version_folder_path)
#                 v2_pdf_path = processor_v2.saved_pdf_path # Path from UploadProcessor

#                 if v1_pdf_path and v2_pdf_path.exists():
#                     st.info("Proceeding to generate document-level differences...")
#                     with st.expander("Document Difference Generation Log", expanded=True):
#                         diff_json_str = generate_document_diff_json(
#                             pdf_path_v1=str(v1_pdf_path),
#                             pdf_path_v2=str(v2_pdf_path),
#                             use_streamlit_feedback=True
#                         )

#                     if diff_json_str:
#                         st.success("Document difference JSON generated successfully by LLM.")
#                         diff_output_dir = Path(RESOURCE_PATH) / selected_regulation / "document_diff_json"
#                         diff_output_dir.mkdir(parents=True, exist_ok=True)
                        
#                         v1_pdf_stem_for_filename = Path(v1_pdf_path).stem if v1_pdf_path else "V1_Unknown"
#                         output_json_filename = f"{v2_file_stem}_vs_{v1_pdf_stem_for_filename}_diff.json"
#                         output_json_filepath = diff_output_dir / output_json_filename

#                         try:
#                             parsed_json = json.loads(diff_json_str)
#                             with open(output_json_filepath, 'w', encoding='utf-8') as f:
#                                 json.dump(parsed_json, f, indent=2, ensure_ascii=False)
#                             st.info(f"Document difference JSON saved to: {output_json_filepath}")
#                             st.json(parsed_json)

#                             if add_graph_to_db:
#                                 graph_name_for_db = output_json_filename
#                                 graph_version_tag = f"V2_{v2_file_stem}_vs_V1_{v1_pdf_stem_for_filename}"
#                                 add_graph_to_db(
#                                     regulation_name=selected_regulation,
#                                     graph_name=graph_name_for_db,
#                                     graph_path=str(output_json_filepath),
#                                     version_tag=graph_version_tag
#                                 )
#                         except json.JSONDecodeError:
#                             st.warning("LLM output was not valid JSON. Saving raw output.")
#                             with open(output_json_filepath, 'w', encoding='utf-8') as f: f.write(diff_json_str)
#                             st.info(f"Raw document difference output saved to: {output_json_filepath}")
#                             st.text_area("Raw LLM Output", diff_json_str, height=300)
#                         except Exception as e:
#                             st.error(f"Error saving/processing diff JSON: {e}")
                        
#                         st.warning("Graph plotting based on the new document-level diff JSON is not yet implemented. "
#                                    "The old graph logic (if any was here) is incompatible.")
#                     else:
#                         st.warning("Document difference JSON generation reported issues or did not complete.")
#                 else:
#                     if not v1_pdf_path: st.error(f"Could not find V1 PDF in '{v1_version_folder_path}'. Cannot generate diff.")
#                     if not v2_pdf_path.exists(): st.error(f"V2 PDF path not found: {v2_pdf_path}.")
#             else:
#                 st.error(f"Failed to process V2 document '{v2_file_obj.name}'.")

#             st.session_state[session_key_uploaded_file] = None
#             st.rerun()

# if __name__ == "__main__":
#     if init_db: init_db() # Ensure DB is initialized
#     render_add_new_version_page()



####*********************************

import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
from pathlib import Path
from typing import Optional, List as TypingList

import fitz
from difflib import SequenceMatcher, Differ
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
import json

from upload_interface import UploadProcessor
from get_difference_prompt import get_difference_prompt
from llm_call import VertexAILangchainLLM

try:
    from .new_regulation import (
        get_all_regulation_names_from_db, init_db, RESOURCE_PATH,
        add_summary_to_db, add_graph_to_db,
        get_latest_pdf_path_for_regulation_version # Import new function
    )
except ImportError:
    try:
        from pages.new_regulation import (
            get_all_regulation_names_from_db, init_db, RESOURCE_PATH,
            add_summary_to_db, add_graph_to_db,
            get_latest_pdf_path_for_regulation_version # Import new function
        )
    except ImportError:
        st.error("Could not import DB functions from new_regulation.py. Functionality will be limited.")
        get_all_regulation_names_from_db = None
        init_db = None
        add_summary_to_db = None
        add_graph_to_db = None
        get_latest_pdf_path_for_regulation_version = None # Ensure it's defined
        RESOURCE_PATH = "resources"

# --- Helper functions for PDF diffing (extract_text..., calculate_sequence..., get_detailed_contextual..., generate_document_diff_json) ---
# These functions remain unchanged from your previous version. For brevity, they are not repeated here.
# Assume they are present as before.

def extract_text_from_pdf_pages_for_diff(pdf_path: str, use_streamlit_feedback: bool = False) -> TypingList[str]:
    pages_text = []
    if not os.path.exists(pdf_path):
        msg = f"Error: PDF file not found at '{pdf_path}'"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return pages_text
    try:
        doc = fitz.open(pdf_path)
        if use_streamlit_feedback: st.caption(f"Extracting text from {len(doc)} pages in '{Path(pdf_path).name}'...")
        for i, page in enumerate(doc):
            text = page.get_text("text")
            pages_text.append(text.strip() if text else "")
        doc.close()
    except Exception as e:
        msg = f"Error reading PDF {pdf_path}: {e}"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
    return pages_text

def calculate_sequence_similarity_ratio_for_diff(text1: str, text2: str) -> float:
    if not text1 and not text2:
        return 1.0
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1, text2).ratio()

def get_detailed_contextual_diff_enhanced_for_diff(text_v1: str, text_v2: str, num_context_lines: int = 4) -> str:
    lines_v1 = text_v1.splitlines()
    lines_v2 = text_v2.splitlines()
    d = Differ()
    diff_result = list(d.compare(lines_v1, lines_v2))
    output_lines = []
    has_changes = False
    for i, line in enumerate(diff_result):
        if line.startswith('+ ') or line.startswith('- '):
            has_changes = True
            if not output_lines or output_lines[-1] == "---":
                 if output_lines and output_lines[-1] == "---": output_lines.pop()
                 for j in range(max(0, i - num_context_lines), i):
                    if j < len(diff_result) and diff_result[j].startswith('  '):
                        output_lines.append(diff_result[j])
            output_lines.append(line)
        elif line.startswith('  ') and has_changes and (not output_lines or not output_lines[-1].startswith('  ')):
            trailing_context_count = 0
            temp_trailing_context = []
            for k in range(i, min(len(diff_result), i + num_context_lines)):
                if diff_result[k].startswith('  '):
                    temp_trailing_context.append(diff_result[k])
                    trailing_context_count +=1
                else:
                    break
            output_lines.extend(temp_trailing_context)
            if temp_trailing_context and i + trailing_context_count < len(diff_result) :
                 output_lines.append("---")
            has_changes = False
        elif line.startswith('? '):
            pass # Ignore hint lines from Differ
    if not output_lines: return "No significant textual differences found by difflib."
    final_output = []
    if output_lines:
        final_output.append(output_lines[0])
        for i in range(1, len(output_lines)):
            if output_lines[i] == "---" and final_output[-1] == "---": continue
            final_output.append(output_lines[i])
        if final_output and final_output[-1] == "---": final_output.pop()
    return "\n".join(final_output) if final_output else "No significant textual differences found by difflib."

def generate_document_diff_json(pdf_path_v1: str, pdf_path_v2: str, context_lines: int = 2, use_streamlit_feedback: bool = False) -> Optional[str]:
    if use_streamlit_feedback:
        st.info(f"Starting document-level difference analysis between '{Path(pdf_path_v1).name}' and '{Path(pdf_path_v2).name}'...")
    text_v1_pages = extract_text_from_pdf_pages_for_diff(pdf_path_v1, use_streamlit_feedback)
    text_v2_pages = extract_text_from_pdf_pages_for_diff(pdf_path_v2, use_streamlit_feedback)
    if not text_v1_pages or not text_v2_pages:
        msg = "Could not extract text from one or both documents. Aborting analysis."
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return None
    min_pages = min(len(text_v1_pages), len(text_v2_pages))
    page_analysis_for_llm = []
    if use_streamlit_feedback: st.write("--- Page-by-Page Similarity & Contextual Diff ---")
    for i in range(min_pages):
        page_text_v1 = text_v1_pages[i]
        page_text_v2 = text_v2_pages[i]
        similarity_ratio = calculate_sequence_similarity_ratio_for_diff(page_text_v1, page_text_v2)
        context_diff_str = ""
        if similarity_ratio < 0.999:
            context_diff_str = get_detailed_contextual_diff_enhanced_for_diff(page_text_v1, page_text_v2, num_context_lines=context_lines)
        page_analysis_for_llm.append(
            f"Page {i+1}:\n"
            f"- Similarity Ratio: {similarity_ratio:.4f}\n"
            f"- V1 Char Count: {len(page_text_v1)}\n"
            f"- V2 Char Count: {len(page_text_v2)}\n"
            + (f"- Contextual Diff Snippet:\n```diff\n{context_diff_str}\n```\n" if context_diff_str and context_diff_str != "No significant textual differences found by difflib." else "- Context: Pages are highly similar or differences are minor.\n")
        )
    if len(text_v1_pages) > min_pages:
        extra_pages_info_v1 = f"Version 1 has {len(text_v1_pages) - min_pages} additional page(s) not present in Version 2 (starting from V1 Page {min_pages + 1})."
        page_analysis_for_llm.append(extra_pages_info_v1)
        for i in range(min_pages, len(text_v1_pages)):
             page_analysis_for_llm.append(f"V1 Additional Page {i+1} Content Snippet:\n```\n{text_v1_pages[i][:200]}...\n```\n")
    if len(text_v2_pages) > min_pages:
        extra_pages_info_v2 = f"Version 2 has {len(text_v2_pages) - min_pages} additional page(s) not present in Version 1 (starting from V2 Page {min_pages + 1})."
        page_analysis_for_llm.append(extra_pages_info_v2)
        for i in range(min_pages, len(text_v2_pages)):
             page_analysis_for_llm.append(f"V2 Additional Page {i+1} Content Snippet:\n```\n{text_v2_pages[i][:200]}...\n```\n")
    llm_input_summary = "\n".join(page_analysis_for_llm)
    if not VertexAILangchainLLM:
        msg = "LLM analysis skipped as VertexAILangchainLLM is not available."
        if use_streamlit_feedback: st.warning(msg)
        else: print(msg)
        return None
    if use_streamlit_feedback: st.info("Sending document similarity analysis to LLM for JSON diff generation...")
    llm = VertexAILangchainLLM({})
    prompt_template_str = get_difference_prompt()
    human_template = HumanMessagePromptTemplate.from_template(prompt_template_str)
    chat_prompt = ChatPromptTemplate.from_messages([human_template])
    try:
        prompt_messages = chat_prompt.format_prompt(page_analysis_summary=llm_input_summary.strip()).to_messages()
        request_content_str = "".join([msg.content for msg in prompt_messages])
        llm_response_json_str = llm._call(prompt=request_content_str)
        if use_streamlit_feedback: st.success("LLM analysis response received.")
        return llm_response_json_str
    except Exception as e:
        msg = f"Error during LLM interaction for document diff: {e}"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return None
# --- End of PDF diffing helper functions ---

def render_add_new_version_page():
    st.set_page_config(layout="wide")
    if init_db: init_db()

    st.sidebar.page_link(page="pages/home.py", label="Home")
    st.sidebar.page_link(page="pages/new_regulation.py", label="Add New Regulation (V1)")
    st.sidebar.page_link(page="pages/add_new_version.py", label="Add New Version (V2) & Diff")
    st.sidebar.page_link(page="pages/view_graphs.py", label="View Difference Graphs")

    add_vertical_space(1)
    st.title("Add New Version (V2) and Generate Document Differences")

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
    else:
        st.warning("Regulation selection unavailable (DB function missing).")
        return

    if not selected_regulation:
        st.info("Please select a regulation above to proceed.")
        return


    session_key_uploaded_file = f"v2_uploaded_file_{selected_regulation}"
    if session_key_uploaded_file not in st.session_state and selected_regulation not in st.session_state:
        st.session_state["selected_regulation"] = selected_regulation
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
        if st.button(f"Process V2 & Generate Document Diffs for '{selected_regulation}'",
                     key=f"process_v2_diff_new_version_page_{selected_regulation}"):

            v2_file_obj = st.session_state[session_key_uploaded_file]
            v2_file_stem = Path(v2_file_obj.name).stem
            v2_processor_base_path = Path(RESOURCE_PATH) / selected_regulation / "new"
            v2_processor_instance_name = v2_file_stem
            v2_processed_ok = False
            processor_v2 = None

            with st.spinner(f"Processing V2 document '{v2_file_obj.name}'..."):
                if UploadProcessor:
                    processor_v2 = UploadProcessor(
                        st_object=st, uploaded_file_obj=v2_file_obj,
                        regulation_name=v2_processor_instance_name,
                        resource_path=str(v2_processor_base_path)
                    )
                    # v2_processed_ok = processor_v2.process()
                    v2_processed_pdf = processor_v2._save_pdf()
                    if v2_processed_pdf:
                        v2_processed_ok = processor_v2._extract_and_save_text()
                    else:
                        st.error("UploadProcessor is not available. Cannot process V2 document.")

            if v2_processed_ok and processor_v2:
                st.success(f"V2 document '{v2_file_obj.name}' processed successfully.")
                if add_summary_to_db:
                    v2_summary_dir_path = v2_processor_base_path / v2_processor_instance_name / f"{v2_file_stem}_summaries"
                    if v2_summary_dir_path.is_dir() and any(v2_summary_dir_path.iterdir()):
                        summary_name_for_db = f"{v2_file_stem}_summaries"
                        version_tag_for_db = f"NEW_{v2_file_stem}" # e.g. NEW_MyDocV2
                        add_summary_to_db(
                            regulation_name=selected_regulation,
                            summary_name=summary_name_for_db,
                            summary_path=str(v2_summary_dir_path),
                            version_tag=version_tag_for_db
                        )
                    else:
                        st.caption(f"No summaries generated for V2 '{v2_file_obj.name}' or directory empty. DB record for summary skipped.")

                v1_pdf_path = None
                if get_latest_pdf_path_for_regulation_version:
                    with st.spinner(f"Locating latest V1 PDF for '{selected_regulation}' from database..."):
                        v1_pdf_path = get_latest_pdf_path_for_regulation_version(selected_regulation, "OLD")
                else:
                    st.error("Function to get V1 PDF path from DB is not available.")

                v2_pdf_path = processor_v2.saved_pdf_path

                if v1_pdf_path and v1_pdf_path.exists() and v2_pdf_path.exists():
                    st.info("Proceeding to generate document-level differences...")
                    with st.expander("Document Difference Generation Log", expanded=True):
                        diff_json_str = generate_document_diff_json(
                            pdf_path_v1=str(v1_pdf_path),
                            pdf_path_v2=str(v2_pdf_path),
                            use_streamlit_feedback=True
                        )
                    if diff_json_str:
                        st.success("Document difference JSON generated successfully by LLM.")
                        diff_output_dir = Path(RESOURCE_PATH) / selected_regulation / "document_diff_json"
                        diff_output_dir.mkdir(parents=True, exist_ok=True)
                        v1_pdf_stem_for_filename = Path(v1_pdf_path).stem
                        output_json_filename = f"{v2_file_stem}_vs_{v1_pdf_stem_for_filename}_diff.json"
                        output_json_filepath = diff_output_dir / output_json_filename
                        try:
                            parsed_json = json.loads(diff_json_str)
                            with open(output_json_filepath, 'w', encoding='utf-8') as f:
                                json.dump(parsed_json, f, indent=2, ensure_ascii=False)
                            st.info(f"Document difference JSON saved to: {output_json_filepath}")
                            st.json(parsed_json)
                            if add_graph_to_db:
                                graph_name_for_db = output_json_filename
                                graph_version_tag = f"V2_{v2_file_stem}_vs_V1_{v1_pdf_stem_for_filename}"
                                add_graph_to_db(
                                    regulation_name=selected_regulation,
                                    graph_name=graph_name_for_db,
                                    graph_path=str(output_json_filepath),
                                    version_tag=graph_version_tag
                                )
                        except json.JSONDecodeError:
                            st.warning("LLM output was not valid JSON. Saving raw output.")
                            with open(output_json_filepath, 'w', encoding='utf-8') as f: f.write(diff_json_str)
                            st.info(f"Raw document difference output saved to: {output_json_filepath}")
                            st.text_area("Raw LLM Output", diff_json_str, height=300)
                        except Exception as e:
                            st.error(f"Error saving/processing diff JSON: {e}")
                        st.warning("Graph plotting based on the new document-level diff JSON is not yet implemented.")
                    else:
                        st.warning("Document difference JSON generation reported issues or did not complete.")
                else:
                    if not v1_pdf_path or not v1_pdf_path.exists():
                        st.error(f"Could not find or access the latest V1 PDF for '{selected_regulation}' using database records. Cannot generate diff.")
                    if not v2_pdf_path.exists():
                        st.error(f"V2 PDF path not found: {v2_pdf_path}.")
            else:
                st.error(f"Failed to process V2 document '{v2_file_obj.name}'.")

            st.session_state[session_key_uploaded_file] = None
            st.rerun()

if __name__ == "__main__":
    if init_db: init_db()
    render_add_new_version_page()


