def get_change_review_prompt():

    prompt = """Please analyze the provided JSON data, which outlines the changes between two versions of a graph (v1 and v2). Your task is to generate a comprehensive report in a flowing, human-readable paragraph style.

        For each identified difference, provide:
        1   Give a specific ID to each title so it is easy extract it 
        2   The overall shift in the graph's structure and meaning.
        3   **[Title Describing the Key Change, e.g., "Introduction of Reporting Week Definition" or "Discontinuation of SLIBOR's Role with Task Force"]**
        4   Explain how relationships and entities have transformed, highlighting the introduction of new concepts, the phasing out of previous ones, and changes in the characteristics of existing elements.
        5   The introduction of new concepts or connections and the phasing out of previous ones.
        6  Integrate the underlying reasons or implications for these changes, as suggested by the 'details' provided.
        7   The underlying reasons or implications for these changes, as suggested by the 'details' provided.
        8.  A "Confidence Rating" for the significance of the change (High, Medium, Low).
            *   **Low Confidence:** Assign this to changes that are primarily rephrasing, minor spelling corrections, or slight alterations in 'details' or 'description' fields that do not fundamentally change the meaning or structure. For example, changing "Regulates" to "regulates" or minor wording adjustments in details.
            *   **Medium Confidence:** Assign this to changes in relationship labels that might alter the nuance of a connection but not its core existence, or more substantial changes to 'details' that provide new, but not critical, information.
            *   **High Confidence:** Assign this to the addition or removal of nodes or edges, or modifications to relationship labels or critical attributes that fundamentally alter the graph's structure or the core meaning of a connection.

        9.  **Crucially suggest potential next steps, considerations, or solutions that might be relevant in response to these changes.** For example, if a process is newly defined, what might need to be implemented? If a key component is removed, what are the implications to address?

        Finally, provide an overall concise summary highlighting the most significant (High/Medium confidence) changes.

        Input JSON:
        {difference_json}

        The goal is a cohesive, insightful narrative that not only explains what changed but also why it matters and what might need to be done in response.
        """
    
    return prompt