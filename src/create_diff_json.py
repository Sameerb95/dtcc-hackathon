# from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
# from langchain_google_vertexai import VertexAI 
# from llm_call import VertexAILangchainLLM
# from graph_diff_prompt import get_graph_prompt
# import os
# import traceback

# def send_data_to_vertex_ai(summary_v1_path, summary_v2_path, output_json_path):
#     """
#     Compares two summary files and generates a JSON diff if changes are found.
#     """
#     try:
#         with open(summary_v1_path, 'r', encoding='utf-8') as f1, \
#              open(summary_v2_path, 'r', encoding='utf-8') as f2:
#             summary_v1_content = f1.read()
#             summary_v2_content = f2.read()
#     except FileNotFoundError as e:
#         print(f"Error: Could not read summary files: {e}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred while reading files: {e}")
#         return None

#     if not summary_v1_content and not summary_v2_content:
#         print("Both summary files are empty. No comparison to perform.")
#         try:
#             with open(output_json_path, 'w', encoding='utf-8') as f:
#                 f.write("{}") # Write an empty JSON object string
#             print(f"Wrote empty JSON to {output_json_path} as both summaries were empty.")
#         except IOError as e:
#             print(f"Error writing empty JSON to {output_json_path}: {e}")
#         return "{}" # Return the string representation of an empty JSON

#     print(f"--- Comparing summaries and sending to Vertex AI for diff generation ---")
    
#     template_string = get_graph_prompt()
#     human_message_prompt = HumanMessagePromptTemplate.from_template(template_string)
#     chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

#     try:
#         formatted_messages = chat_prompt.format_prompt(
#             summary_v1=summary_v1_content,
#             summary_v2=summary_v2_content
#         ).to_messages()
#     except Exception as e:
#         print(f"Error during chat_prompt.format_prompt: {e}")
#         traceback.print_exc()
#         return None

#     print(f"Formatted Messages to LLM: {[msg.content for msg in formatted_messages]}") # For debugging


#     llm = VertexAILangchainLLM({})
#     try:
#         response_content = llm._call(prompt=str(formatted_messages))

#         output_dir = os.path.dirname(output_json_path)
#         if output_dir and not os.path.exists(output_dir):
#             os.makedirs(output_dir)
#             print(f"Created output directory: {output_dir}")

#         with open(output_json_path, 'w', encoding='utf-8') as f:
#             f.write(response_content)
#         print(f"Successfully wrote diff JSON to: {output_json_path}")
#         return response_content
#     except Exception as e:
#         print(f"Error during Vertex AI call or writing JSON: {e}")
#         traceback.print_exc()
#         return None


# if __name__ == "__main__":
#     BASE_SUMMARY_PATH_V1 = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/summary/AWPR Version 1_text"
#     BASE_SUMMARY_PATH_V2 = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/summary/AWPR Version 2_text"
#     OUTPUT_JSON_DIFF_BASE_PATH = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/graph_diff_json"

#     if not os.path.exists(OUTPUT_JSON_DIFF_BASE_PATH):
#         os.makedirs(OUTPUT_JSON_DIFF_BASE_PATH)
#         print(f"Created output directory: {OUTPUT_JSON_DIFF_BASE_PATH}")

#     try:
#         v1_summary_files = sorted([
#             f for f in os.listdir(BASE_SUMMARY_PATH_V1) 
#             if f.endswith(".txt") and os.path.isfile(os.path.join(BASE_SUMMARY_PATH_V1, f))
#         ])
#     except FileNotFoundError:
#         print(f"Error: Version 1 summary folder not found at {BASE_SUMMARY_PATH_V1}")
#         v1_summary_files = [] # Initialize to empty list to prevent further errors
#     except Exception as e:
#         print(f"Error listing files in Version 1 summary folder: {e}")
#         v1_summary_files = []

#     if not v1_summary_files:
#         print(f"No summary files found in {BASE_SUMMARY_PATH_V1}. Exiting.")
#     else:
#         print(f"Found {len(v1_summary_files)} summary files in {BASE_SUMMARY_PATH_V1}. Processing...")

#         for summary_filename in v1_summary_files:
#             summary_v1_filepath = os.path.join(BASE_SUMMARY_PATH_V1, summary_filename)
#             summary_v2_filepath = os.path.join(BASE_SUMMARY_PATH_V2, summary_filename) 

