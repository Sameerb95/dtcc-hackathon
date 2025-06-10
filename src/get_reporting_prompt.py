def get_report_prompt():

    prompt = """Please analyze the provided JSON data, which outlines the changes between two versions of a graph (v1 and v2). Your task is to generate a clear Key Operating Procedures (KOP) out of it

        For each identified difference, provide:
        1   The overall shift in the graph's structure and meaning.
        2   **[Title Describing the Key Change, e.g., "Introduction of Reporting Week Definition" or "Discontinuation of SLIBOR's Role with Task Force"]**
        3   Explain how relationships and entities have transformed, highlighting the introduction of new concepts, the phasing out of previous ones, and changes in the characteristics of existing elements.
        4   The introduction of new concepts or connections and the phasing out of previous ones.
        5.  Integrate the underlying reasons or implications for these changes, as suggested by the 'details' provided.
        6   The underlying reasons or implications for these changes, as suggested by the 'details' provided.
       

        8.  **Crucially suggest potential next steps, considerations, or solutions that might be relevant in response to these changes.** For example, if a process is newly defined, what might need to be implemented? If a key component is removed, what are the implications to address?

        Finally, provide an overall concise summary highlighting the most significant (High/Medium confidence) changes.

        Input JSON:
        {approved_items_data_string}

            Generate a KOP document with step wise instruction for operational personnel.        """
    return prompt