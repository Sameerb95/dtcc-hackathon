def get_graph_prompt():
    prompt = """**Objective:** You will be provided with two structured summaries, one from Version 1 and one from Version 2 of a document, corresponding to the same page or conceptual section. Your goal is to compare these two summaries, identify any differences in entities (nodes) or relationships (edges), and if differences exist, output a single JSON object detailing these changes. If there are no differences between the two provided summaries, you should output an empty JSON object `{{}}`.

            summary_version_1
            -----------------
            {summary_v1}

            summary_version_2
            -----------------
            {summary_v2}

            **Input:**
            You will receive two text inputs:
            1.  `summary_v1`: A structured summary from Version 1 of the document.
            2.  `summary_v2`: A structured summary from Version 2 of the document, corresponding to the same page/section as summary_v1.

            Each summary (if not empty) will typically include:
            *   Overall Summary
            *   Key Entities/Concepts (Nodes) with descriptions.
            *   Key Relationships/Interactions (Edges) with source, target, and nature of relationship.
            *   Main Theme/Information Clusters.

            **Instructions:**

            1.  **Compare Summaries:** Carefully compare both the summaries.
            2.  **Identify Differences:** Look for:
                *   Entities present in one version but not the other.
                *   Relationships present in one version but not the other.
                *   Changes in the description or attributes of common entities.
                *   Changes in the nature or attributes of common relationships.
            3.  **Output JSON (Only if Differences Exist):**
                *   If and only if you find any differences, generate a single JSON object with two main keys: `"nodes_diff"` and `"edges_diff"`.
                *   If there are NO differences between them output an empty JSON object.

            **JSON Structure (if differences exist):**

            *   **`"nodes_diff"`**: (Object) Contains details about node differences.
                *   `"added_in_v2"`: (Array of Objects) Nodes present in `summary_v2` but not in `summary_v1`.
                    *   Each object: `{{"label": "Node Label", "description": "Node Description from V2"}}`
                *   `"removed_from_v1"`: (Array of Objects) Nodes present in `summary_v1` but not in `summary_v2`.
                    *   Each object: `{{"label": "Node Label", "description": "Node Description from V1"}}`
                *   `"modified"`: (Array of Objects) Nodes present in both but with changed attributes.
                    *   Each object: `{{"label": "Common Node Label", "v1_description": "Desc in V1", "v2_description": "Desc in V2", "other_changed_attributes": {{"attr_name": {{"v1_value": "val1", "v2_value": "val2"}}}}}}` (other_changed_attributes is optional)

            *   **`"edges_diff"`**: (Object) Contains details about edge differences.
                *   `"added_in_v2"`: (Array of Objects) Edges present in `summary_v2` but not in `summary_v1`.
                    *   Each object: `{{"source_label": "Source Node Label", "target_label": "Target Node Label", "relationship_label": "Relationship Label from V2", "details": "Details from V2"}}`
                *   `"removed_from_v1"`: (Array of Objects) Edges present in `summary_v1` but not in `summary_v2`.
                    *   Each object: `{{"source_label": "Source Node Label", "target_label": "Target Node Label", "relationship_label": "Relationship Label from V1", "details": "Details from V1"}}`
                *   `"modified"`: (Array of Objects) Edges between the same entities but with changed relationship label or details.
                    *   Each object: `{{"source_label": "Source Node Label", "target_label": "Target Node Label", "v1_relationship_label": "Rel Label V1", "v2_relationship_label": "Rel Label V2", "v1_details": "Details V1", "v2_details": "Details V2"}}`

            **CRITICAL: The entire response must be ONLY the JSON object (or `{{}}` if no differences). Ensure it is complete, valid, and not truncated. Do not include any explanatory text.**

            **Example JSON Output (If Differences Exist):**
            ```json
            {{
              "nodes_diff": {{
                "added_in_v2": [
                  {{
                    "label": "New Regulatory Body",
                    "description": "A body introduced in V2 to oversee compliance."
                  }}
                ],
                "removed_from_v1": [],
                "modified": [
                  {{
                    "label": "EMIR Regulation",
                    "v1_description": "Financial regulation being updated.",
                    "v2_description": "Financial regulation extensively revised with new reporting mandates.",
                    "other_changed_attributes": {{}}
                  }}
                ]
              }},
              "edges_diff": {{
                "added_in_v2": [
                  {{
                    "source_label": "New Regulatory Body",
                    "target_label": "EMIR Regulation",
                    "relationship_label": "oversees",
                    "details": "The new body will ensure adherence to the revised EMIR."
                  }}
                ],
                "removed_from_v1": [
                  {{
                    "source_label": "Old Task Force",
                    "target_label": "EMIR Regulation",
                    "relationship_label": "monitored",
                    "details": "The task force was responsible for initial monitoring."
                  }}
                ],
                "modified": []
              }}
            }}
            ```

            **Example JSON Output (If NO Differences Exist):**
            {{}}
            """
    return prompt