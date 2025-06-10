def get_summary_prompt():
    return """
        You are an expert document analyst. Your task is to read the provided text content of a single page from a document and generate a structured summary.

        Focus on identifying and extracting the following key information:

        1.  **Overall Summary:** A concise paragraph (3-5 sentences) summarizing the main topic and purpose of this specific page.
        2.  **Key Entities/Concepts (Nodes):** List the most important nouns, concepts, or defined terms on this page. For each, provide a brief, one-sentence description based *only* on the text provided.
            *   Example:
                *   `Reporting Week`: The period from Monday to Sunday used for data aggregation.
                *   `Reference Number`: A unique identifier assigned to each submission.
        3.  **Key Relationships/Interactions (Edges):** Identify how the entities or concepts relate to each other or to actions described on the page. Describe the relationship clearly.
            *   Example:
                *   `Reporting Week` -> `used for` -> `Data Aggregation`
                *   `Submission` -> `assigned` -> `Reference Number`
        4.  **Main Theme/Information Clusters:** Briefly describe the primary focus or type of information presented on this page (e.g., Definitions, Reporting Procedures, Data Fields, Compliance Requirements).

        **Input Page Text:**
        -----------------
        {text_contents}

        **Output Format:**

        Present the extracted information clearly under the headings specified above. Use bullet points for the lists of Entities/Concepts and Relationships/Interactions.

        **Example Output Structure:**

        Overall Summary:
        [Summary paragraph]

        Key Entities/Concepts (Nodes):
        *   [Entity 1]: [Description]
        *   [Entity 2]: [Description]
        ...

        Key Relationships/Interactions (Edges):
        *   [Source Entity] -> [Relationship Type] -> [Target Entity] ([Optional: Brief detail])
        *   [Source Entity] -> [Relationship Type] -> [Target Entity] ([Optional: Brief detail])
        ...

        Main Theme/Information Clusters:
        [Brief description of the theme(s)]

        **Constraints:**
        *   Base your summary *strictly* on the provided `text_contents`. Do not include external knowledge.
        *   Keep descriptions concise.
    """