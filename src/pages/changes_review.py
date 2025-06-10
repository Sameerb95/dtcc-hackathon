# import streamlit as st
# import re
# import os
# # Assuming create_reports.py is in the same directory or src
# try:
#     from create_reports import generate_kop_from_approved_items
# except ImportError:
#     try:
#         from ..create_reports import generate_kop_from_approved_items
#     except ImportError:
#         st.error("Failed to import 'generate_kop_from_approved_items' from create_reports.py")
#         generate_kop_from_approved_items = None

# from get_change_review_prompt import get_change_review_prompt
# from llm_call import VertexAILangchainLLM
# from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate


# # --- Parsing Function (keep as is) ---

# def send_diff_to_llm(graph_difference_json_string):
 
#     print(f"--- Preparing to send to LLM ---")
#     messages = []

#     template = get_change_review_prompt() # Get the prompt string
#     human_template = HumanMessagePromptTemplate.from_template(template)
#     messages.append(human_template) 


#     chat_prompt = ChatPromptTemplate.from_messages(messages)


#     prompt_messages = chat_prompt.format_prompt(difference_json=graph_difference_json_string).to_messages()

#     request_content_str = "".join([msg.content for msg in prompt_messages])


#     print(f"Formatted Prompt for LLM: {request_content_str[:500]}...") # Print start of the prompt

#     llm = VertexAILangchainLLM({}) # Replace with your actual LLM initialization
#     try:
#         # Assuming llm._call expects a single string prompt
#         response = llm._call(prompt=request_content_str)
#         print("\n--- LLM Response ---")
#         print(response)
#         return response
#     except Exception as e:
#         print(f"An error occurred while calling LLM: {e}")
#         return None

#     # # Path to your merged JSON file
#     # merged_json_path = "/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/merged_graph_output.json"

#     # with open(merged_json_path, 'r') as f:
#     #     graph_diff_json_content_string = f.read()

#     #     if graph_diff_json_content_string:
#     #         llm_summary = send_diff_to_llm(graph_diff_json_content_string)
#     #         if llm_summary:
#     #             print("\nSummary generation successful.")
#     #         else:
#     #             print("\nSummary generation failed.")
#     #     else:
#     #         print(f"Error: The file '{merged_json_path}' is empty or could not be read.")

# def parse_llm_analysis_items(response_text):
#     """
#     Parses the LLM response text to extract structured analysis items.
#     """
#     parsed_items = []
    
#     header_match = re.match(r"^(##.*?)\n\n(.*?)\n\n", response_text, re.DOTALL)
#     main_title = ""
#     intro_paragraph = ""
#     if header_match:
#         main_title = header_match.group(1).strip()
#         intro_paragraph = header_match.group(2).strip()
    
#     item_pattern = re.compile(
#         r"\*\*\((?P<item_number>\d+)\)\s*(?P<title_text>[^(]+?)\s*\((?P<confidence>[^)]+)\)\*\*\s*(?P<description_and_next_steps>.*?)(?=\n\n\*\*\(|\Z)",
#         re.DOTALL | re.MULTILINE
#     )

#     for match in item_pattern.finditer(response_text):
#         item_number = match.group("item_number").strip()
#         title_text = match.group("title_text").strip()
#         confidence = match.group("confidence").strip()
#         description_and_next_steps = match.group("description_and_next_steps").strip()

#         next_steps_match = re.search(r"\*Next Steps:\* (.*)", description_and_next_steps, re.DOTALL)
#         description = description_and_next_steps
#         next_steps = "Not specified."

#         if next_steps_match:
#             next_steps = next_steps_match.group(1).strip()
#             description = description_and_next_steps[:next_steps_match.start()].strip()
        
#         item_id = f"analysis_item_{item_number}"

#         parsed_items.append({
#             "id": item_id,
#             "item_number": item_number,
#             "title_display": f"({item_number}) {title_text}",
#             "title_text": title_text,
#             "confidence": confidence,
#             "description": description,
#             "next_steps": next_steps
#         })
        
#     return main_title, intro_paragraph, parsed_items

# # --- Streamlit Page ---
# def render_llm_analysis_dashboard():
#     st.set_page_config(layout="wide", page_title="LLM Analysis Dashboard")
    
#     if 'analysis_item_statuses' not in st.session_state:
#         st.session_state.analysis_item_statuses = {}

#     main_title, intro_paragraph, parsed_items = parse_llm_analysis_items(LLM_RESPONSE_TEXT)