#             base_name_without_ext = os.path.splitext(summary_filename)[0]
#             output_json_filename = f"{base_name_without_ext}_diff.json"
#             output_json_filepath = os.path.join(OUTPUT_JSON_DIFF_BASE_PATH, output_json_filename)

#             print(f"\nProcessing pair:")
#             print(f"  V1 Summary: {summary_v1_filepath}")
#             print(f"  V2 Summary: {summary_v2_filepath}")
#             print(f"  Output JSON: {output_json_filepath}")

#             if os.path.exists(summary_v1_filepath) and os.path.exists(summary_v2_filepath):
#                 send_data_to_vertex_ai(summary_v1_filepath, summary_v2_filepath, output_json_filepath)
#             else:
#                 if not os.path.exists(summary_v1_filepath):
#                     print(f"  Skipping: Version 1 summary file not found: {summary_v1_filepath}")
#                 if not os.path.exists(summary_v2_filepath):
#                     print(f"  Skipping: Version 2 summary file not found: {summary_v2_filepath}")
    
#     print("\nFinished processing all summary file pairs.")

import os
import traceback
import streamlit as st
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from llm_call import VertexAILangchainLLM
from get_difference_prompt import get_graph_prompt # Assuming this is the correct prompt for graph diff JSON
from pathlib import Path

try:
    # Assuming new_regulation.py is in src/pages/
    from pages.new_regulation import add_graph_to_db
except ImportError:
    st.warning("Could not import 'add_graph_to_db' from pages.new_regulation. Graph data will not be saved to the database.")
    add_graph_to_db = None

