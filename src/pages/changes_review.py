import streamlit as st
import re
import os
# Assuming create_reports.py is in the same directory or src
try:
    from create_reports import generate_kop_from_approved_items
except ImportError:
    try:
        from ..create_reports import generate_kop_from_approved_items
    except ImportError:
        st.error("Failed to import 'generate_kop_from_approved_items' from create_reports.py")
        generate_kop_from_approved_items = None


# --- LLM Response Text (keep as is) ---
LLM_RESPONSE_TEXT = """
## Analysis of AWPR Guidelines Changes (v1 to v2)

The changes from v1 to v2 of the AWPR guidelines represent a significant restructuring of the reporting process, introducing greater clarity and specificity.  Several new entities and relationships have been added, reflecting a more detailed and formalized approach to AWPR calculation and reporting.

**(1) Organizational Oversight of AWPR Reporting (High Confidence)**  The introduction of the "Money & Banking Division" (ID: `Money & Banking Division`) and its relationship to the "Economic Research Department" (ID: `Economic Research Department`) clarifies the internal structure of the Central Bank of Sri Lanka (CBSL) responsible for AWPR oversight.  The "Money & Banking Division" is now explicitly identified as the body issuing guidelines for AWPR (ID: `Average Weighted Prime Lending Rate (AWPR)`), adding a layer of organizational accountability. *Next Steps:* Internal communication and role clarity within CBSL should be ensured to reflect these new responsibilities.

**(2) Formal Definition of Reporting Week (High Confidence)** The addition of "Reporting Week" (ID: `Reporting Week`) and its association with the "AWPR Guidelines" (ID: `AWPR Guidelines`) introduces a formal definition of the reporting period (Friday to Thursday). This eliminates potential ambiguity and ensures consistency in data collection. *Next Steps:*  LCBs should be explicitly informed of this standardized reporting week to align their internal processes.

**(3) Impact of SLIBOR Discontinuation on AWPR (High Confidence)** The introduction of "Discontinuation of SLIBOR" (ID: `Discontinuation of SLIBOR`) and its link to "Revision of AWPR Guidelines" (ID: `Revision of AWPR Guidelines`) explicitly acknowledges the catalyst for these changes. This provides valuable context and underscores the importance of adapting the AWPR framework in response to market developments. *Next Steps:*  Further analysis of the implications of SLIBOR's discontinuation on AWPR calculation and its effectiveness as a benchmark should be conducted.

**(4) Refined Reporting Thresholds for Prime Customers (High Confidence)** The introduction of specific threshold values, "Rs. 15 Million Threshold" (ID: `Rs. 15 Million Threshold`) and "Rs. 1 Million Threshold" (ID: `Rs. 1 Million Threshold`), along with their connection to "Reported Transactions" (ID: `Reported Transactions`), provides concrete reporting criteria.  The revised definition of "Prime Customers" (ID: `Prime Customers`) clarifies that loans above Rs. 1 million are reported only if no loans exceed Rs. 15 million, replacing the previous Rs. 10 million threshold (ID: `10 Million Threshold`). This change introduces a more nuanced approach to data collection, potentially impacting the representativeness of the AWPR. *Next Steps:*  Assess the impact of these new thresholds on the composition of reported data and the overall AWPR calculation.  Communicate these changes clearly to LCBs.

**(5) Introduction of Reporting Format and Excluded Lending Types (High Confidence)** The addition of "Reporting Format (Annexure I)" (ID: `Reporting Format (Annexure I)`) and "Excluded Lending (Government, Subsidized)" (ID: `Excluded Lending (Government, Subsidized)`) further formalizes the reporting process.  The specified format ensures consistency and comparability of data, while the exclusion of certain lending types improves the accuracy and relevance of the AWPR as a benchmark for private sector lending. *Next Steps:*  Ensure LCBs have access to and understand the new reporting format and the criteria for excluded lending.

**(6) Clarification of Utilized Balance and Interest Rate (Medium Confidence)** The descriptions of "Utilized Balance" (ID: `Utilized Balance`) and "Interest Rate" (ID: `Interest Rate`) have been refined, and their relationship to AWPR calculation clarified.  While the core meaning remains consistent, the updated language provides greater precision. *Next Steps:* Monitor the interpretation and application of these refined definitions by LCBs.

**(7) Minor Refinements to Terminology and Details (Low Confidence)** Several edges have undergone minor changes in relationship labels or details, such as "LCBs" (ID: `LCBs`) reporting to "AWPR" (ID: `AWPR`) (changing from "Reports" to "report"). These changes are primarily stylistic and do not significantly alter the graph's meaning. *Next Steps:* No specific action required.
"""

