# def get_graph_prompt():
#     prompt = """**Objective:** You will be provided with two structured summaries, one from Version 1 and one from Version 2 of a document, corresponding to the same page or conceptual section. Your goal is to compare these two summaries, identify any differences in entities (nodes) or relationships (edges), and if differences exist, output a single JSON object detailing these changes. If there are no differences between the two provided summaries, you should output an empty JSON object `{{}}`.

#             summary_version_1
#             -----------------
#             {summary_v1}

#             summary_version_2
#             -----------------
#             {summary_v2}

#             **Input:**
#             You will receive two text inputs:
#             1.  `summary_v1`: A structured summary from Version 1 of the document.
#             2.  `summary_v2`: A structured summary from Version 2 of the document, corresponding to the same page/section as summary_v1.

#             Each summary (if not empty) will typically include:
#             *   Overall Summary
#             *   Key Entities/Concepts (Nodes) with descriptions.
#             *   Key Relationships/Interactions (Edges) with source, target, and nature of relationship.
#             *   Main Theme/Information Clusters.

#             **Instructions:**

#             1.  **Compare Summaries:** Carefully compare both the summaries.
#             2.  **Identify Differences:** Look for:
#                 *   Entities present in one version but not the other.
#                 *   Relationships present in one version but not the other.
#                 *   Changes in the description or attributes of common entities.
#                 *   Changes in the nature or attributes of common relationships.
#             3.  **Output JSON (Only if Differences Exist):**
#                 *   If and only if you find any differences, generate a single JSON object with two main keys: `"nodes_diff"` and `"edges_diff"`.
#                 *   If there are NO differences between them output an empty JSON object.

#             **JSON Structure (if differences exist):**

#             *   **`"nodes_diff"`**: (Object) Contains details about node differences.
#                 *   `"added_in_v2"`: (Array of Objects) Nodes present in `summary_v2` but not in `summary_v1`.
#                     *   Each object: `{{"label": "Node Label", "description": "Node Description from V2"}}`
#                 *   `"removed_from_v1"`: (Array of Objects) Nodes present in `summary_v1` but not in `summary_v2`.
#                     *   Each object: `{{"label": "Node Label", "description": "Node Description from V1"}}`
#                 *   `"modified"`: (Array of Objects) Nodes present in both but with changed attributes.
#                     *   Each object: `{{"label": "Common Node Label", "v1_description": "Desc in V1", "v2_description": "Desc in V2", "other_changed_attributes": {{"attr_name": {{"v1_value": "val1", "v2_value": "val2"}}}}}}` (other_changed_attributes is optional)

#             *   **`"edges_diff"`**: (Object) Contains details about edge differences.
#                 *   `"added_in_v2"`: (Array of Objects) Edges present in `summary_v2` but not in `summary_v1`.
#                     *   Each object: `{{"source_label": "Source Node Label", "target_label": "Target Node Label", "relationship_label": "Relationship Label from V2", "details": "Details from V2"}}`
#                 *   `"removed_from_v1"`: (Array of Objects) Edges present in `summary_v1` but not in `summary_v2`.
#                     *   Each object: `{{"source_label": "Source Node Label", "target_label": "Target Node Label", "relationship_label": "Relationship Label from V1", "details": "Details from V1"}}`
#                 *   `"modified"`: (Array of Objects) Edges between the same entities but with changed relationship label or details.
#                     *   Each object: `{{"source_label": "Source Node Label", "target_label": "Target Node Label", "v1_relationship_label": "Rel Label V1", "v2_relationship_label": "Rel Label V2", "v1_details": "Details V1", "v2_details": "Details V2"}}`

#             **CRITICAL: The entire response must be ONLY the JSON object (or `{{}}` if no differences). Ensure it is complete, valid, and not truncated. Do not include any explanatory text.**

#             **Example JSON Output (If Differences Exist):**
#             ```json
#             {{
#               "nodes_diff": {{
#                 "added_in_v2": [
#                   {{
#                     "label": "New Regulatory Body",
#                     "description": "A body introduced in V2 to oversee compliance."
#                   }}
#                 ],
#                 "removed_from_v1": [],
#                 "modified": [
#                   {{
#                     "label": "EMIR Regulation",
#                     "v1_description": "Financial regulation being updated.",
#                     "v2_description": "Financial regulation extensively revised with new reporting mandates.",
#                     "other_changed_attributes": {{}}
#                   }}
#                 ]
#               }},
#               "edges_diff": {{
#                 "added_in_v2": [
#                   {{
#                     "source_label": "New Regulatory Body",
#                     "target_label": "EMIR Regulation",
#                     "relationship_label": "oversees",
#                     "details": "The new body will ensure adherence to the revised EMIR."
#                   }}
#                 ],
#                 "removed_from_v1": [
#                   {{
#                     "source_label": "Old Task Force",
#                     "target_label": "EMIR Regulation",
#                     "relationship_label": "monitored",
#                     "details": "The task force was responsible for initial monitoring."
#                   }}
#                 ],
#                 "modified": []
#               }}
#             }}
#             ```

#             **Example JSON Output (If NO Differences Exist):**
#             {{}}
#             """
#     return prompt


def get_difference_prompt():
    
    """Returns the prompt template for LLM analysis of similarity scores and diffs."""
    # Prompt remains the same as in your previous version
    template = """
            You are provided with a page-by-page analysis showing differences between two versions of a document (Version 1 and Version 2). This analysis includes contextual diff snippets marked with `+` for added lines, `-` for removed lines, and leading spaces for unchanged context lines.
            Input Page-by-Page Analysis Text:
            ---------------------------------
            {page_analysis_summary}

            **Output JSON Format and Structure:**

            Your primary task is to transform the input analysis into a **valid JSON array**. Each element in this array will be a JSON object representing a distinct change (addition, removal, or modification) identified from the `+` and `-` lines in the diff snippets.

            **Crucial** Maintain the Json format and structure no comment, or any other strings and ignore the header changes or insignificant changes like spelling changes , formatting changes and etc.

            **Make a strict note of responding in valid JSON only. Don’t explain.**

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