def send_data_to_vertex_ai(
    selected_regulation: str,
    summary_v1_path: str,
    summary_v2_path: str,
    output_json_path: str,
    v2_folder_name: str,
    v1_chunk_base_name: str,
    use_streamlit_feedback=False
):
    try:
        with open(summary_v1_path, 'r', encoding='utf-8') as f1, \
             open(summary_v2_path, 'r', encoding='utf-8') as f2:
            summary_v1_content = f1.read()
            summary_v2_content = f2.read()
    except FileNotFoundError as e:
        msg = f"Error reading summary files: {e}. V1: '{summary_v1_path}', V2: '{summary_v2_path}'"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return None, None # Return None for response and path
    except Exception as e:
        msg = f"Unexpected error reading files: {e}"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return None, None

    if not summary_v1_content and not summary_v2_content:
        msg = "Both summary files are empty. No comparison to perform."
        if use_streamlit_feedback: st.info(msg)
        else: print(msg)
        try:
            output_dir = os.path.dirname(output_json_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(output_json_path, 'w', encoding='utf-8') as f:
                f.write("[]") # Write empty JSON array for graph compatibility
            msg_written = f"Wrote empty JSON array to {output_json_path} as both summaries were empty."
            if use_streamlit_feedback: st.caption(msg_written)
            else: print(msg_written)
            return "[]", output_json_path # Return empty JSON and path
        except IOError as e:
            msg_io_error = f"Error writing empty JSON to {output_json_path}: {e}"
            if use_streamlit_feedback: st.error(msg_io_error)
            else: print(msg_io_error)
        return None, None

    compare_msg = "Comparing summaries and sending to Vertex AI for diff generation..."
    if use_streamlit_feedback: st.caption(compare_msg)
    else: print(f"--- {compare_msg} ---")

    template_string = get_graph_prompt()
    human_message_prompt = HumanMessagePromptTemplate.from_template(template_string)
    chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

    try:
        formatted_messages = chat_prompt.format_prompt(
            summary_v1=summary_v1_content,
            summary_v2=summary_v2_content
        ).to_messages()
    except Exception as e:
        msg_format_error = f"Error during chat_prompt.format_prompt: {e}"
        if use_streamlit_feedback: st.error(msg_format_error)
        else: print(msg_format_error)
        traceback.print_exc()
        return None, None

    llm = VertexAILangchainLLM({})
    try:
        response_content = llm._call(prompt=str(formatted_messages))
        output_dir = os.path.dirname(output_json_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            if use_streamlit_feedback: st.caption(f"Created output directory: {output_dir}")
            else: print(f"Created output directory: {output_dir}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            f.write(response_content)
        success_msg = f"Successfully wrote diff JSON to: {output_json_path}"
        if use_streamlit_feedback: st.caption(success_msg)
        else: print(success_msg)

        if add_graph_to_db:
            graph_name_for_db = os.path.basename(output_json_path)
            version_tag_for_db = f"V2_{v2_folder_name}_vs_V1_{v1_chunk_base_name}"
            add_graph_to_db(
                regulation_name=selected_regulation,
                graph_name=graph_name_for_db,
                graph_path=output_json_path,
                version_tag=version_tag_for_db
            )
            db_save_msg = f"Graph metadata for '{graph_name_for_db}' saved to database."
            if use_streamlit_feedback: st.caption(db_save_msg)
            else: print(db_save_msg)
        else:
            no_db_msg = "Skipping database save for graph metadata (add_graph_to_db not available)."
            if use_streamlit_feedback: st.caption(no_db_msg)
            else: print(no_db_msg)

        return response_content, output_json_path # Return response and the path
    except Exception as e:
        error_msg = f"Error during Vertex AI call or writing JSON for {output_json_path}: {e}"
        if use_streamlit_feedback: st.error(error_msg)
        else: print(error_msg)
        traceback.print_exc()
        return None, None

def generate_all_diffs(selected_regulation:str, base_summary_path_v1_arg: str, base_summary_path_v2_arg: str, use_streamlit_feedback=False):
    OUTPUT_JSON_DIFF_BASE_PATH = f"resources/{selected_regulation}/graph_diff_json"
    BASE_SUMMARY_PATH_V1 = base_summary_path_v1_arg
    BASE_SUMMARY_PATH_V2 = base_summary_path_v2_arg

    if not os.path.exists(BASE_SUMMARY_PATH_V1):
        msg = f"Error: Version 1 summary folder not found at '{BASE_SUMMARY_PATH_V1}'"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return False
    if not os.path.exists(BASE_SUMMARY_PATH_V2):
        msg = f"Error: Version 2 summary folder not found at '{BASE_SUMMARY_PATH_V2}'"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return False

    if not os.path.exists(OUTPUT_JSON_DIFF_BASE_PATH):
        os.makedirs(OUTPUT_JSON_DIFF_BASE_PATH)
        msg = f"Created base output directory for diffs: {OUTPUT_JSON_DIFF_BASE_PATH}"
        if use_streamlit_feedback: st.info(msg)
        else: print(msg)

    try:
        v1_summary_files = sorted([
            f for f in os.listdir(BASE_SUMMARY_PATH_V1)
            if f.endswith(".txt") and os.path.isfile(os.path.join(BASE_SUMMARY_PATH_V1, f))
        ])
    except Exception as e:
        msg = f"Error listing files in Version 1 summary folder '{BASE_SUMMARY_PATH_V1}': {e}"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return False

    if not v1_summary_files:
        msg = f"No summary files found in {BASE_SUMMARY_PATH_V1}. Cannot generate differences."
        if use_streamlit_feedback: st.warning(msg)
        else: print(msg)
        return False # Return False as no processing will occur

    msg_found = f"Found {len(v1_summary_files)} summary files in {BASE_SUMMARY_PATH_V1} to process against {BASE_SUMMARY_PATH_V2}."
    if use_streamlit_feedback: st.info(msg_found)
    else: print(msg_found)

    processed_count = 0
    skipped_count = 0
    error_count = 0
    last_successful_json_path = None # Variable to store the path of the last successful JSON
    progress_bar = None
    if use_streamlit_feedback:
        progress_text = "Processing summary pairs..."
        progress_bar = st.progress(0, text=progress_text)

    for i, summary_filename in enumerate(v1_summary_files):
        if use_streamlit_feedback and progress_bar:
            progress_bar.progress((i + 1) / len(v1_summary_files), text=f"Processing {summary_filename}...")

        summary_v1_filepath = os.path.join(BASE_SUMMARY_PATH_V1, summary_filename)
        summary_v2_filepath = os.path.join(BASE_SUMMARY_PATH_V2, summary_filename)
        base_name_without_ext = Path(summary_filename).stem
        v2_folder_name = Path(BASE_SUMMARY_PATH_V2).name
        specific_output_json_dir = os.path.join(OUTPUT_JSON_DIFF_BASE_PATH, v2_folder_name)
        os.makedirs(specific_output_json_dir, exist_ok=True)
        output_json_filename = f"{base_name_without_ext}_diff.json"
        output_json_filepath = os.path.join(specific_output_json_dir, output_json_filename)

        if use_streamlit_feedback: st.markdown(f"--- \n**Processing:** `{summary_filename}`")
        else: print(f"\nProcessing pair: {summary_filename}")

        if os.path.exists(summary_v1_filepath) and os.path.exists(summary_v2_filepath):
            response, successful_path = send_data_to_vertex_ai(
                selected_regulation=selected_regulation,
                summary_v1_path=summary_v1_filepath,
                summary_v2_path=summary_v2_filepath,
                output_json_path=output_json_filepath,
                v2_folder_name=v2_folder_name,
                v1_chunk_base_name=base_name_without_ext,
                use_streamlit_feedback=use_streamlit_feedback
            )
            if response and successful_path:
                processed_count += 1
                last_successful_json_path = successful_path # Update last successful path
            elif response is not None and successful_path is None: # Case where empty JSON was written due to empty summaries
                processed_count +=1 # Count it as processed, as a file was written
                last_successful_json_path = output_json_filepath
            else:
                error_count +=1
        else:
            skipped_count += 1
            skip_reasons = []
            if not os.path.exists(summary_v1_filepath):
                skip_reasons.append(f"V1 summary not found at {summary_v1_filepath}")
            if not os.path.exists(summary_v2_filepath):
                skip_reasons.append(f"V2 summary not found at {summary_v2_filepath}")
            full_skip_msg = f"Skipping `{summary_filename}`: " + "; ".join(skip_reasons)
            if use_streamlit_feedback: st.caption(full_skip_msg)
            else: print(full_skip_msg.replace("`",""))

    if use_streamlit_feedback and progress_bar:
        progress_bar.empty()

    final_msg = f"Finished processing for V2 summaries in '{BASE_SUMMARY_PATH_V2}'. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}."
    if use_streamlit_feedback:
        if error_count > 0: st.error(final_msg)
        elif skipped_count > 0 and processed_count > 0: st.warning(final_msg)
        elif processed_count > 0 : st.success(final_msg)
        else: st.warning(final_msg) # Covers case where nothing was processed, skipped, or errored (e.g. no v1 files)
    else: print(f"\n{final_msg}")

    if use_streamlit_feedback and processed_count > 0 and last_successful_json_path:
        st.success("Successfully generated graph differences. Navigating to view graphs...")
        st.switch_page(f"pages/view_graphs.py?initial_graph_path={last_successful_json_path}")
    elif use_streamlit_feedback and processed_count == 0:
        st.warning("No graph differences were successfully generated. Staying on this page.")

    return processed_count > 0

if __name__ == "__main__":
    test_regulation_name = "AWPR2_Test"
    test_v1_path = f"resources/{test_regulation_name}/summary/AWPR Version 1_text"
    test_v2_path = f"resources/{test_regulation_name}/summary/AWPR Version 2_text"

    Path(test_v1_path).mkdir(parents=True, exist_ok=True)
    Path(test_v2_path).mkdir(parents=True, exist_ok=True)

    # Create dummy files for testing
    # with open(os.path.join(test_v1_path, "chunk_1.txt"), "w") as f: f.write("V1 content for chunk 1.")
    # with open(os.path.join(test_v2_path, "chunk_1.txt"), "w") as f: f.write("V2 content for chunk 1.")
    # with open(os.path.join(test_v1_path, "chunk_2.txt"), "w") as f: f.write("V1 content for chunk 2.")
    # with open(os.path.join(test_v2_path, "chunk_2.txt"), "w") as f: f.write("V2 content for chunk 2.")


    if os.path.exists(test_v1_path) and os.path.exists(test_v2_path):
        print(f"Running direct test for create_diff_json.py with Regulation: {test_regulation_name}, V1: {test_v1_path}, V2: {test_v2_path}")
        success = generate_all_diffs(test_regulation_name, test_v1_path, test_v2_path, use_streamlit_feedback=False)
        if success:
            print("Test completed. In a Streamlit app, this would switch to view_graphs.py with the last JSON path.")
        else:
            print("Test completed, but no diffs were successfully generated or conditions not met for page switch.")
    else:
        print(f"Direct test skipped: Default summary paths not found for regulation '{test_regulation_name}'.")