#     if main_title:
#         st.markdown(main_title)
#     else:
#         st.title("📋 LLM Analysis Review Dashboard")

#     if intro_paragraph:
#         st.markdown(intro_paragraph)
    
#     st.caption("Review analysis items, approve/reject, and view details. Generate KOP from approved items.")
#     st.divider()

#     # --- Button to Generate KOP from Approved Items ---
#     approved_items_data = []
#     if parsed_items: # Check if there are items to iterate over
#         for item in parsed_items:
#             if st.session_state.analysis_item_statuses.get(item["id"]) == "Approved":
#                 approved_items_data.append(item)
    
#     if approved_items_data:
#         st.sidebar.subheader("Reporting")
#         if st.sidebar.button("📄 Generate KOP from Approved Items", key="generate_kop_btn"):
#             if generate_kop_from_approved_items: # Check if the function is available
#                 with st.spinner("Generating KOP document... This may take a few moments."):
                   
#                     output_dir_for_kop = "generated_reports" # This will create "generated_reports/KOP/"
                    
#                     saved_kop_path = generate_kop_from_approved_items(
#                         approved_items_data, 
#                         output_directory=output_dir_for_kop,
#                         filename="KOP_From_Approved_Analysis.docx" # You can customize the filename
#                     )
#                 if saved_kop_path:
#                     st.sidebar.success(f"KOP document generated!")
#                     with open(saved_kop_path, "rb") as fp:
#                         st.sidebar.download_button(
#                             label="Download KOP (Approved Items)",
#                             data=fp,
#                             file_name=os.path.basename(saved_kop_path), # Gets "KOP_From_Approved_Analysis.docx"
#                             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#                         )
#                 else:
#                     st.sidebar.error("Failed to generate KOP document from approved items.")
#             else:
#                 st.sidebar.error("KOP generation function (for approved items) is not available.")

#     elif 'generate_kop_btn' in st.session_state and st.session_state.generate_kop_btn: # If button was clicked but no approved items
#         st.sidebar.warning("No items have been approved yet to generate a KOP.")


#     # --- Display Parsed Items in a Grid ---
#     if not parsed_items:
#         st.warning("No actionable analysis items could be parsed from the LLM response.")
#         return

#     num_columns = 2
#     cols = st.columns(num_columns)

#     for index, item in enumerate(parsed_items):
#         item_id = item["id"]
#         current_status = st.session_state.analysis_item_statuses.get(item_id, "Pending")
#         target_col = cols[index % num_columns]

#         with target_col:
#             with st.container(border=True):
#                 st.subheader(f"{item['title_display']}")
#                 st.markdown(f"**Confidence:** {item['confidence']}")
                
#                 status_color = "orange"
#                 if current_status == "Approved": status_color = "green"
#                 elif current_status == "Rejected": status_color = "red"
#                 st.markdown(f"**Status:** :{status_color}[{current_status}]")

#                 button_cols = st.columns(2)
#                 with button_cols[0]:
#                     if st.button("✅ Approve", key=f"approve_{item_id}", use_container_width=True, 
#                                  type="primary" if current_status != "Approved" else "secondary",
#                                  disabled=(current_status == "Approved")):
#                         st.session_state.analysis_item_statuses[item_id] = "Approved"
#                         st.rerun() 
#                 with button_cols[1]:
#                     if st.button("❌ Reject", key=f"reject_{item_id}", use_container_width=True,
#                                  type="primary" if current_status != "Rejected" else "secondary",
#                                  disabled=(current_status == "Rejected")):
#                         st.session_state.analysis_item_statuses[item_id] = "Rejected"
#                         st.rerun()

#                 with st.expander("View Details & Recommended Steps"):
#                     st.markdown(f"##### Detailed Analysis:")
#                     st.markdown(f"{item['description']}")
#                     st.markdown(f"##### Recommended Next Steps:")
#                     st.markdown(f"{item['next_steps']}")
                
#                 st.markdown("<br>", unsafe_allow_html=True)

# if __name__ == "__main__":
#     render_llm_analysis_dashboard()





####======================================================

import streamlit as st
import re
import os
from pathlib import Path # Import Path for robust path handling
from  datetime import datetime  as dt

# Assuming create_reports.py is in the same directory or src
try:
    from create_reports import generate_kop_from_approved_items