# --- Parsing Function (keep as is) ---
def parse_llm_analysis_items(response_text):
    """
    Parses the LLM response text to extract structured analysis items.
    """
    parsed_items = []
    
    header_match = re.match(r"^(##.*?)\n\n(.*?)\n\n", response_text, re.DOTALL)
    main_title = ""
    intro_paragraph = ""
    if header_match:
        main_title = header_match.group(1).strip()
        intro_paragraph = header_match.group(2).strip()
    
    item_pattern = re.compile(
        r"\*\*\((?P<item_number>\d+)\)\s*(?P<title_text>[^(]+?)\s*\((?P<confidence>[^)]+)\)\*\*\s*(?P<description_and_next_steps>.*?)(?=\n\n\*\*\(|\Z)",
        re.DOTALL | re.MULTILINE
    )

    for match in item_pattern.finditer(response_text):
        item_number = match.group("item_number").strip()
        title_text = match.group("title_text").strip()
        confidence = match.group("confidence").strip()
        description_and_next_steps = match.group("description_and_next_steps").strip()

        next_steps_match = re.search(r"\*Next Steps:\* (.*)", description_and_next_steps, re.DOTALL)
        description = description_and_next_steps
        next_steps = "Not specified."

        if next_steps_match:
            next_steps = next_steps_match.group(1).strip()
            description = description_and_next_steps[:next_steps_match.start()].strip()
        
        item_id = f"analysis_item_{item_number}"

        parsed_items.append({
            "id": item_id,
            "item_number": item_number,
            "title_display": f"({item_number}) {title_text}",
            "title_text": title_text,
            "confidence": confidence,
            "description": description,
            "next_steps": next_steps
        })
        
    return main_title, intro_paragraph, parsed_items

# --- Streamlit Page ---
def render_llm_analysis_dashboard():
    st.set_page_config(layout="wide", page_title="LLM Analysis Dashboard")
    
    if 'analysis_item_statuses' not in st.session_state:
        st.session_state.analysis_item_statuses = {}

    main_title, intro_paragraph, parsed_items = parse_llm_analysis_items(LLM_RESPONSE_TEXT)

    if main_title:
        st.markdown(main_title)
    else:
        st.title("📋 LLM Analysis Review Dashboard")

    if intro_paragraph:
        st.markdown(intro_paragraph)
    
    st.caption("Review analysis items, approve/reject, and view details. Generate KOP from approved items.")
    st.divider()

    # --- Button to Generate KOP from Approved Items ---
    approved_items_data = []
    if parsed_items: # Check if there are items to iterate over
        for item in parsed_items:
            if st.session_state.analysis_item_statuses.get(item["id"]) == "Approved":
                approved_items_data.append(item)
    
    if approved_items_data:
        st.sidebar.subheader("Reporting")
        if st.sidebar.button("📄 Generate KOP from Approved Items", key="generate_kop_btn"):
            if generate_kop_from_approved_items: # Check if the function is available
                with st.spinner("Generating KOP document... This may take a few moments."):
                   
                    output_dir_for_kop = "generated_reports" # This will create "generated_reports/KOP/"
                    
                    saved_kop_path = generate_kop_from_approved_items(
                        approved_items_data, 
                        output_directory=output_dir_for_kop,
                        filename="KOP_From_Approved_Analysis.docx" # You can customize the filename
                    )
                if saved_kop_path:
                    st.sidebar.success(f"KOP document generated!")
                    with open(saved_kop_path, "rb") as fp:
                        st.sidebar.download_button(
                            label="Download KOP (Approved Items)",
                            data=fp,
                            file_name=os.path.basename(saved_kop_path), # Gets "KOP_From_Approved_Analysis.docx"
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.sidebar.error("Failed to generate KOP document from approved items.")
            else:
                st.sidebar.error("KOP generation function (for approved items) is not available.")

    elif 'generate_kop_btn' in st.session_state and st.session_state.generate_kop_btn: # If button was clicked but no approved items
        st.sidebar.warning("No items have been approved yet to generate a KOP.")


    # --- Display Parsed Items in a Grid ---
    if not parsed_items:
        st.warning("No actionable analysis items could be parsed from the LLM response.")
        return

    num_columns = 2
    cols = st.columns(num_columns)

    for index, item in enumerate(parsed_items):
        item_id = item["id"]
        current_status = st.session_state.analysis_item_statuses.get(item_id, "Pending")
        target_col = cols[index % num_columns]

        with target_col:
            with st.container(border=True):
                st.subheader(f"{item['title_display']}")
                st.markdown(f"**Confidence:** {item['confidence']}")
                
                status_color = "orange"
                if current_status == "Approved": status_color = "green"
                elif current_status == "Rejected": status_color = "red"
                st.markdown(f"**Status:** :{status_color}[{current_status}]")

                button_cols = st.columns(2)
                with button_cols[0]:
                    if st.button("✅ Approve", key=f"approve_{item_id}", use_container_width=True, 
                                 type="primary" if current_status != "Approved" else "secondary",
                                 disabled=(current_status == "Approved")):
                        st.session_state.analysis_item_statuses[item_id] = "Approved"
                        st.rerun() 
                with button_cols[1]:
                    if st.button("❌ Reject", key=f"reject_{item_id}", use_container_width=True,
                                 type="primary" if current_status != "Rejected" else "secondary",
                                 disabled=(current_status == "Rejected")):
                        st.session_state.analysis_item_statuses[item_id] = "Rejected"
                        st.rerun()

                with st.expander("View Details & Recommended Steps"):
                    st.markdown(f"##### Detailed Analysis:")
                    st.markdown(f"{item['description']}")
                    st.markdown(f"##### Recommended Next Steps:")
                    st.markdown(f"{item['next_steps']}")
                
                st.markdown("<br>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_llm_analysis_dashboard()
