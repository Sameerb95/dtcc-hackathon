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
from graph_diff_prompt import get_graph_prompt

def send_data_to_vertex_ai(summary_v1_path, summary_v2_path, output_json_path, use_streamlit_feedback=False):
    # ... (function content remains the same)
    try:
        with open(summary_v1_path, 'r', encoding='utf-8') as f1, \
             open(summary_v2_path, 'r', encoding='utf-8') as f2:
            summary_v1_content = f1.read()
            summary_v2_content = f2.read()
    except FileNotFoundError as e:
        msg = f"Error reading summary files: {e}. V1: '{summary_v1_path}', V2: '{summary_v2_path}'"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return None
    except Exception as e:
        msg = f"Unexpected error reading files: {e}"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return None

    if not summary_v1_content and not summary_v2_content:
        msg = "Both summary files are empty. No comparison to perform."
        if use_streamlit_feedback: st.info(msg)
        else: print(msg)
        try:
            output_dir = os.path.dirname(output_json_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(output_json_path, 'w', encoding='utf-8') as f:
                f.write("{}") 
            msg_written = f"Wrote empty JSON to {output_json_path} as both summaries were empty."
            if use_streamlit_feedback: st.caption(msg_written)
            else: print(msg_written)
        except IOError as e:
            msg_io_error = f"Error writing empty JSON to {output_json_path}: {e}"
            if use_streamlit_feedback: st.error(msg_io_error)
            else: print(msg_io_error)
        return "{}" 

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
        return None

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
        return response_content
    except Exception as e:
        error_msg = f"Error during Vertex AI call or writing JSON for {output_json_path}: {e}"
        if use_streamlit_feedback: st.error(error_msg)
        else: print(error_msg)
        traceback.print_exc()
        return None

def generate_all_diffs(selected_regulation:str, base_summary_path_v1_arg: str, base_summary_path_v2_arg: str, use_streamlit_feedback=False):
    """
    Generates difference JSON files by comparing summaries from V1 and V2 paths.
    Args:
        base_summary_path_v1_arg (str): Path to the directory containing V1 summary text files.
        base_summary_path_v2_arg (str): Path to the directory containing V2 summary text files.
        use_streamlit_feedback (bool): If True, use Streamlit elements for feedback.
    """
    # This path can also be made dynamic if needed, e.g., based on regulation name
    OUTPUT_JSON_DIFF_BASE_PATH = f"resources/{selected_regulation}/graph_diff_json"

    # Use the provided arguments for V1 and V2 summary paths
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
    except Exception as e: # Catching general exception after specific FileNotFoundError check above
        msg = f"Error listing files in Version 1 summary folder '{BASE_SUMMARY_PATH_V1}': {e}"
        if use_streamlit_feedback: st.error(msg)
        else: print(msg)
        return False

    if not v1_summary_files:
        msg = f"No summary files found in {BASE_SUMMARY_PATH_V1}. Cannot generate differences."
        if use_streamlit_feedback: st.warning(msg)
        else: print(msg)
        return False # Important to return False if no files to process
    
    msg_found = f"Found {len(v1_summary_files)} summary files in {BASE_SUMMARY_PATH_V1} to process against {BASE_SUMMARY_PATH_V2}."
    if use_streamlit_feedback: st.info(msg_found)
    else: print(msg_found)

    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    progress_bar = None
    if use_streamlit_feedback:
        progress_text = "Processing summary pairs..."
        progress_bar = st.progress(0, text=progress_text)

    for i, summary_filename in enumerate(v1_summary_files):
        if use_streamlit_feedback and progress_bar:
            progress_bar.progress((i + 1) / len(v1_summary_files), text=f"Processing {summary_filename}...")

        summary_v1_filepath = os.path.join(BASE_SUMMARY_PATH_V1, summary_filename)
        summary_v2_filepath = os.path.join(BASE_SUMMARY_PATH_V2, summary_filename) 

        base_name_without_ext = os.path.splitext(summary_filename)[0]
        # Store diffs in a subfolder named after the V2 summary directory to keep them organized
        # e.g., graph_diff_json/AWPR_Version_2_text/chunk_1_diff.json
        v2_folder_name = os.path.basename(BASE_SUMMARY_PATH_V2) # e.g., "AWPR Version 2_text"
        specific_output_json_dir = os.path.join(OUTPUT_JSON_DIFF_BASE_PATH, v2_folder_name)
        os.makedirs(specific_output_json_dir, exist_ok=True)
        output_json_filename = f"{base_name_without_ext}_diff.json"
        output_json_filepath = os.path.join(specific_output_json_dir, output_json_filename)


        if use_streamlit_feedback: st.markdown(f"--- \n**Processing:** `{summary_filename}`")
        else: print(f"\nProcessing pair: {summary_filename}")
        
        path_logs = [
            f"  V1 Summary: `{summary_v1_filepath}`",
            f"  V2 Summary: `{summary_v2_filepath}`",
            f"  Output JSON: `{output_json_filepath}`"
        ]
        for p_log in path_logs:
            if use_streamlit_feedback: st.caption(p_log)
            else: print(p_log.replace("`",""))

        if os.path.exists(summary_v1_filepath) and os.path.exists(summary_v2_filepath):
            response = send_data_to_vertex_ai(summary_v1_filepath, summary_v2_filepath, output_json_filepath, use_streamlit_feedback)
            if response:
                processed_count += 1
            else: 
                error_count +=1
        else:
            skipped_count += 1
            skip_reasons = []
            if not os.path.exists(summary_v1_filepath):
                skip_reasons.append(f"V1 summary not found")
            if not os.path.exists(summary_v2_filepath):
                skip_reasons.append(f"V2 summary not found")
            
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
        else: st.warning(final_msg)
    else: print(f"\n{final_msg}")
    
    return processed_count > 0 or (processed_count == 0 and skipped_count == 0 and error_count == 0 and not v1_summary_files)

if __name__ == "__main__":
    # Example usage (won't run when imported, but good for direct testing)
    # You would need to define these paths for direct script execution
    test_v1_path = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/summary/AWPR Version 1_text"
    test_v2_path = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/summary/AWPR Version 2_text"
    if os.path.exists(test_v1_path) and os.path.exists(test_v2_path):
        print(f"Running direct test for create_diff_json.py with V1: {test_v1_path}, V2: {test_v2_path}")
        generate_all_diffs(test_v1_path, test_v2_path, use_streamlit_feedback=False)
    else:
        print("Direct test skipped: Default summary paths not found.")