except ImportError:
    try:
        from ..create_reports import generate_kop_from_approved_items
    except ImportError:
        st.error("Failed to import 'generate_kop_from_approved_items' from create_reports.py")
        generate_kop_from_approved_items = None

try:
    from get_change_review_prompt import get_change_review_prompt
except ImportError:
    st.error("Failed to import 'get_change_review_prompt'. LLM calls will be affected.")
    get_change_review_prompt = None

try:
    from llm_call import VertexAILangchainLLM
except ImportError:
    st.error("Failed to import 'VertexAILangchainLLM'. LLM calls will fail.")
    VertexAILangchainLLM = None

from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate


# --- LLM Interaction Function ---
def send_diff_to_llm(graph_difference_json_string):
    if not VertexAILangchainLLM or not get_change_review_prompt:
        st.error("LLM or prompt function not available. Cannot send data to LLM.")
        return None

    st.caption(f"--- Preparing to send graph difference to LLM for review generation ---")
    messages = []

    template = get_change_review_prompt() # Get the prompt string
    human_template = HumanMessagePromptTemplate.from_template(template)
    messages.append(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(messages)
    prompt_messages = chat_prompt.format_prompt(difference_json=graph_difference_json_string).to_messages()
    request_content_str = "".join([msg.content for msg in prompt_messages])

    # st.caption(f"Formatted Prompt for LLM (first 200 chars): {request_content_str[:200]}...")

    llm = VertexAILangchainLLM({})
    try:
        with st.spinner("Generating change analysis from LLM... This may take a moment."):
            response = llm._call(prompt=request_content_str)
        st.caption("--- LLM Response Received ---")
        # st.text_area("Raw LLM Response (for debugging)", response, height=150) # Optional: for debugging
        return response
    except Exception as e:
        st.error(f"An error occurred while calling LLM: {e}")
        return None

import re

def parse_llm_analysis_items(response_text):
    """
    Parses the LLM response text to extract structured analysis items
    based on the new format.
    """
    if not response_text:
        return "", "", []

    parsed_items = []
    main_title = ""  # Assuming no markdown H1 style title from the new example
    intro_paragraph = ""
    items_text = response_text.strip() # Start with the full text, stripped

    # Find where the first actual item " **1. [" starts to separate intro
    # Regex looks for newline(s) followed by "**digit. ["
    first_item_pattern_match = re.search(r"\n\s*\*\*(?=\d+\.\s*\[)", response_text)

    if first_item_pattern_match:
        intro_paragraph = response_text[:first_item_pattern_match.start()].strip()
        # Get the text from the start of the first item marker
        items_text = response_text[first_item_pattern_match.end():].strip()
        # Prepend the "**" that was part of the lookahead/delimiter
        items_text = "**" + items_text
    else:
        # If no clear separation, check if the text itself starts like an item list
        if items_text.startswith("**1.") or re.match(r"\*\*\d+\.\s*\[", items_text):
            intro_paragraph = "" # No separate intro paragraph
            # items_text is already the full response_text.strip()
        else:
            # Assume all of it is an introduction if no items are detected by pattern
            intro_paragraph = items_text
            items_text = "" # No items to parse

    if not items_text:
        return main_title, intro_paragraph, []

    # Regex for individual items: **N. [Title]: content_body
    # content_body is everything until the next item or end of text.
    item_pattern = re.compile(
        r"\*\*(?P<item_number>\d+)\.\s*\[(?P<title_text>[^\]]+)\]:\s*(?P<content_body>.*?)(?=\n\s*\*\*\d+\.\s*\[|\Z)",
        re.DOTALL | re.MULTILINE
    )

    for match in item_pattern.finditer(items_text):
        item_number = match.group("item_number").strip()
        title_text = match.group("title_text").strip()
        content_body = match.group("content_body").strip()

        # Default values
        id_val = "N/A"
        confidence_val = "N/A"
        next_steps_val = "Not specified."
        description = ""

        # Extract ID from (ID: ...)
        id_match = re.search(r"\(ID:\s*([^)]+)\)", content_body)
        # Extract Confidence from *Confidence Rating: ...*
        confidence_match = re.search(r"\*Confidence Rating:\s*([^.]+)\.\*", content_body)
        # Extract Next Steps from *Next Steps: ... (can be multi-line)
        next_steps_keyword_re = r"\*Next Steps:\s*"
        # Search for the keyword and capture everything after it.
        next_steps_full_match = re.search(f"({next_steps_keyword_re})(.*)", content_body, re.DOTALL)

        # Determine description: text before the first of (ID:), *Confidence Rating:, *Next Steps:
        idx_id_marker = id_match.start() if id_match else float('inf')
        idx_conf_marker = confidence_match.start() if confidence_match else float('inf')
        idx_ns_marker = next_steps_full_match.start() if next_steps_full_match else float('inf')

        end_of_description = min(idx_id_marker, idx_conf_marker, idx_ns_marker)

        if end_of_description != float('inf') and end_of_description > 0 : # end_of_description can be 0 if marker is at start
            description = content_body[:end_of_description].strip()
        elif end_of_description == float('inf'): # No markers found, all of content_body is description
            description = content_body.strip()
        else: # A marker is at the very beginning of content_body
            description = ""


        if id_match:
            id_val = id_match.group(1).strip()

        if confidence_match:
            confidence_val = confidence_match.group(1).strip()

        if next_steps_full_match:
            # group(2) is the content after the "*Next Steps: " keyword itself
            next_steps_val = next_steps_full_match.group(2).strip()

        # Use the extracted ID for the item's unique key if available
        unique_item_identifier = id_val if id_val != "N/A" else f"item_{item_number}"

        parsed_items.append({
            "id": unique_item_identifier,
            "item_number": item_number,
            "title_display": f"({item_number}) {title_text}", # For display
            "title_text": title_text, # Raw title text
            "confidence": confidence_val,
            "description": description,
            "next_steps": next_steps_val,
            "original_id_from_text": id_val # Store the original ID from text
        })

    return main_title, intro_paragraph, parsed_items



# --- Streamlit Page ---
def render_llm_analysis_dashboard():
    st.set_page_config(layout="wide", page_title="LLM Analysis Dashboard")

    # --- Sidebar Navigation ---
    st.sidebar.page_link("pages/home.py", label="Home")
    st.sidebar.page_link("pages/new_regulation.py", label="Add New Regulation (V1)")
    st.sidebar.page_link("pages/add_new_version.py", label="Add New Version (V2) & Diff")
    st.sidebar.page_link("pages/view_graphs.py", label="View Difference Graphs")
    st.sidebar.page_link("pages/changes_review.py", label="Review Changes & KOP")


    if 'analysis_item_statuses' not in st.session_state:
        st.session_state.analysis_item_statuses = {}
    
    # --- Load graph data and get LLM analysis ---
    llm_response_text = None
    if 'graph_data_for_review' in st.session_state and st.session_state.graph_data_for_review:
        graph_json_string = st.session_state.graph_data_for_review
        file_source_info = st.session_state.get('graph_file_path_for_review', 'current graph data')
        if file_source_info != "uploaded_data" and Path(file_source_info).exists():
             st.caption(f"Analyzing differences from: `{Path(file_source_info).name}`")
        else:
             st.caption(f"Analyzing differences from: `{file_source_info}`")

        llm_response_text = """
        'The changes between version 1 (v1) and version 2 (v2) of the graph represent modifications to reporting guidelines, primarily concerning thresholds and loan definitions.  Several key monetary thresholds have been increased, suggesting a potential shift in regulatory focus or economic context.  Additionally, a clause related to loan security has been removed, and the reporting deadline has been slightly adjusted.\n\n**1. [Reporting Deadline Adjustment]:**  The reporting deadline for AWPR has shifted from 12:00 noon to 2:00 PM each Friday. (ID: Reporting_Deadline_Change) This change, while seemingly minor, provides a two-hour extension for reporting.  The underlying reason is not explicitly stated, but it could be due to operational considerations or to accommodate reporting institutions. *Confidence Rating: Low*.  *Next Steps:*  Communicate this change clearly to all reporting entities to ensure compliance with the new deadline.\n\n**2. [Expansion of Short-Term Loan Definition]:** The definition of a short-term loan has been broadened from "3 months or less" to "6 months or less." (ID: Short_Term_Loan_Definition_Expansion) This change significantly impacts the scope of loans considered short-term.  The rationale behind this expansion is not provided, but it could reflect changes in market practices or regulatory priorities. *Confidence Rating: High*. *Next Steps:* Review internal systems and processes to ensure they align with the new definition.  Assess the impact of this change on loan classifications and reporting metrics.\n\n**3. [Increase in Reporting Threshold for Loan Amount Differences]:** The threshold for reporting differences in loan amounts has increased from Rs. 10 million to Rs. 15 million. (ID: Loan_Amount_Difference_Threshold_Increase) This change suggests a focus on larger discrepancies, potentially to reduce reporting burden or prioritize more significant variations. *Confidence Rating: Medium*. *Next Steps:* Adjust reporting systems to reflect the new threshold.  Analyze the potential impact on the detection of significant loan fluctuations.\n\n**4. [Removal of Loan Security Exclusion Clause]:** The clause excluding loans fully secured by cash deposits or government securities has been removed. (ID: Loan_Security_Clause_Removal) This is a significant change, as it broadens the scope of reportable loans.  The reason for this removal is not specified, but it could be related to regulatory changes or a desire for more comprehensive reporting. *Confidence Rating: High*. *Next Steps:*  Update reporting procedures to include previously excluded loans.  Assess the impact of this change on the overall volume and composition of reported loans.\n\n**5. [Increase in Transaction Reporting Threshold]:** The threshold for reporting individual transactions has been raised from Rs. 10 million to Rs. 15 million. (ID: Transaction_Reporting_Threshold_Increase) This change, similar to the loan amount difference threshold increase, likely aims to reduce reporting burden and focus on larger transactions. *Confidence Rating: Medium*. *Next Steps:*  Update reporting systems to reflect the new threshold.  Analyze the potential impact on the detection of significant transactions.\n\n**6. [Adjustment to Small Loan Reporting Threshold]:** The threshold for reporting smaller loans for prime customers when no loans above a certain amount were granted has been increased from Rs. 10 million to Rs. 15 million. (ID: Small_Loan_Reporting_Threshold_Adjustment) This change aligns with the overall trend of increasing reporting thresholds. *Confidence Rating: Medium*. *Next Steps:* Update reporting systems and communicate the change to relevant stakeholders.\n\n**Summary of Significant Changes:**\n\nThe most significant changes (High/Medium confidence) include the expansion of the short-term loan definition, the removal of the loan security exclusion clause, and increases in various reporting thresholds (loan amount differences, individual transactions, and small loans for prime customers). These changes suggest a shift towards focusing on larger transactions and loans, potentially to streamline reporting and prioritize more substantial financial activities.  The removal of the security exclusion clause notably broadens the scope of reportable loans.  These modifications necessitate careful review and adjustment of reporting systems and processes to ensure compliance and accurate data collection.\n'
        """

        # cache_key = f"llm_analysis_{hash(graph_json_string)}"
        # if cache_key in st.session_state:
        #     llm_response_text = st.session_state[cache_key]
        #     st.caption("Using cached LLM analysis.")
        # else:
        #     # llm_response_text = send_diff_to_llm(graph_json_string)
        #     if llm_response_text:
        #         st.session_state[cache_key] = llm_response_text # Cache the response
        #     else:
        #         st.error("Failed to get analysis from LLM.")
    else:
        st.warning("No graph difference data found in session state. Please generate differences first (e.g., via 'View Difference Graphs' page after processing V2).")
        st.markdown("Navigate to View Difference Graphs or Add New Version to generate data.")
        return # Stop further rendering if no data

    # --- Parse LLM response ---
    main_title, intro_paragraph, parsed_items = parse_llm_analysis_items(llm_response_text)

    if main_title:
        st.markdown(main_title) # Display title from LLM if available
    else:
        st.title("📋 LLM Analysis Review Dashboard") # Fallback title

    if intro_paragraph:
        st.markdown(intro_paragraph) # Display intro from LLM
    
    st.caption("Review analysis items, approve/reject, and view details. Generate KOP from approved items.")
    st.divider()

    # --- Button to Generate KOP from Approved Items ---
    approved_items_data = []
    if parsed_items:
        for item in parsed_items:
            if st.session_state.analysis_item_statuses.get(item["id"]) == "Approved":
                approved_items_data.append(item) # Collect data for KOP
    
    # Place KOP generation button in the sidebar for better layout
    st.sidebar.subheader("Reporting Actions")
    if approved_items_data:
        print(approved_items_data)
        if st.sidebar.button("📄 Generate KOP from Approved Items", key="generate_kop_approved_btn"):
            if generate_kop_from_approved_items:
                with st.spinner("Generating KOP document... This may take a few moments."):
                    output_dir_for_kop = "generated_reports"
                    selected_regulation = st.session_state['selected_regulation']
                    saved_kop_path = generate_kop_from_approved_items(
                        approved_items_data,
                        output_directory=output_dir_for_kop,
                        filename=f"KOP_{selected_regulation}_{str(dt.now())}.docx"
                    )
                if saved_kop_path:
                    st.sidebar.success(f"KOP document generated!")
                    with open(saved_kop_path, "rb") as fp:
                        st.sidebar.download_button(
                            label="Download KOP (Approved)",
                            data=fp,
                            file_name=os.path.basename(saved_kop_path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.sidebar.error("Failed to generate KOP document from approved items.")
            else:
                st.sidebar.error("KOP generation function (for approved items) is not available.")
    elif 'generate_kop_approved_btn' in st.session_state and st.session_state.generate_kop_approved_btn:
        st.sidebar.warning("No items have been approved yet to generate a KOP.")
    else: # No approved items, button not clicked yet
        st.sidebar.caption("Approve items in the main panel to enable KOP generation.")


    # --- Display Parsed Items in a Grid ---
    if not parsed_items and llm_response_text: # LLM responded but no items parsed
        st.warning("LLM provided a response, but no actionable analysis items could be parsed from it. Please check the raw LLM response if shown, or try regenerating.")
        if st.button("Retry LLM Analysis"):
            if cache_key in st.session_state: del st.session_state[cache_key] # Clear cache to force re-call
            st.rerun()
        return
    elif not parsed_items and not llm_response_text: # No LLM response at all
        st.error("Could not retrieve or parse LLM analysis.")
        return


    num_columns = 2 # Or 1 for a single column layout, or 3 for more dense
    cols = st.columns(num_columns)

    for index, item in enumerate(parsed_items):
        item_id = item["id"]
        # Default to "Pending" if not yet set
        current_status = st.session_state.analysis_item_statuses.get(item_id, "Pending")
        
        target_col = cols[index % num_columns]

        with target_col:
            with st.container(border=True): # Add a border to each item's container
                st.subheader(f"{item['title_display']}")
                st.markdown(f"**Confidence:** {item['confidence']}")
                
                status_color = "orange" # Default for Pending
                if current_status == "Approved": status_color = "green"
                elif current_status == "Rejected": status_color = "red"
                st.markdown(f"**Status:** :{status_color}[{current_status}]")

                # Action buttons
                button_cols = st.columns(2)
                with button_cols[0]:
                    if st.button("✅ Approve", key=f"approve_{item_id}", use_container_width=True, 
                                 type="primary" if current_status != "Approved" else "secondary",
                                 disabled=(current_status == "Approved")):
                        st.session_state.analysis_item_statuses[item_id] = "Approved"
                        st.rerun() # Rerun to update UI and potentially enable KOP button
                with button_cols[1]:
                    if st.button("❌ Reject", key=f"reject_{item_id}", use_container_width=True,
                                 type="primary" if current_status != "Rejected" else "secondary",
                                 disabled=(current_status == "Rejected")):
                        st.session_state.analysis_item_statuses[item_id] = "Rejected"
                        st.rerun()

                with st.expander("View Details & Recommended Steps"):
                    st.markdown(f"##### Detailed Analysis:")
                    st.markdown(f"{item['description']}") # Ensure this is just the description
                    st.markdown(f"##### Recommended Next Steps:")
                    st.markdown(f"{item['next_steps']}") # Ensure this is just next steps
                
                st.markdown("<br>", unsafe_allow_html=True) # Adds a bit of space at the end of the container

if __name__ == "__main__":
    # For direct testing, you might want to simulate session state
    # if 'graph_data_for_review' not in st.session_state:
    #     # Try to load a default JSON for testing if this page is run directly
    #     # This is just an example, replace with an actual path to a diff JSON
    #     test_json_path = Path("/Users/shirsama/dtcc-hackathon/dtcc-ai-hackathon-2025/src/resources/AWPR2/document_diff_json/AWPR Version 2_vs_AWPR Version 1_diff.json")
    #     if test_json_path.exists():
    #         with open(test_json_path, 'r') as f:
    #             st.session_state.graph_data_for_review = f.read()
    #             st.session_state.graph_file_path_for_review = str(test_json_path)
    #         print(f"INFO (local test): Loaded test graph data from {test_json_path.name}")
    #     else:
    #         print(f"WARNING (local test): Default test JSON not found at {test_json_path}. Dashboard may be empty.")
            
    render_llm_analysis_dashboard()
