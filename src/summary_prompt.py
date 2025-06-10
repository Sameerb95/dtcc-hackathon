def get_prompt():

    template = """
            You are provided with a page-by-page analysis showing differences between two versions of a document (Version 1 and Version 2). This analysis includes contextual diff snippets marked with `+` for added lines, `-` for removed lines, and leading spaces for unchanged context lines.


            Input Page-by-Page Analysis Text:
            ---------------------------------
            {page_analysis_summary}

            **Output JSON Format and Structure:**

            Your primary task is to transform the input analysis into a **valid JSON array**. Each element in this array will be a JSON object representing a distinct change (addition, removal, or modification) identified from the `+` and `-` lines in the diff snippets.

            **Structure for each JSON object within the array:**

            ```json
            {{
            "source_node": {{
                "id": "string (Unique identifier for the conceptual source of the change, e.g., 'Page_X_Section_Y_v1', or a more abstract concept like 'Reporting_Guidelines_v1')",
                "label": "string (User-friendly label, e.g., 'Page X Section Y Change', 'Reporting Guidelines')",
                "type": "string (Categorization, e.g., 'Document Section', 'Guideline Point', 'Definition')",
                "description_v1": "string (Describe the state of this conceptual entity or related text in version 1, based on '-' lines or context. If purely an addition, this might be 'N/A' or describe the absence.)",
                "description_v2": "string (Describe the state of this conceptual entity or related text in version 2, based on '+' lines or context. If purely a removal, this might be 'N/A' or describe the removal.)"
            }},
            "target_node": {{
                "id": "string (Unique identifier for the conceptual target or specific changed element, e.g., 'Ref_No_Field_v2', 'Loan_Security_Clause_v2')",
                "label": "string (User-friendly label, e.g., 'Reference Number Field', 'Loan Security Clause')",
                "type": "string (Categorization, e.g., 'Field', 'Clause', 'Text Snippet')",
                "description_v1": "string (The specific text or concept from version 1 that was changed/removed, taken from '-' lines. If an addition, this is 'N/A'.)",
                "description_v2": "string (The specific text or concept from version 2 that was added/changed, taken from '+' lines. If a removal, this is 'N/A'.)"
            }},
            "relationship": {{
                "type": "string (Uppercase, e.g., 'MODIFIED_IN', 'ADDED_TO', 'REMOVED_FROM', 'CONTAINS_CHANGE')",
                "label_v1": "string (Label for v1 state, e.g., 'Contained Old Value', 'Included Clause', 'N/A')",
                "label_v2": "string (Label for v2 state, e.g., 'Contains New Value', 'Excludes Clause', 'N/A')",
                "details_v1": "string (Further context for v1, if any, beyond the description_v1 of nodes.)",
                "details_v2": "string (Further context for v2, if any, beyond the description_v2 of nodes.)",
                "change_status": "string ('modified' if both '+' and '-' lines are related to the same conceptual change, 'added' if primarily '+' lines, 'removed' if primarily '-' lines)"
            }},
            "change_description": "string (A concise, human-readable summary of this specific change, directly reflecting the added/removed/modified text. E.g., 'The Reference Number date was updated from 20 December 2021 to 26 December 2024.' or 'The clause regarding loans secured by cash deposits was removed.')"
            }}
    """
    return template